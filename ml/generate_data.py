"""
AgriOptima - Synthetic Agronomic Data Generator
Generates realistic multi-crop yield responses based on:
1. Mitscherlich-Baule diminishing nutrient returns.
2. Soil pH Gaussian efficiency response.
3. Quadratic rainfall response curve (drought and waterlogging limits).
4. Fertilizer toxicity penalties under severe over-application.
"""

import os
import numpy as np
import pandas as pd

np.random.seed(42)

CROP_SPECS = {
    'Rice': {
        'y_max': 9.5,
        'n_range': (20, 220),
        'p_range': (10, 90),
        'k_range': (20, 160),
        'c_n': 0.015,
        'c_p': 0.035,
        'c_k': 0.020,
        'n_toxic': 240,
        'opt_ph': 6.0,
        'ph_width': 1.1,
        'opt_rain': 1100,
        'rain_range': (600, 1800),
    },
    'Wheat': {
        'y_max': 7.2,
        'n_range': (15, 200),
        'p_range': (10, 80),
        'k_range': (15, 130),
        'c_n': 0.018,
        'c_p': 0.040,
        'c_k': 0.022,
        'n_toxic': 220,
        'opt_ph': 6.6,
        'ph_width': 0.9,
        'opt_rain': 650,
        'rain_range': (350, 1100),
    },
    'Maize': {
        'y_max': 11.5,
        'n_range': (30, 260),
        'p_range': (15, 110),
        'k_range': (30, 180),
        'c_n': 0.014,
        'c_p': 0.030,
        'c_k': 0.018,
        'n_toxic': 280,
        'opt_ph': 6.4,
        'ph_width': 1.0,
        'opt_rain': 800,
        'rain_range': (450, 1300),
    },
    'Cotton': {
        'y_max': 4.8,
        'n_range': (20, 180),
        'p_range': (10, 75),
        'k_range': (20, 140),
        'c_n': 0.016,
        'c_p': 0.038,
        'c_k': 0.025,
        'n_toxic': 210,
        'opt_ph': 6.8,
        'ph_width': 1.2,
        'opt_rain': 750,
        'rain_range': (400, 1200),
    }
}

def generate_crop_data(crop_name: str, n_samples: int = 700) -> pd.DataFrame:
    spec = CROP_SPECS[crop_name]

    nitrogen = np.random.uniform(spec['n_range'][0], spec['n_range'][1] * 1.15, n_samples)
    phosphorus = np.random.uniform(spec['p_range'][0], spec['p_range'][1] * 1.15, n_samples)
    potassium = np.random.uniform(spec['k_range'][0], spec['k_range'][1] * 1.15, n_samples)
    ph = np.random.normal(loc=spec['opt_ph'], scale=0.6, size=n_samples)
    ph = np.clip(ph, 4.5, 8.5)
    rainfall = np.random.uniform(spec['rain_range'][0], spec['rain_range'][1], n_samples)

    factor_n = 1.0 - 10 ** (-spec['c_n'] * nitrogen)
    n_excess = np.maximum(0, nitrogen - spec['n_toxic'])
    factor_n = np.maximum(0.1, factor_n - 0.0015 * (n_excess ** 1.3))

    factor_p = 1.0 - 10 ** (-spec['c_p'] * phosphorus)
    factor_k = 1.0 - 10 ** (-spec['c_k'] * potassium)

    nutrient_multiplier = factor_n * factor_p * factor_k

    factor_ph = np.exp(-0.5 * ((ph - spec['opt_ph']) / spec['ph_width']) ** 2)

    rain_deviation = (rainfall - spec['opt_rain']) / spec['opt_rain']
    factor_rain = 1.0 - 0.75 * (rain_deviation ** 2)
    factor_rain = np.clip(factor_rain, 0.25, 1.0)

    stochastic_noise = np.random.normal(loc=0.0, scale=0.22, size=n_samples)
    yield_tons = (
        spec['y_max'] * nutrient_multiplier * factor_ph * factor_rain
        + stochastic_noise
    )

    yield_tons = np.maximum(0.4, np.round(yield_tons, 3))

    df = pd.DataFrame({
        'crop_type': crop_name,
        'nitrogen': np.round(nitrogen, 1),
        'phosphorus': np.round(phosphorus, 1),
        'potassium': np.round(potassium, 1),
        'ph': np.round(ph, 2),
        'rainfall': np.round(rainfall, 1),
        'yield_tons_per_hectare': yield_tons
    })

    return df

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    frames = [generate_crop_data(crop, n_samples=700) for crop in CROP_SPECS.keys()]
    dataset = pd.concat(frames, ignore_index=True)

    dataset = dataset.sample(frac=1.0, random_state=42).reset_index(drop=True)

    output_path = os.path.join(data_dir, 'soil_yields.csv')
    dataset.to_csv(output_path, index=False)

    print(f"[OK] Generated {len(dataset):,} agronomic records across {len(CROP_SPECS)} crops.")
    print(f"[OK] Saved dataset to: {output_path}")

if __name__ == '__main__':
    main()
