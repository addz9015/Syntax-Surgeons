# VitalEdge+

VitalEdge+ is a clinical allergy intelligence project with three layers:

- **Data pipeline** — `vitaledge_prd_pipeline.py` calculates patient risk scores and writes analytics artifacts to `outputs/`.
- **FastAPI backend** — `fastapi_app.py` exposes KPIs, patient profiles, simulation results, and cluster data via REST.
- **Streamlit frontend** — `vitaledge_dashboard.py` presents a polished command-center dashboard.

## Project Structure

```
api/index.py          — Vercel serverless entry point (wraps fastapi_app.py)
fastapi_app.py        — FastAPI backend
vitaledge_core.py     — Shared data loading and risk logic
vitaledge_dashboard.py — Streamlit frontend
vitaledge_prd_pipeline.py — Analytics pipeline (run once to generate outputs/)
outputs/              — Generated CSV artifacts consumed at runtime
.streamlit/config.toml — Streamlit theme and server config
vercel.json           — Vercel routing config
```

---

## Deploy: API on Vercel + Dashboard on Streamlit Community Cloud

This is the recommended cloud deployment. The API hosts on Vercel (free tier), and the dashboard hosts on Streamlit Community Cloud (also free).

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial VitalEdge+ deploy"
git remote add origin https://github.com/YOUR_USERNAME/vitaledge-plus.git
git push -u origin main
```

Make sure `outputs/` and all CSV files are committed. The `.gitignore` is configured to allow them.

### Step 2 — Deploy the API to Vercel

1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **Add New Project** → Import the `vitaledge-plus` repository.
3. Leave the framework preset as **Other**.
4. Vercel will detect `vercel.json` automatically — no extra config needed.
5. Click **Deploy**.

After deploy your API will be live at:

```
https://your-project.vercel.app/health
https://your-project.vercel.app/docs
```

Add one environment variable in Vercel project settings → Environment Variables:

| Key | Value |
|-----|-------|
| `VITALEDGE_CORS_ORIGINS` | `https://your-dashboard.streamlit.app` (fill in after step 3) |

### Step 3 — Deploy the Dashboard to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
2. Click **New app**.
3. Set:
   - **Repository**: `YOUR_USERNAME/vitaledge-plus`
   - **Branch**: `main`
   - **Main file path**: `vitaledge_dashboard.py`
4. Expand **Advanced settings → Secrets** and add:

```toml
VITALEDGE_API_BASE_URL = "https://your-project.vercel.app"
```

5. Click **Deploy**.

Your dashboard will be live at `https://your-dashboard.streamlit.app`.

After both deploy, go back to Vercel and update `VITALEDGE_CORS_ORIGINS` to the Streamlit app URL.

---

## Run Locally

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate outputs (once)
python vitaledge_prd_pipeline.py

# 3. Start API (terminal 1)
python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8010

# 4A. Start Streamlit dashboard (terminal 2)
python -m streamlit run vitaledge_dashboard.py

# 4B. Or start the React frontend (terminal 2)
cd frontend
npm install
npm run dev:local

# 4C. Optional: analyze frontend bundle composition
npm run build:analyze
```

Streamlit: http://localhost:8501 | React: http://localhost:5174 | API docs: http://localhost:8010/docs

Set `VITE_API_BASE_URL` if the API is not running on `http://localhost:8010`.

`npm run build:analyze` writes:
- `frontend/dist/bundle-analysis.html` (treemap report)
- `frontend/dist/bundle-analysis.json` (raw data for CI diffing)

## Docker (local two-container stack)

```bash
docker compose up --build
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/kpis` | PRD KPI results |
| GET | `/model-metrics` | Model benchmark scores |
| GET | `/data-quality` | Data quality scorecard |
| GET | `/doctor-risk` | Doctor prescribing risk profiles |
| GET | `/clusters` | Patient cluster summary |
| GET | `/explanations` | SHAP explanation rows |
| GET | `/patients/{id}` | Full patient profile |
| GET | `/simulate?patient_id=&medicine_id=` | What-if risk simulation |
