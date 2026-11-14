import json
import os
from django.shortcuts import render
from django.contrib import messages
from .models import OptimizationRecord
from .forms import SoilOptimizationForm
from .services.optimization import optimize_fertilizer, generate_response_curves

def dashboard_view(request):
    latest_result = None
    response_curves = None

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
        'response_curves_json': json.dumps(response_curves) if response_curves else None,
    }
    return render(request, 'optimizer/dashboard.html', context)


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
