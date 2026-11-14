import json
import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import OptimizationRecord
from .forms import SoilOptimizationForm
from .services.optimization import optimize_fertilizer, generate_response_curves
from .services.pdf_generator import generate_agronomist_pdf, calculate_commercial_bags
from .services.weather import fetch_weather_forecast, DEFAULT_PRESETS


def dashboard_view(request):
    latest_result = None
    response_curves = None
    commercial_bags = None

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
        'response_curves_json': json.dumps(response_curves) if response_curves else None,
        'weather_presets': DEFAULT_PRESETS,
    }
    return render(request, 'optimizer/dashboard.html', context)


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
    """API endpoint to fetch 14-day weather & leaching risk for given lat/lon."""
    try:
        lat = float(request.GET.get('lat', 31.1471))
        lon = float(request.GET.get('lon', 75.3412))
    except (ValueError, TypeError):
        lat, lon = 31.1471, 75.3412

    weather_data = fetch_weather_forecast(lat, lon)
    return JsonResponse(weather_data)


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
