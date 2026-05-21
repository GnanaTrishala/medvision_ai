# MedVision AI

**MedVision AI** is a full-stack AI dermatology analysis platform for dermoscopic skin lesion classification. Clinicians and researchers can upload lesion images, receive multi-class predictions with confidence scores, inspect **Grad-CAM** explainability heatmaps, read AI-generated clinical interpretations, and download PDF reports — all through a modern web dashboard.

> **Disclaimer:** For research and clinical decision support only. Not FDA-cleared as a medical device. Not a substitute for professional diagnosis.

---

## Overview

MedVision AI combines a **PyTorch EfficientNet-B0** classifier trained on the **HAM10000** dataset with a production-style **FastAPI** backend and **Next.js** frontend. The system supports **7-class** skin lesion classification, JWT-secured user accounts, prediction history, dashboard analytics, and explainable AI visualizations.

| Metric | Value |
|--------|--------|
| **Model** | EfficientNet-B0 (ImageNet pretrained, fine-tuned head) |
| **Dataset** | HAM10000 (10,015 dermoscopic images) |
| **Classes** | 7 lesion types |
| **Validation accuracy** | **89.82%** |

---

## Features

- **7-class lesion classification** — akiec, bcc, bkl, df, mel, nv, vasc
- **Confidence scores** — top predictions with per-class probabilities
- **Grad-CAM explainability** — heatmaps highlighting regions that influenced the model
- **AI medical interpretation** — structured clinical narrative per prediction
- **PDF reports** — downloadable summaries with findings and metadata
- **JWT authentication** — signup, login, protected routes
- **Dashboard** — analytics cards, diagnosis distribution, confidence trends, history
- **Dark / light mode** — responsive SaaS-style UI with animations

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, Framer Motion, Recharts, next-themes |
| **Backend** | FastAPI, Python, JWT (python-jose), SQLAlchemy, Pydantic, ReportLab |
| **ML** | PyTorch, torchvision (EfficientNet-B0), Grad-CAM |
| **Database** | SQLite (local) · PostgreSQL (production via `DATABASE_URL`) |
| **Deployment** | Vercel (frontend) · Render / Railway (backend) |

---

## Project structure

```
medvision_ai/
├── backend/                    # FastAPI API + ML inference
│   ├── app/
│   │   ├── api/routes/         # auth, predictions, reports, files
│   │   ├── core/               # config, security, database
│   │   ├── ml/                 # EfficientNet, Grad-CAM, preprocessing
│   │   ├── models/             # SQLAlchemy ORM
│   │   ├── schemas/            # Pydantic DTOs
│   │   └── services/           # predictions, explanations, PDF
│   ├── train.py                # Train EfficientNet-B0 on HAM10000
│   └── models/                 # best_model.pth (after training)
├── medvision-ui/               # Next.js frontend
├── data/                       # HAM10000 raw + prepared splits
├── scripts/
│   └── prepare_local_data.py   # Build train/val ImageFolder
├── assets/                     # Screenshots & media for docs
└── README.md
```

---

## Dataset (HAM10000)

MedVision uses the [HAM10000](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000) dataset — 10,015 dermatoscopic images with 7 diagnostic labels.

### Class labels

| Code | Lesion type |
|------|-------------|
| `akiec` | Actinic keratosis / intraepithelial carcinoma |
| `bcc` | Basal cell carcinoma |
| `bkl` | Benign keratosis |
| `df` | Dermatofibroma |
| `mel` | Melanoma |
| `nv` | Melanocytic nevus |
| `vasc` | Vascular lesion |

### Expected raw layout

Place Kaggle files under `data/` or `data/ham10000/`:

```
data/
├── HAM10000_metadata.csv
├── HAM10000_images_part_1/
└── HAM10000_images_part_2/
```

### Prepare train / validation splits

From the project root:

```bash
python scripts/prepare_local_data.py --source ./data --output ./data/ham10000
```

