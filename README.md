# 🚀 SmartCash AI

**Intelligent Cash Flow Risk Monitoring and Decision Support System for Small Businesses**

> A production-ready, AI-powered financial intelligence platform built for grocery shops, restaurants, salons, startups, and every small business in between.

---

## ✨ Features

| Module | Capability |
|---|---|
| 🔐 Authentication | JWT, refresh tokens, email verification, RBAC (Admin / Owner / Employee) |
| 🏢 Business Profile | GST, industry, currency, opening balance, financial year |
| 💰 Income Management | CRUD, categories, payment methods, daily/weekly/monthly charts |
| 💸 Expense Management | CRUD, 15 categories, receipt uploads, anomaly flags |
| 👥 Customer Management | Dues tracking, risk rating, payment history, reminders |
| 🔄 Cash Flow Engine | Burn rate, runway, net flow, reserve calculation |
| 🧠 AI Cash Flow Forecast | Prophet + linear fallback, 7/15/30/90-day horizons |
| 🚨 Anomaly Detection | Isolation Forest, duplicate detection, fraud alerts |
| ❤️ Health Score | 0-100 weighted composite score, Green/Yellow/Red |
| 💡 Recommendations | Prioritized AI advice sorted by impact |
| ⚠️ Shortage Prediction | Rule-based + XGBoost risk probability |
| 📊 Reports | PDF, Excel, CSV export |
| 🔔 Alerts | Dashboard, email, push notification (FCM) |
| 🌙 Dark/Light Mode | System-aware theming |
| 📱 Responsive | Mobile-first layout |

---

## 🏗️ Architecture

```
smartcash-ai/
├── backend/                  # Python FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/ # Auth, Business, Income, Expense, Customer, Dashboard, Predictions, Reports
│   │   ├── core/             # Config, Security, Dependencies
│   │   ├── db/               # Async SQLAlchemy session
│   │   ├── models/           # 11 SQLAlchemy models
│   │   ├── schemas/          # Pydantic v2 schemas
│   │   ├── services/         # Business logic layer
│   │   └── ai/models/        # ML models (Forecaster, AnomalyDetector, HealthScorer, Recommender)
│   ├── alembic/              # Database migrations
│   ├── tests/                # Unit + Integration tests
│   └── scripts/              # Seed data
│
├── frontend/                 # React 18 + TypeScript + Vite
│   └── src/
│       ├── components/       # Reusable UI (ShadCN-based), Layout
│       ├── pages/            # 14 full pages
│       ├── store/            # Zustand (auth, theme)
│       ├── lib/              # Axios client, utilities
│       └── types/            # TypeScript interfaces
│
├── data/samples/             # CSV datasets for testing
├── .github/workflows/        # CI/CD pipeline
└── docker-compose.yml        # Full stack deployment
```

---

## 🛠️ Tech Stack

**Frontend:** React 18 · TypeScript · Vite · Tailwind CSS · ShadCN UI · Chart.js · React Router · React Hook Form · Zod · Zustand · Axios

**Backend:** Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Alembic · PostgreSQL · Redis

**AI/ML:** Scikit-Learn · XGBoost · Prophet · Isolation Forest · Pandas · NumPy

**Infrastructure:** Docker · Docker Compose · GitHub Actions · Nginx · AWS S3 · Firebase FCM

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/smartcash-ai.git
cd smartcash-ai
cp .env.example .env
# Edit .env with your values
```

### 2. Start with Docker

```bash
docker compose up -d
```

Access:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000

### 3. Seed demo data

```bash
docker compose exec backend python -m scripts.seed_data
```

### 4. Login with demo account

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@smartcash.ai | Admin@123 |
| Owner | demo@smartcash.ai | Demo@123 |

---

## 🔧 Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Run Tests

```bash
# Backend unit tests
cd backend
pytest tests/unit -v

# Backend with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📊 Database Schema

| Table | Description |
|-------|-------------|
| users | Authentication, roles, FCM tokens |
| businesses | Business profile, GST, currency, opening balance |
| incomes | All money in: sales, payments, bank transfers |
| expenses | All money out: rent, salary, inventory, etc. |
| customers | Customer details, outstanding, risk rating |
| invoices | Invoice management with status tracking |
| predictions | AI forecast results |
| risk_scores | Business health score history |
| recommendations | AI recommendations |
| notifications | System alerts |
| audit_logs | Immutable action log |

---

## 🔑 API Endpoints

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
GET    /api/v1/auth/me

GET    /api/v1/business
POST   /api/v1/business
PUT    /api/v1/business/{id}

GET    /api/v1/dashboard/{business_id}

GET    /api/v1/income/{business_id}
POST   /api/v1/income/{business_id}
PUT    /api/v1/income/{business_id}/{income_id}
DELETE /api/v1/income/{business_id}/{income_id}

GET    /api/v1/expenses/{business_id}
POST   /api/v1/expenses/{business_id}

GET    /api/v1/customers/{business_id}
POST   /api/v1/customers/{business_id}

POST   /api/v1/predictions/{business_id}/forecast?horizon=30
POST   /api/v1/predictions/{business_id}/health-score
POST   /api/v1/predictions/{business_id}/anomalies
POST   /api/v1/predictions/{business_id}/shortage
POST   /api/v1/predictions/{business_id}/recommendations

GET    /api/v1/reports/{business_id}/export?format=pdf&report_type=summary
```

Full Swagger docs at: `http://localhost:8000/docs`

---

## 🔒 Security

- JWT access tokens (30 min) + refresh tokens (7 days)
- Bcrypt password hashing (12 rounds)
- Role-based access control (Admin / Business Owner / Employee)
- CORS protection with configurable origins
- Rate limiting via middleware
- SQL injection protection via SQLAlchemy ORM
- Secure headers via Nginx
- Audit logging for all critical actions
- Input validation via Pydantic v2

---

## 🤖 AI Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| CashFlowForecaster | Prophet + Linear fallback | 7/15/30/90 day income prediction |
| AnomalyDetector | Isolation Forest | Expense anomaly & duplicate detection |
| BusinessHealthScorer | Weighted formula | 0-100 business health score |
| RecommendationEngine | Rule-based + threshold | Prioritized financial recommendations |
| CashShortagePredictor | Rule-based scoring | Cash shortage probability |

---

## 📦 Deployment

### Production (Docker Compose)

```bash
# Set production environment variables
export SECRET_KEY="your-super-secret-key-min-32-chars"
export DB_PASSWORD="secure-db-password"
export REDIS_PASSWORD="secure-redis-password"

docker compose -f docker-compose.yml up -d --build
```

### GitHub Actions CI/CD

The pipeline automatically:
1. Runs backend unit tests
2. Runs frontend type check and build
3. Builds and pushes Docker images to GHCR
4. Deploys to production via SSH

Configure secrets in GitHub: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`

---

## 📝 License

MIT License — Free to use for hackathons, MVPs, and production.

---

## 🏆 Built for

- Final Year Engineering Projects
- Startup MVPs
- Hackathons
- Small Business Owners across India

---

*SmartCash AI — Empowering Small Businesses with Financial Intelligence*
