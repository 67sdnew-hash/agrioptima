import json
import os
import random
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import OptimizationRecord, CommunityPost, CommunityReply, CommunityChatMessage, FarmerProfile
from .forms import SoilOptimizationForm
from .services.optimization import optimize_fertilizer, generate_response_curves
from .services.pdf_generator import generate_agronomist_pdf, calculate_commercial_bags
from .services.weather import fetch_weather_forecast, DEFAULT_PRESETS
from .services.split_schedule import calculate_split_schedule, generate_ics_calendar, get_google_calendar_url
from .services.ai_agronomist import answer_agronomic_query
from .services.notification import dispatch_email_otp, dispatch_sms_otp


def dashboard_view(request):
    latest_result = None
    response_curves = None
    commercial_bags = None
    split_schedule = None
    ai_context = {}

    if request.method == 'POST':
        form = SoilOptimizationForm(request.POST)
        if form.is_valid():
            crop_type = form.cleaned_data['crop_type']
            current_n = form.cleaned_data['current_nitrogen']
            current_p = form.cleaned_data['current_phosphorus']
            current_k = form.cleaned_data['current_potassium']
            ph = form.cleaned_data['soil_ph']
            rainfall = form.cleaned_data['rainfall']
            target_yield = form.cleaned_data['target_yield']

            try:
                opt_res = optimize_fertilizer(
                    crop_type=crop_type,
                    current_n=current_n,
                    current_p=current_p,
                    current_k=current_k,
                    ph=ph,
                    rainfall=rainfall,
                    target_yield=target_yield
                )

                record = OptimizationRecord.objects.create(
                    crop_type=crop_type,
                    current_nitrogen=current_n,
                    current_phosphorus=current_p,
                    current_potassium=current_k,
                    soil_ph=ph,
                    rainfall=rainfall,
                    target_yield=target_yield,
                    baseline_yield=opt_res['baseline_yield'],
                    predicted_yield=opt_res['predicted_yield'],
                    delta_nitrogen=opt_res['delta_n'],
                    delta_phosphorus=opt_res['delta_p'],
                    delta_potassium=opt_res['delta_k'],
                    total_fertilizer_kg=opt_res['total_fertilizer_kg'],
                    optimized_cost=opt_res['optimized_cost'],
                    blanket_cost=opt_res['blanket_cost'],
                    cost_savings=opt_res['cost_savings'],
                    percent_savings=opt_res['percent_savings'],
                    is_feasible=opt_res['is_feasible'],
                    infeasibility_note=opt_res['infeasibility_note'],
                )

                response_curves = generate_response_curves(
                    crop_type=crop_type,
                    current_n=current_n,
                    current_p=current_p,
                    current_k=current_k,
                    ph=ph,
                    rainfall=rainfall,
                    opt_dn=opt_res['delta_n'],
                    opt_dp=opt_res['delta_p'],
                    opt_dk=opt_res['delta_k'],
                )

                commercial_bags = calculate_commercial_bags(
                    float(opt_res['delta_n']),
                    float(opt_res['delta_p']),
                    float(opt_res['delta_k'])
                )

                # Compute 4R Split Application Schedule
                sowing_date = datetime.now()
                split_schedule = calculate_split_schedule(
                    crop_type=crop_type,
                    sowing_date=sowing_date,
                    urea_bags=commercial_bags['urea_bags'],
                    dap_bags=commercial_bags['dap_bags'],
                    mop_bags=commercial_bags['mop_bags'],
                    delta_n_kg=opt_res['delta_n'],
                    delta_p_kg=opt_res['delta_p'],
                    delta_k_kg=opt_res['delta_k']
                )

                # Attach Google Calendar links to each stage
                for stage in split_schedule:
                    desc = f"{stage['title']} for {crop_type}: {stage['application_method']} ({stage['rationale']})"
                    stage['google_cal_url'] = get_google_calendar_url(
                        f"Fertilizer Stage {stage['stage_number']} ({crop_type})",
                        stage['iso_date'],
                        desc
                    )

                ai_context = {
                    'crop_type': crop_type,
                    'current_nitrogen': current_n,
                    'current_phosphorus': current_p,
                    'current_potassium': current_k,
                    'soil_ph': ph,
                    'rainfall': rainfall,
                    'target_yield': target_yield,
                    'delta_nitrogen': opt_res['delta_n'],
                    'delta_phosphorus': opt_res['delta_p'],
                    'delta_potassium': opt_res['delta_k'],
                    'urea_bags': commercial_bags['urea_bags'],
                    'dap_bags': commercial_bags['dap_bags'],
                    'mop_bags': commercial_bags['mop_bags'],
                    'savings': opt_res['cost_savings']
                }

                latest_result = record
                messages.success(request, "Prescriptive fertilizer optimization calculated successfully!")

            except Exception as e:
                messages.error(request, f"Optimization Error: {str(e)}")
    else:
        initial_data = {
            'crop_type': 'Wheat',
            'current_nitrogen': 45.0,
            'current_phosphorus': 22.0,
            'current_potassium': 35.0,
            'soil_ph': 6.5,
            'rainfall': 720.0,
            'target_yield': 6.0,
        }
        form = SoilOptimizationForm(initial=initial_data)

    context = {
        'form': form,
        'latest_result': latest_result,
        'commercial_bags': commercial_bags,
        'split_schedule': split_schedule,
        'response_curves_json': json.dumps(response_curves) if response_curves else None,
        'weather_presets': DEFAULT_PRESETS,
        'ai_context_json': json.dumps(ai_context) if ai_context else "{}",
        'today_iso': datetime.now().strftime('%Y-%m-%d'),
    }
    return render(request, 'optimizer/dashboard.html', context)


