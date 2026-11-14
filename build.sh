#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Train models if artifacts are missing
if [ ! -f "ml/yield_model.joblib" ] || [ ! -f "ml/metrics.json" ]; then
    echo "ML model or metrics missing. Running training pipeline..."
    python ml/train_models.py
fi

python manage.py collectstatic --no-input
python manage.py migrate