This creates an ImageFolder layout:

```
data/ham10000/
├── train/
│   ├── akiec/
│   ├── bcc/
│   └── ...
└── val/
    ├── akiec/
    └── ...
```

See [data/README.md](data/README.md) for more detail.

---

## Training

Train EfficientNet-B0 from the `backend/` directory:

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python train.py --data ../data/ham10000 --epochs 15 --batch-size 32
```

The best checkpoint is saved to:

```
backend/models/best_model.pth
```

**Reported validation accuracy:** 89.82% (HAM10000 holdout split).

---

## Setup & run locally

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+

### 1. Backend

```bash
cd backend
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
```

Edit `.env` — set a strong `SECRET_KEY`:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./data/medvision.db
CORS_ORIGINS=http://localhost:3000
MODEL_PATH=./models/best_model.pth
```

Start the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API: https://medvision-ai-iae1.onrender.com  
- Interactive docs: https://medvision-ai-iae1.onrender.com/docs  

### 2. Frontend

```bash
cd medvision-ui
copy .env.example .env.local   # Windows
# cp .env.example .env.local   # macOS / Linux
```

Set in `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://medvision-ai-iae1.onrender.com
```

```bash
npm install
npm run dev
```

Open http://localhost:3000 → sign up → **Analyze Lesion**.

---

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/signup` | Create account |
| `POST` | `/api/v1/auth/login` | JWT token (form: `username`, `password`) |
| `GET` | `/api/v1/auth/me` | Current user |
| `POST` | `/api/v1/predictions/analyze` | Upload image (multipart `file`) |
| `GET` | `/api/v1/predictions/history` | Prediction history |
| `GET` | `/api/v1/predictions/dashboard` | Dashboard analytics |
| `GET` | `/api/v1/reports/{id}/pdf` | Download PDF report |

---

## Screenshots

Add project screenshots to the [`assets/`](assets/) folder, then reference them here:

| View | File |
|------|------|
| Landing page | `assets/landing.png` |
| Dashboard | `assets/dashboard.png` |
| Lesion analysis + Grad-CAM | `assets/analyze.png` |
| PDF report sample | `assets/report.png` |

**Landing page**

![MedVision AI Landing](assets/landing.png)

**Dashboard**

![Dashboard](assets/dashboard.png)

**Analysis & Grad-CAM**

![Analyze](assets/analyze.png)

> Placeholder paths above — replace images in `assets/` when available.

---

## Deployment

| Component | Platform | Notes |
|-----------|----------|--------|
| Frontend | [Vercel](https://vercel.com) | Root: `medvision-ui`, set `NEXT_PUBLIC_API_URL` |
| Backend | [Render](https://render.com) / [Railway](https://railway.app) | Root: `backend`, see `render.yaml` |
| Database | PostgreSQL | Set `DATABASE_URL` in production |

Production backend start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Future improvements

- [ ] DICOM upload support for clinical imaging workflows
- [ ] Multi-GPU / distributed training
- [ ] LLM-enhanced report narratives (optional layer on top of template interpretations)
- [ ] Patient case management and batch inference
- [ ] Model versioning and A/B evaluation dashboard
- [ ] FHIR / EHR integration hooks
- [ ] External validation on additional dermatology datasets
- [ ] Mobile-responsive PWA and offline queueing

---

## License & ethics

- Respect the [HAM10000](https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000) dataset license and citation requirements.
- Do not deploy without appropriate clinical governance, bias assessment, and regulatory review for your jurisdiction.

---

## Acknowledgments

- **HAM10000** — Tschandl, P.; Rosendahl, K.; Kittler, H. (2018)
- **EfficientNet** — Tan & Le, Google Research
- **Grad-CAM** — Selvaraju et al.

---

<p align="center">
  <strong>MedVision AI</strong> — Explainable dermatology intelligence for the modern clinic.
</p>
