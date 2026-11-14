"""
AgriOptima - Prescriptive Fertilizer Optimization Engine
Wraps scikit-learn yield models with scipy.optimize.minimize (SLSQP).
"""

import os
import joblib
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, Any

_MODEL_CACHE = None

MAX_DELTA_N = 200.0
MAX_DELTA_P = 120.0
MAX_DELTA_K = 120.0

COST_PER_KG_N = 1.20
COST_PER_KG_P = 1.50
COST_PER_KG_K = 0.90

BLANKET_APPLICATION = {
    'delta_n': 120.0,
    'delta_p': 60.0,
    'delta_k': 40.0,
}


def get_model():
    """Loads the serialized ML pipeline with caching."""
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml', 'yield_model.joblib')
        if not os.path.exists(model_path):
            model_path = os.path.join('ml', 'yield_model.joblib')
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model file {model_path} missing. Train the model using `python ml/train_models.py`."
            )
        _MODEL_CACHE = joblib.load(model_path)
    return _MODEL_CACHE


def predict_single_yield(model, crop_type: str, n: float, p: float, k: float, ph: float, rain: float) -> float:
    """Invokes the ML pipeline for a single parameter vector."""
    row = pd.DataFrame([{
        'crop_type': crop_type,
        'nitrogen': float(n),
        'phosphorus': float(p),
        'potassium': float(k),
        'ph': float(ph),
        'rainfall': float(rain),
    }])
    pred = model.predict(row)[0]
    return float(np.maximum(0.0, pred))


def calculate_fertilizer_cost(delta_n: float = 0.0, delta_p: float = 0.0, delta_k: float = 0.0, **kwargs) -> float:
    """Calculates total input cost in USD/hectare."""
    dn = float(kwargs.get('dn', delta_n))
    dp = float(kwargs.get('dp', delta_p))
    dk = float(kwargs.get('dk', delta_k))
    return float(dn * COST_PER_KG_N + dp * COST_PER_KG_P + dk * COST_PER_KG_K)


