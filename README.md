# VitalEdge+

VitalEdge+ is a clinical allergy intelligence project with three layers:

- **Data pipeline** — `vitaledge_prd_pipeline.py` calculates patient risk scores and writes analytics artifacts to `outputs/`.
- **FastAPI backend** — `fastapi_app.py` exposes KPIs, patient profiles, simulation results, and cluster data via REST.
- **React frontend** — `frontend/` is a Vite + React SPA with a 5-section sidebar dashboard and a custom allergy detection tool.

## Project Structure

```
api/index.py               — Vercel serverless entry point (wraps fastapi_app.py)
fastapi_app.py             — FastAPI backend
vitaledge_core.py          — Shared data loading and risk logic
vitaledge_prd_pipeline.py  — Analytics pipeline (run once to generate outputs/)
outputs/                   — Generated CSV artifacts consumed at runtime
frontend/                  — Vite + React dashboard SPA
vercel.json                — Vercel routing config
```

---

## Deploy: API on Vercel + Frontend on Vercel

Both the API and React frontend can be hosted on Vercel (free tier).

### Step 1 — Push to GitHub

```bash
git add .
git commit -m "Deploy VitalEdge+"
git push origin main
```

Make sure `outputs/` and all CSV files are committed. The `.gitignore` is configured to allow them.

### Step 2 — Deploy the API to Vercel

1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New Project** → import the repository.
3. Leave the framework preset as **Other**.
4. Vercel detects `vercel.json` automatically — no extra config needed.
5. Click **Deploy**.

After deploy your API will be live at:

```
https://your-project.vercel.app/health
https://your-project.vercel.app/docs
```

Add one environment variable in Vercel project settings → Environment Variables:

| Key | Value |
|-----|-------|
| `VITALEDGE_CORS_ORIGINS` | `https://your-frontend.vercel.app` (fill in after step 3) |

### Step 3 — Deploy the React Frontend to Vercel

1. Create a second Vercel project, pointing to the same repo.
2. Set **Root Directory** to `frontend`.
3. Vercel will auto-detect Vite — leave defaults.
4. Add one environment variable:

```
VITE_API_BASE_URL = https://your-project.vercel.app
```

5. Click **Deploy**.

Your dashboard will be live at `https://your-frontend.vercel.app`.

Go back to the API project and update `VITALEDGE_CORS_ORIGINS` to that URL.

---

## Run Locally

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate outputs (once)
python vitaledge_prd_pipeline.py

# 3. Start API (terminal 1)
python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8010

# 4. Start the React frontend (terminal 2)
cd frontend
npm install
npm run dev:local

# Optional: analyze frontend bundle composition
npm run build:analyze
```

React: http://localhost:5174 | API docs: http://localhost:8010/docs

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
