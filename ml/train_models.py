"""
AgriOptima - Machine Learning Training Pipeline
Trains and evaluates Ridge Regression and Support Vector Regression (SVR - RBF kernel),
computes 5-fold cross-validation benchmarks, serializes the best model to ml/yield_model.joblib,
and outputs evaluation metrics to ml/metrics.json.
"""

import os
import sys
import json
from datetime import datetime
import numpy as np
import pandas as pd
import joblib

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.metrics import r2_score, root_mean_squared_error, mean_absolute_error

from ml.generate_data import main as generate_synthetic_data


def train_and_evaluate():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'soil_yields.csv')
    ml_dir = os.path.join(base_dir, 'ml')
    os.makedirs(ml_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print("[INFO] Dataset not found. Generating synthetic agronomic data...")
        generate_synthetic_data()

    print(f"[INFO] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)

    feature_cols = ['crop_type', 'nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall']
    target_col = 'yield_tons_per_hectare'

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    numeric_features = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall']
    categorical_features = ['crop_type']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
        ]
    )

    candidate_pipelines = {
        'Polynomial Ridge Regression': Pipeline([
            ('preprocessor', preprocessor),
            ('poly', PolynomialFeatures(degree=2, include_bias=False)),
            ('regressor', Ridge(alpha=10.0))
        ]),
        'Support Vector Regression (RBF)': Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', SVR(kernel='rbf', C=30.0, epsilon=0.1, gamma='scale'))
        ])
    }

    metrics_output = {
        'trained_at': datetime.utcnow().isoformat() + 'Z',
        'dataset_size': len(df),
        'features': feature_cols,
        'models_evaluated': {},
        'selected_model': None
    }

    best_score = -np.inf
    best_model_name = None
    best_pipeline = None

    print("[INFO] Starting model training & cross-validation benchmarks...")

    for name, pipeline in candidate_pipelines.items():
        print(f"\n--- Evaluating: {name} ---")
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='r2')
        cv_mean = float(np.mean(cv_scores))
        cv_std = float(np.std(cv_scores))

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        test_r2 = float(r2_score(y_test, y_pred))
        test_rmse = float(root_mean_squared_error(y_test, y_pred))
        test_mae = float(mean_absolute_error(y_test, y_pred))

        metrics_output['models_evaluated'][name] = {
            'test_r2': round(test_r2, 4),
            'test_rmse': round(test_rmse, 4),
            'test_mae': round(test_mae, 4),
            'cv_mean_r2': round(cv_mean, 4),
            'cv_std_r2': round(cv_std, 4)
        }

        print(f"  Test R²:        {test_r2:.4f}")
        print(f"  Test RMSE:      {test_rmse:.4f} t/ha")
        print(f"  Test MAE:       {test_mae:.4f} t/ha")
        print(f"  5-Fold Mean R²: {cv_mean:.4f} (+/- {cv_std:.4f})")

        if cv_mean > best_score:
            best_score = cv_mean
            best_model_name = name
            best_pipeline = pipeline

    metrics_output['selected_model'] = best_model_name
    print(f"\n[OK] Best model selected: {best_model_name} (CV Mean R²: {best_score:.4f})")

    # Fit best model on the complete dataset for maximum production fidelity
    print(f"[INFO] Fitting {best_model_name} on entire dataset ({len(df)} samples)...")
    best_pipeline.fit(X, y)

    model_save_path = os.path.join(ml_dir, 'yield_model.joblib')
    joblib.dump(best_pipeline, model_save_path)
    print(f"[OK] Serialized production model to: {model_save_path}")

    metrics_save_path = os.path.join(ml_dir, 'metrics.json')
    with open(metrics_save_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_output, f, indent=2)
    print(f"[OK] Evaluation metrics saved to: {metrics_save_path}")


if __name__ == '__main__':
    train_and_evaluate()
