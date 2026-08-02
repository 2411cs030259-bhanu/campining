# Marketing Analytics Platform — Version 1.0 (Core MVP)

A full-stack SaaS application for uploading marketing campaign data,
calculating KPIs, visualizing performance, generating downloadable
reports, and answering basic marketing questions via a chatbot.

**Stack:** Python / Flask (REST API) · MySQL · Pandas · React.js

This is built as a foundation for a scalable product — every layer
(routes → services → models → database) is separated so future
versions can add features without rewriting the app.

---

## 1. Architecture

```
React Frontend  →  REST API (Flask)  →  Service Layer  →  MySQL + Analytics Engine
```

```
marketing_analytics_platform/
├── backend/
│   ├── app.py                 # App factory, blueprint registration, error handlers
│   ├── config.py               # All configuration, read from environment variables
│   ├── database.py             # MySQL connection pool
│   ├── schema.sql              # Database schema (run this first)
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/                 # HTTP layer only — parses requests, calls services
│   │   ├── auth_routes.py
│   │   ├── upload_routes.py
│   │   ├── report_routes.py
│   │   ├── chatbot_routes.py
│   │   └── analytics_routes.py
│   ├── services/                # Business logic, decoupled from Flask
│   │   ├── auth_service.py
│   │   ├── analytics_engine.py  # CSV cleaning, KPI math, insights (pandas)
│   │   ├── report_service.py    # Report file generation
│   │   └── chatbot_service.py   # Rule-based Q&A
│   ├── models/                  # Database access (SQL lives here only)
│   │   └── user_model.py
│   ├── utils/
│   │   ├── validators.py
│   │   ├── response_helpers.py
│   │   └── auth_decorators.py
│   ├── uploads/                 # Uploaded CSVs (gitignored)
│   └── reports/                 # Generated report CSVs (gitignored)
├── frontend/
│   ├── src/
│   │   ├── api/api.js            # Single place all backend calls go through
│   │   ├── context/AuthContext.js
│   │   ├── components/           # Sidebar, KpiCard, AppLayout, ProtectedRoute
│   │   └── pages/                # Login, Signup, Dashboard, Upload, Reports, Chatbot, Profile
│   └── package.json
├── sample_campaign_data.csv       # Sample file to test the upload flow
└── README.md
```

---

## 2. Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- MySQL 8.0+ running locally (or accessible remotely)

---

## 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your real MySQL credentials, secret key, etc.
**Never commit `.env`.**

Create the database and tables:

```bash
mysql -u root -p < schema.sql
```

Run the backend:

```bash
python app.py
```

The API will be available at `http://localhost:5000/api/v1`.
Check `GET /api/v1/health` to confirm the database connection is working.

---

## 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The app runs at `http://localhost:3000` and talks to the backend at
`http://localhost:5000/api/v1` (see `frontend/src/api/api.js` —
override with the `REACT_APP_API_URL` environment variable if needed).

---

## 5. Using the App

1. Sign up for an account.
2. Go to **Upload Data** and upload `sample_campaign_data.csv` (included
   at the project root) or your own CSV with these columns:
   `campaign, platform, impressions, clicks, ad_spend, conversions, revenue`
3. View KPIs, charts, and insights on the **Reports** page.
4. Click **Download Report (CSV)** to save the report.
5. Visit **Dashboard** to see your latest KPIs at a glance.
6. Ask the **Chatbot** things like "What is ROAS?" or "How do I generate reports?"

---

## 6. API Endpoints

| Method | Endpoint                     | Description                          | Auth required |
|--------|-------------------------------|---------------------------------------|----------------|
| POST   | `/api/v1/signup`              | Create an account                     | No             |
| POST   | `/api/v1/login`                | Log in                                | No             |
| POST   | `/api/v1/logout`               | Log out                               | Yes            |
| GET    | `/api/v1/me`                   | Get current session user              | Yes            |
| POST   | `/api/v1/upload`               | Upload & process a campaign CSV       | Yes            |
| GET    | `/api/v1/dashboard-summary`    | Latest KPI summary for dashboard      | Yes            |
| POST   | `/api/v1/download`             | Generate a downloadable report        | Yes            |
| GET    | `/api/v1/reports/<filename>`   | Download a specific report file       | Yes            |
| GET    | `/api/v1/reports`              | List report history                   | Yes            |
| POST   | `/api/v1/chatbot`              | Ask the marketing chatbot a question  | Yes            |
| GET    | `/api/v1/health`               | Health check (backend + DB status)    | No             |

All responses follow the shape:
```json
{ "success": true, "message": "...", "data": { ... } }
```

---

## 7. Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plaintext).
- All secrets and DB credentials come from environment variables — nothing is hardcoded.
- Sessions are HTTP-only cookies; CORS is restricted to `ALLOWED_ORIGINS`.
- Uploaded filenames are sanitized; only `.csv` is accepted; max upload size is enforced.
- Raw server errors are never shown to the user — see `app.py` error handlers.

---

## 8. Deployment (Render)

- **Backend:** deploy `backend/` as a Web Service. Set `Start Command` to
  `gunicorn app:app`. Add all `.env` variables in Render's environment settings.
- **MySQL:** provision a managed MySQL instance (Render, PlanetScale, or similar)
  and point `DB_HOST`/`DB_USER`/`DB_PASSWORD`/`DB_NAME` at it. Run `schema.sql` against it.
- **Frontend:** deploy `frontend/` as a Static Site with build command `npm run build`
  and publish directory `build`. Set `REACT_APP_API_URL` to your deployed backend URL.

---

## 9. Roadmap (Beyond Version 1.0)

This version was intentionally built so these can be layered on without rewrites:

| Version | Focus |
|---------|-------|
| 2.0 | Report storage & retrieval history |
| 3.0 | User history & personal dashboard |
| 4.0 | Advanced analytics |
| 5.0 | Dashboard customization |
| 6.0 | Security & account management (JWT, 2FA) |
| 7.0 | AI-powered marketing intelligence |
| 8.0 | Large-scale data processing |
| 9.0 | Team & business/org accounts (`organizations`, `permissions` tables) |
| 10.0 | Enterprise marketing intelligence platform |

The `datasets` and `reports` tables in `schema.sql` already exist so
Version 2.0 can add history/retrieval features purely at the API layer.
