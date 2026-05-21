# MedVision AI

Production-style **AI healthcare platform** for chest X-ray analysis: disease prediction, confidence scores, **Grad-CAM** explainability, AI-generated clinical interpretation, and **PDF reports** — with JWT auth, dashboard analytics, and a modern SaaS UI.

> **Research & clinical decision support only** — not FDA-cleared as a medical device.

---

## Architecture

```
medvision_ai/
├── backend/                 # FastAPI + PyTorch + SQLite/PostgreSQL
│   ├── app/
│   │   ├── api/routes/      # auth, predictions, reports, files
│   │   ├── core/            # config, security, database
│   │   ├── ml/              # EfficientNet, Grad-CAM, preprocessing
│   │   ├── models/          # SQLAlchemy ORM
│   │   ├── schemas/         # Pydantic DTOs
│   │   └── services/        # business logic, PDF, explanations
│   ├── train.py             # Train EfficientNet-B0
│   └── models/              # best_model.pth (after training)
├── medvision-ui/            # Next.js 15 frontend
├── data/                    # Chest X-Ray dataset (ImageFolder)
└── scripts/prepare_local_data.py
```

| Layer | Stack |
|-------|--------|
| Frontend | Next.js, TypeScript, Tailwind, Framer Motion, Recharts, next-themes |
| Backend | FastAPI, JWT, SQLAlchemy, ReportLab |
| ML | PyTorch, EfficientNet-B0, Grad-CAM |
| Database | SQLite (default) → PostgreSQL via `DATABASE_URL` |

---

## Features

- **Auth**: JWT signup/login, protected dashboard
- **AI**: Upload X-ray → pneumonia/normal prediction + probabilities
- **Explainability**: Grad-CAM heatmaps
- **Interpretation**: Template-based clinical narrative (extensible to LLM)
- **Reports**: Download PDF per analysis
- **Dashboard**: Stats, pie chart, confidence trend, history

---

## Quick start (local)

### 1. Dataset

Download [Chest X-Ray Pneumonia](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia), then:

```bash
python scripts/prepare_local_data.py --source path/to/chest_xray --output data
```

### 2. Train model

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python train.py --data ../data --epochs 15
```

Weights save to `backend/models/best_model.pth`.

### 3. Backend API

```bash
cd backend
copy .env.example .env          # set SECRET_KEY
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 4. Frontend

```bash
cd medvision-ui
copy .env.example .env.local    # NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm install
npm run dev
```

Open http://localhost:3000 → Sign up → **Analyze X-Ray**.

---

## API overview

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/v1/auth/signup` | — |
| POST | `/api/v1/auth/login` | form: username=email, password |
| GET | `/api/v1/auth/me` | Bearer |
| POST | `/api/v1/predictions/analyze` | Bearer + multipart `file` |
| GET | `/api/v1/predictions/history` | Bearer |
| GET | `/api/v1/predictions/dashboard` | Bearer |
| GET | `/api/v1/reports/{id}/pdf` | Bearer |

---

## Deployment

### Frontend → Vercel

1. Import `medvision-ui` as root directory (or monorepo subpath).
2. Set `NEXT_PUBLIC_API_URL` to your production API (e.g. `https://medvision-api.onrender.com/api/v1`).
3. Deploy.

### Backend → Render / Railway

1. Root directory: `backend`
2. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Env vars: `SECRET_KEY`, `DATABASE_URL` (Postgres), `CORS_ORIGINS`, `MODEL_PATH`
4. Upload `best_model.pth` to persistent disk or bake into image.

See `render.yaml` for a Render starter blueprint.

### PostgreSQL

```env
DATABASE_URL=postgresql://user:pass@host:5432/medvision
```

---

## Resume / portfolio highlights

- Full-stack separation with REST + JWT
- Explainable AI (Grad-CAM) — not black-box only
- PDF clinical reports + audit history in DB
- SaaS UI: dark mode, charts, drag-and-drop, animations
- Production patterns: env config, modular services, typed schemas

---

## Disclaimer

Not for standalone diagnosis. Always validate with qualified clinicians and institutional protocols.