def export_ics_calendar_view(request, record_id: int):
    """Generates an RFC 5545 .ics iCalendar file for the 4R split-application schedule."""
    record = get_object_or_404(OptimizationRecord, id=record_id)
    comm = calculate_commercial_bags(record.delta_nitrogen, record.delta_phosphorus, record.delta_potassium)
    
    date_str = request.GET.get('sowing_date')
    try:
        sowing_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
    except ValueError:
        sowing_date = datetime.now()

    ics_content = generate_ics_calendar(
        crop_type=record.crop_type,
        sowing_date=sowing_date,
        urea_bags=comm['urea_bags'],
        dap_bags=comm['dap_bags'],
        mop_bags=comm['mop_bags'],
        delta_n_kg=record.delta_nitrogen,
        delta_p_kg=record.delta_phosphorus,
        delta_k_kg=record.delta_potassium
    )

    response = HttpResponse(ics_content, content_type='text/calendar; charset=utf-8')
    filename = f"AgriOptima_Schedule_{record.crop_type}_AGRI{record.id}.ics"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@csrf_exempt
@require_POST
def agronomist_chat_api_view(request):
    """API endpoint providing real-time AI Agronomist Copilot advisory."""
    try:
        payload = json.loads(request.body.decode('utf-8'))
        message = payload.get('message', '').strip()
        context = payload.get('context', {})

        if not message:
            return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

        result = answer_agronomic_query(message, context)
        return JsonResponse({'success': True, 'data': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def export_pdf_report_view(request, record_id: int):
    """Generates and streams a certified Agronomist Field Report PDF."""
    record = get_object_or_404(OptimizationRecord, id=record_id)
    pdf_buffer = generate_agronomist_pdf(record)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"AgriOptima_Report_AGRI-{record.id:05d}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_GET
def weather_proxy_view(request):
    """
    API endpoint to fetch weather & leaching risk.
    Supports:
    1. Explicit lat & lon (?lat=...&lon=...)
    2. City / town query (?city=Kolkata)
    3. Auto IP detection (?auto=true)
    """
    from .services.weather import geolocate_ip, geocode_city_name

    city_query = request.GET.get('city', '').strip()
    auto_detect = request.GET.get('auto', '').lower() in ('true', '1', 'yes')

    location_name = None

    if city_query:
        geo = geocode_city_name(city_query)
        if geo['success']:
            lat = geo['latitude']
            lon = geo['longitude']
            location_name = geo['location_name']
        else:
            return JsonResponse({'success': False, 'error': f"Location '{city_query}' not found."})
    elif auto_detect:
        # Extract client IP from proxy headers (Render X-Forwarded-For)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR')

        geo = geolocate_ip(client_ip)
        lat = geo['latitude']
        lon = geo['longitude']
        location_name = geo['location_name']
    else:
        try:
            lat = float(request.GET.get('lat', 31.1471))
            lon = float(request.GET.get('lon', 75.3412))
            location_name = request.GET.get('name')
        except (ValueError, TypeError):
            lat, lon = 31.1471, 75.3412

    weather_data = fetch_weather_forecast(lat, lon, location_name=location_name)
    return JsonResponse(weather_data)


@require_GET
def search_locations_api_view(request):
    """API endpoint providing real-time worldwide location search autocomplete."""
    from .services.weather import search_global_locations
    query = request.GET.get('q', '').strip()
    results = search_global_locations(query, count=8)
    return JsonResponse({'results': results})


def multi_zone_view(request):
    """Interactive multi-zone farm mapper for precision variable-rate application."""
    context = {
        'weather_presets': DEFAULT_PRESETS,
    }
    return render(request, 'optimizer/multi_zone.html', context)


@csrf_exempt
@require_POST
def optimize_zone_api_view(request):
    """
    API endpoint accepting multi-zone farm specifications and returning
    individual prescriptions, whole-farm aggregate totals, and VRA GeoJSON payload.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        zones = payload.get('zones', [])

        if not zones:
            return JsonResponse({'error': 'No farm zones provided'}, status=400)

        zone_results = []
        total_farm_area = 0.0
        total_farm_cost = 0.0
        total_blanket_cost = 0.0
        total_urea_kg = 0.0
        total_dap_kg = 0.0
        total_mop_kg = 0.0

        geojson_features = []

        for idx, z in enumerate(zones):
            zone_name = z.get('name', f"Zone {idx + 1}")
            area_ha = float(z.get('area_ha', 10.0))
            crop = z.get('crop_type', 'Wheat')
            cn = float(z.get('current_nitrogen', 45.0))
            cp = float(z.get('current_phosphorus', 20.0))
            ck = float(z.get('current_potassium', 30.0))
            ph = float(z.get('soil_ph', 6.5))
            rain = float(z.get('rainfall', 750.0))
            target_y = float(z.get('target_yield', 6.0))
            lat = float(z.get('lat', 31.1471 + idx * 0.005))
            lon = float(z.get('lon', 75.3412 + idx * 0.005))

            opt = optimize_fertilizer(
                crop_type=crop,
                current_n=cn,
                current_p=cp,
                current_k=ck,
                ph=ph,
                rainfall=rain,
                target_yield=target_y
            )

            comm = calculate_commercial_bags(opt['delta_n'], opt['delta_p'], opt['delta_k'])

            zone_total_cost = round(opt['optimized_cost'] * area_ha, 2)
            zone_blanket_cost = round(opt['blanket_cost'] * area_ha, 2)
            zone_savings = round(zone_blanket_cost - zone_total_cost, 2)

            total_farm_area += area_ha
            total_farm_cost += zone_total_cost
            total_blanket_cost += zone_blanket_cost
            total_urea_kg += comm['urea_kg'] * area_ha
            total_dap_kg += comm['dap_kg'] * area_ha
            total_mop_kg += comm['mop_kg'] * area_ha

            zone_data = {
                'id': idx + 1,
                'name': zone_name,
                'area_ha': area_ha,
                'crop_type': crop,
                'target_yield': target_y,
                'predicted_yield': opt['predicted_yield'],
                'delta_n': opt['delta_n'],
                'delta_p': opt['delta_p'],
                'delta_k': opt['delta_k'],
                'urea_bags_per_ha': comm['urea_bags'],
                'dap_bags_per_ha': comm['dap_bags'],
                'mop_bags_per_ha': comm['mop_bags'],
                'total_urea_bags': round((comm['urea_kg'] * area_ha) / 50.0, 1),
                'total_dap_bags': round((comm['dap_kg'] * area_ha) / 50.0, 1),
                'total_mop_bags': round((comm['mop_kg'] * area_ha) / 50.0, 1),
                'optimized_cost': zone_total_cost,
                'blanket_cost': zone_blanket_cost,
                'cost_savings': zone_savings,
                'is_feasible': opt['is_feasible']
            }
            zone_results.append(zone_data)

            # Build GeoJSON feature for tractor guidance
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat]
                },
                'properties': {
                    'zone_name': zone_name,
                    'area_hectares': area_ha,
                    'crop': crop,
                    'target_yield_t_ha': target_y,
                    'prescribed_delta_n_kg_ha': opt['delta_n'],
                    'prescribed_delta_p_kg_ha': opt['delta_p'],
                    'prescribed_delta_k_kg_ha': opt['delta_k'],
                    'urea_50kg_bags_total': round((comm['urea_kg'] * area_ha) / 50.0, 1),
                    'dap_50kg_bags_total': round((comm['dap_kg'] * area_ha) / 50.0, 1),
                    'mop_50kg_bags_total': round((comm['mop_kg'] * area_ha) / 50.0, 1)
                }
            }
            geojson_features.append(feature)

        total_farm_savings = round(total_blanket_cost - total_farm_cost, 2)
        pct_savings = round((total_farm_savings / total_blanket_cost) * 100, 1) if total_blanket_cost > 0 else 0.0

        geojson_doc = {
            'type': 'FeatureCollection',
            'properties': {
                'generator': 'AgriOptima Precision Agriculture Multi-Zone Engine',
                'total_farm_area_ha': round(total_farm_area, 1),
                'total_cost_usd': round(total_farm_cost, 2),
                'total_savings_usd': round(total_farm_savings, 2)
            },
            'features': geojson_features
        }

        return JsonResponse({
            'success': True,
            'summary': {
                'total_farm_area_ha': round(total_farm_area, 1),
                'total_farm_cost_usd': round(total_farm_cost, 2),
                'total_blanket_cost_usd': round(total_blanket_cost, 2),
                'total_savings_usd': round(total_farm_savings, 2),
                'percent_savings': pct_savings,
                'total_urea_bags': round(total_urea_kg / 50.0, 1),
                'total_dap_bags': round(total_dap_kg / 50.0, 1),
                'total_mop_bags': round(total_mop_kg / 50.0, 1),
            },
            'zones': zone_results,
            'geojson': geojson_doc
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def history_view(request):
    records = OptimizationRecord.objects.all()[:50]
    total_savings = sum(r.cost_savings for r in records)
    total_optimized = len(records)

    context = {
        'records': records,
        'total_savings': round(total_savings, 2),
        'total_optimized': total_optimized,
    }
    return render(request, 'optimizer/history.html', context)


def research_view(request):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_path = os.path.join(base_dir, 'ml', 'metrics.json')
    if not os.path.exists(metrics_path):
        metrics_path = os.path.join('ml', 'metrics.json')

    metrics_data = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)

    context = {
        'metrics': metrics_data,
    }
    return render(request, 'optimizer/research.html', context)


def community_hub_view(request):
    """Virtual Farmer Community: Localized & Global discussions, farmer map, and live radio chat."""
    from .services.community_seed import seed_community_if_empty
    seed_community_if_empty()

    category = request.GET.get('category', 'all')
    crop = request.GET.get('crop', '').strip()
    search = request.GET.get('q', '').strip()

    posts_qs = CommunityPost.objects.all().prefetch_related('replies')

    if category and category != 'all':
        posts_qs = posts_qs.filter(category=category)

    if crop:
        posts_qs = posts_qs.filter(crop_type__iexact=crop)

    if search:
        posts_qs = posts_qs.filter(title__icontains=search) | posts_qs.filter(content__icontains=search) | posts_qs.filter(author_location__icontains=search)

    posts = list(posts_qs[:50])
    recent_chats = list(CommunityChatMessage.objects.order_by('-created_at')[:30])
    recent_chats.reverse()

    # Prepare map pins for active farmers/posts
    map_pins = []
    for p in posts:
        if p.latitude and p.longitude:
            map_pins.append({
                'id': p.id,
                'author': p.author_name,
                'location': p.author_location,
                'crop': p.crop_type,
                'category': p.get_category_display(),
                'title': p.title,
                'lat': p.latitude,
                'lon': p.longitude,
                'replies_count': p.replies.count()
            })

    context = {
        'posts': posts,
        'recent_chats': recent_chats,
        'selected_category': category,
        'selected_crop': crop,
        'search_query': search,
        'map_pins_json': json.dumps(map_pins),
        'total_farmers': CommunityPost.objects.values('author_name').distinct().count() + 42,
        'categories': CommunityPost.CATEGORY_CHOICES,
    }
    return render(request, 'optimizer/community.html', context)


@csrf_exempt
@require_POST
def community_create_post_api(request):
    """API endpoint to create a new discussion post in the Farmer Community."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        author_name = data.get('author_name', '').strip() or "Neighboring Farmer"
        author_location = data.get('author_location', '').strip() or "Local Agro Belt"
        crop_type = data.get('crop_type', 'Wheat').strip()
        category = data.get('category', 'fertilizer').strip()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        soil_metrics_json = data.get('soil_metrics', '').strip()

        lat = data.get('latitude')
        lon = data.get('longitude')
        try:
            lat = float(lat) if lat is not None and lat != '' else None
            lon = float(lon) if lon is not None and lon != '' else None
        except ValueError:
            lat, lon = None, None

        if not title or not content:
            return JsonResponse({'error': 'Title and content cannot be empty.'}, status=400)

        post = CommunityPost.objects.create(
            author_name=author_name,
            author_location=author_location,
            latitude=lat,
            longitude=lon,
            crop_type=crop_type,
            category=category,
            title=title,
            content=content,
            soil_metrics_json=soil_metrics_json,
            upvotes=1
        )

        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'author': post.author_name,
                'location': post.author_location,
                'crop': post.crop_type,
                'category': post.category,
                'title': post.title,
                'content': post.content,
                'soil_metrics': post.soil_metrics_json,
                'created_at': post.created_at.strftime('%b %d, %Y • %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def community_reply_api(request, post_id: int):
    """API endpoint to add a reply to an existing discussion thread."""
    try:
        post = get_object_or_404(CommunityPost, id=post_id)
        data = json.loads(request.body.decode('utf-8'))
        author_name = data.get('author_name', '').strip() or "Neighboring Farmer"
        author_location = data.get('author_location', '').strip() or "Local Agricultural Area"
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'error': 'Reply content cannot be empty.'}, status=400)

        reply = CommunityReply.objects.create(
            post=post,
            author_name=author_name,
            author_location=author_location,
            content=content
        )

        return JsonResponse({
            'success': True,
            'reply': {
                'id': reply.id,
                'author': reply.author_name,
                'location': reply.author_location,
                'content': reply.content,
                'created_at': reply.created_at.strftime('%b %d, %Y • %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def community_upvote_api(request, post_id: int):
    """API endpoint to upvote / endorse a helpful agronomic post."""
    try:
        post = get_object_or_404(CommunityPost, id=post_id)
        post.upvotes += 1
        post.save(update_fields=['upvotes'])
        return JsonResponse({'success': True, 'upvotes': post.upvotes})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def community_chat_api(request):
    """API endpoint for the real-time Live Farmer Radio chat channel."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            author_name = data.get('author_name', '').strip() or "Farmer"
            author_location = data.get('author_location', '').strip() or "Local Field"
            channel = data.get('channel', 'nearby').strip()
            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

            msg = CommunityChatMessage.objects.create(
                author_name=author_name,
                author_location=author_location,
                channel=channel,
                message=message
            )

            return JsonResponse({
                'success': True,
                'message': {
                    'id': msg.id,
                    'author': msg.author_name,
                    'location': msg.author_location,
                    'channel': msg.channel,
                    'text': msg.message,
                    'time': msg.created_at.strftime('%H:%M')
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        channel = request.GET.get('channel', '')
        qs = CommunityChatMessage.objects.all()
        if channel and channel != 'all':
            qs = qs.filter(channel=channel)

        msgs = list(qs.order_by('-created_at')[:40])
        msgs.reverse()

        data = [{
            'id': m.id,
            'author': m.author_name,
            'location': m.author_location,
            'channel': m.channel,
            'text': m.message,
            'time': m.created_at.strftime('%H:%M')
        } for m in msgs]

        return JsonResponse({'success': True, 'messages': data})


def login_view(request):
    """Farmer Sign In supporting either Phone Number OR Email Address + Password."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()

        if not identifier or not password:
            messages.error(request, "Please enter both your Phone / Email and Password.")
            return render(request, 'optimizer/login.html', {'identifier': identifier})

        matched_user = None

        if '@' in identifier:
            matched_user = User.objects.filter(email__iexact=identifier).first()
        else:
            clean_phone = ''.join(c for c in identifier if c.isdigit() or c == '+')
            profile = FarmerProfile.objects.filter(phone_number__icontains=clean_phone).select_related('user').first()
            if profile:
                matched_user = profile.user

        if not matched_user:
            matched_user = User.objects.filter(username__iexact=identifier).first()

        if matched_user:
            user = authenticate(request, username=matched_user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, Farmer {user.first_name or user.username}!")
                next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
                return redirect(next_url)
            else:
                messages.error(request, "Incorrect password. Please verify and try again.")
        else:
            messages.error(request, "No registered farmer found with that Phone Number or Email.")

    return render(request, 'optimizer/login.html')


def register_view(request):
    """Farmer Registration with Phone OTP verification or Email verification."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'optimizer/register.html')


@csrf_exempt
@require_POST
def send_registration_otp_api(request):
    """Generates and delivers a 6-digit OTP code to the assigned Phone Number or Email."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        method = data.get('method', 'phone').strip().lower()
        full_name = data.get('full_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        email = data.get('email', '').strip()
        farm_location = data.get('farm_location', '').strip() or "Local Agro Basin"
        primary_crop = data.get('primary_crop', 'Wheat').strip()
        password = data.get('password', '').strip()

        if not full_name:
            return JsonResponse({'success': False, 'error': 'Full Name is required.'}, status=400)
        if len(password) < 6:
            return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters.'}, status=400)

        target = ""
        if method == 'phone':
            if not phone_number:
                return JsonResponse({'success': False, 'error': 'Phone number is required for phone registration.'}, status=400)
            if FarmerProfile.objects.filter(phone_number=phone_number).exists():
                return JsonResponse({'success': False, 'error': 'This phone number is already registered. Please sign in.'}, status=400)
            target = phone_number
        else:
            if not email or '@' not in email:
                return JsonResponse({'success': False, 'error': 'Valid email address is required.'}, status=400)
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'success': False, 'error': 'This email is already registered. Please sign in.'}, status=400)
            target = email

        otp_code = f"{random.randint(100000, 999999)}"

        request.session['farmer_reg_otp'] = otp_code
        request.session['farmer_reg_payload'] = {
            'method': method,
            'full_name': full_name,
            'phone_number': phone_number,
            'email': email,
            'farm_location': farm_location,
            'primary_crop': primary_crop,
            'password': password
        }

        # Dispatch OTP to respective channel
        if method == 'email':
            dispatch_res = dispatch_email_otp(email, otp_code, full_name)
        else:
            dispatch_res = dispatch_sms_otp(phone_number, otp_code, full_name)

        return JsonResponse({
            'success': True,
            'otp': otp_code,
            'target': target,
            'channel': method,
            'message': dispatch_res.get('message', f"Verification OTP delivered to {target}")
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def verify_registration_otp_api(request):
    """Verifies the 6-digit OTP and completes Farmer Registration."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        entered_otp = data.get('otp', '').strip()
        session_otp = request.session.get('farmer_reg_otp')
        payload = request.session.get('farmer_reg_payload')

        if not session_otp or not payload:
            return JsonResponse({'success': False, 'error': 'OTP expired or session not found. Please request a new OTP.'}, status=400)

        if entered_otp != session_otp:
            return JsonResponse({'success': False, 'error': 'Invalid OTP code. Please enter the correct 6-digit verification code.'}, status=400)

        base_username = payload['phone_number'] if payload['method'] == 'phone' else payload['email'].split('@')[0]
        base_username = ''.join(c for c in base_username if c.isalnum() or c in '_-')[:20]
        if not base_username:
            base_username = "farmer"

        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{suffix}"
            suffix += 1

        user = User.objects.create_user(
            username=username,
            email=payload.get('email', ''),
            password=payload['password'],
            first_name=payload['full_name']
        )

        FarmerProfile.objects.create(
            user=user,
            phone_number=payload.get('phone_number') or None,
            farm_location=payload.get('farm_location', 'Local Farm'),
            primary_crop=payload.get('primary_crop', 'Wheat'),
            verification_method=payload.get('method', 'phone'),
            is_verified=True
        )

        request.session.pop('farmer_reg_otp', None)
        request.session.pop('farmer_reg_payload', None)

        login(request, user)

        return JsonResponse({
            'success': True,
            'message': f"Account verified successfully! Welcome to AgriOptima, {user.first_name}!",
            'redirect_url': '/'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def logout_view(request):
    """Signs out the currently logged-in farmer."""
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('dashboard')


