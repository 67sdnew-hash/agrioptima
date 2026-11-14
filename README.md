# AgriOptima — Crop Yield Prediction & Prescriptive Fertilizer Optimizer

AgriOptima is a production web application engineered for prescriptive precision agriculture. Given current soil macronutrient levels (Nitrogen, Phosphorus, Potassium), soil pH, rainfall, and a farmer's target yield, the application computes the mathematically minimal supplemental fertilizer ($\Delta N, \Delta P, \Delta K$ in kg/ha) needed to achieve that target while maximizing economic cost savings and preventing over-fertilization and environmental degradation.

---

## Key Features

1. **Synthetic Agronomic Data Generator & Non-Linear Biophysical Dynamics:**
   - Multi-crop simulation (Rice, Wheat, Maize, Cotton) modeling Mitscherlich-Baule diminishing nutrient returns.
   - Gaussian pH efficiency responses and quadratic rainfall drought/waterlogging thresholds.
2. **Machine Learning Predictive Pipelines:**
   - Preprocessing via `ColumnTransformer` (`StandardScaler` + `OneHotEncoder`).
   - Evaluated models: **Polynomial Ridge Regression** vs. **Support Vector Regression (SVR - RBF kernel)**.
   - Comprehensive cross-validated metrics (R², RMSE, MAE) logged to `ml/metrics.json` and serialized using `joblib`.
3. **Prescriptive Fertilizer Optimizer (`scipy.optimize.minimize`):**
   - Sequential Least Squares Programming (SLSQP) constrained optimization minimizing total fertilizer expenditure.
   - Tikhonov regularization $\lambda (\Delta N^2 + \Delta P^2 + \Delta K^2)$ to maintain balanced agronomic stoichiometry.
   - Biophysical feasibility detection alerting farmers if their target yield exceeds environmental carrying capacity.
4. **Interactive Dashboard & Diagnostic Views:**
   - Built with Django 5.x, Tailwind CSS, and Chart.js.
   - Dynamic 15-point nutrient response curves for N, P, and K with optimal dosage callouts.
   - Historical optimization log persisted in PostgreSQL / SQLite.
   - Dedicated `/methodology/` benchmark page showing model evaluation and formulation details.

---

## Tech Stack

- **Backend:** Django 5.1, Gunicorn, WhiteNoise, dj-database-url, psycopg
- **Machine Learning & Math:** scikit-learn, SciPy (`scipy.optimize.minimize`), NumPy, Pandas, Joblib
- **Frontend:** Django Templates, Tailwind CSS CDN, Chart.js CDN
- **Database:** PostgreSQL (production on Render) / SQLite (local development)
- **Deployment:** Render Web Service + Managed PostgreSQL

---

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd agrioptima
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate data and train the ML model:**
   ```bash
   python ml/train_models.py
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py makemigrations optimizer
   python manage.py migrate
   ```

6. **Run unit tests:**
   ```bash
   python manage.py test optimizer
   ```

7. **Start local development server:**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000` in your browser.

---

## Deployment to Render

The repository includes a `render.yaml` blueprint for one-click deployment:

1. Push this project to a new repository on your GitHub account.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** > **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically provision:
   - Managed PostgreSQL Database (`agrioptima-db`)
   - Web Service (`agrioptima`) running Gunicorn and WhiteNoise
5. The build script (`build.sh`) automatically runs migrations, static asset collection, and trains the model if artifacts are missing.