def optimize_fertilizer(
    crop_type: str,
    current_n: float,
    current_p: float,
    current_k: float,
    ph: float,
    rainfall: float,
    target_yield: float
) -> Dict[str, Any]:
    """
    Computes minimum supplemental fertilizer (delta_N, delta_P, delta_K)
    required to meet or exceed target_yield using SLSQP.
    """
    model = get_model()

    # 1. Baseline yield calculation (zero additional fertilizer)
    baseline_yield = predict_single_yield(
        model, crop_type, current_n, current_p, current_k, ph, rainfall
    )

    # 2. Maximum achievable yield calculation under current environmental conditions
    max_attainable_yield = predict_single_yield(
        model,
        crop_type,
        current_n + MAX_DELTA_N,
        current_p + MAX_DELTA_P,
        current_k + MAX_DELTA_K,
        ph,
        rainfall
    )

    is_feasible = True
    infeasibility_note = None
    effective_target = float(target_yield)

    # Infeasibility check: Target yield exceeds biological ceiling under current pH/rainfall
    if target_yield > max_attainable_yield:
        is_feasible = False
        effective_target = max_attainable_yield
        infeasibility_note = (
            f"Target yield of {target_yield:.2f} t/ha exceeds the maximum biologically "
            f"attainable yield of {max_attainable_yield:.2f} t/ha under current soil pH ({ph}) "
            f"and rainfall ({rainfall} mm). Showing optimal fertilizer recipe for maximum attainable yield."
        )

    # 3. If baseline already exceeds or meets target yield, no fertilizer needed
    if baseline_yield >= effective_target and is_feasible:
        blanket_cost = calculate_fertilizer_cost(**BLANKET_APPLICATION)
        return {
            'is_feasible': True,
            'infeasibility_note': None,
            'baseline_yield': round(baseline_yield, 2),
            'target_yield': round(target_yield, 2),
            'predicted_yield': round(baseline_yield, 2),
            'delta_n': 0.0,
            'delta_p': 0.0,
            'delta_k': 0.0,
            'total_fertilizer_kg': 0.0,
            'optimized_cost': 0.0,
            'blanket_cost': round(blanket_cost, 2),
            'cost_savings': round(blanket_cost, 2),
            'percent_savings': 100.0,
            'max_attainable_yield': round(max_attainable_yield, 2)
        }

    # 4. Objective Function: Minimize economic fertilizer cost with Tikhonov regularization
    def objective(deltas):
        dn, dp, dk = deltas
        cost = (dn * COST_PER_KG_N) + (dp * COST_PER_KG_P) + (dk * COST_PER_KG_K)
        reg = 1e-4 * (dn**2 + dp**2 + dk**2)
        return cost + reg

    # 5. Non-linear Constraint: Predicted Yield >= Effective Target Yield
    def yield_constraint(deltas):
        dn, dp, dk = deltas
        pred = predict_single_yield(
            model,
            crop_type,
            current_n + dn,
            current_p + dp,
            current_k + dk,
            ph,
            rainfall
        )
        return pred - effective_target

    constraints = [{'type': 'ineq', 'fun': yield_constraint}]
    bounds = [
        (0.0, MAX_DELTA_N),
        (0.0, MAX_DELTA_P),
        (0.0, MAX_DELTA_K)
    ]

    x0 = np.array([25.0, 15.0, 15.0])

    res = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'ftol': 1e-5, 'maxiter': 150, 'disp': False}
    )

    opt_dn, opt_dp, opt_dk = np.maximum(0.0, res.x)

    # Post-optimization yield validation
    final_predicted_yield = predict_single_yield(
        model,
        crop_type,
        current_n + opt_dn,
        current_p + opt_dp,
        current_k + opt_dk,
        ph,
        rainfall
    )

    opt_cost = calculate_fertilizer_cost(opt_dn, opt_dp, opt_dk)
    blanket_cost = calculate_fertilizer_cost(**BLANKET_APPLICATION)
    savings = max(0.0, blanket_cost - opt_cost)
    pct_savings = round((savings / blanket_cost) * 100, 1) if blanket_cost > 0 else 0.0

    return {
        'is_feasible': is_feasible,
        'infeasibility_note': infeasibility_note,
        'baseline_yield': round(baseline_yield, 2),
        'target_yield': round(target_yield, 2),
        'predicted_yield': round(final_predicted_yield, 2),
        'delta_n': round(float(opt_dn), 1),
        'delta_p': round(float(opt_dp), 1),
        'delta_k': round(float(opt_dk), 1),
        'total_fertilizer_kg': round(float(opt_dn + opt_dp + opt_dk), 1),
        'optimized_cost': round(opt_cost, 2),
        'blanket_cost': round(blanket_cost, 2),
        'cost_savings': round(savings, 2),
        'percent_savings': pct_savings,
        'max_attainable_yield': round(max_attainable_yield, 2)
    }


def generate_response_curves(
    crop_type: str,
    current_n: float,
    current_p: float,
    current_k: float,
    ph: float,
    rainfall: float,
    opt_dn: float = 0.0,
    opt_dp: float = 0.0,
    opt_dk: float = 0.0,
    n_points: int = 15
) -> Dict[str, Any]:
    """
    Computes nutrient response curves for N, P, and K independently
    around the baseline and optimal points for frontend Chart.js visualizers.
    """
    model = get_model()

    n_vals = np.linspace(current_n, current_n + MAX_DELTA_N, n_points)
    n_yields = [
        round(predict_single_yield(model, crop_type, n, current_p, current_k, ph, rainfall), 2)
        for n in n_vals
    ]

    p_vals = np.linspace(current_p, current_p + MAX_DELTA_P, n_points)
    p_yields = [
        round(predict_single_yield(model, crop_type, current_n, p, current_k, ph, rainfall), 2)
        for p in p_vals
    ]

    k_vals = np.linspace(current_k, current_k + MAX_DELTA_K, n_points)
    k_yields = [
        round(predict_single_yield(model, crop_type, current_n, current_p, k, ph, rainfall), 2)
        for k in k_vals
    ]

    return {
        'nitrogen_curve': {
            'labels': [round(float(v), 1) for v in n_vals],
            'yields': n_yields,
            'current_x': round(current_n, 1),
            'optimal_x': round(current_n + opt_dn, 1),
        },
        'phosphorus_curve': {
            'labels': [round(float(v), 1) for v in p_vals],
            'yields': p_yields,
            'current_x': round(current_p, 1),
            'optimal_x': round(current_p + opt_dp, 1),
        },
        'potassium_curve': {
            'labels': [round(float(v), 1) for v in k_vals],
            'yields': k_yields,
            'current_x': round(current_k, 1),
            'optimal_x': round(current_k + opt_dk, 1),
        }
    }
