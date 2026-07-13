# Business OS — MVP Development Plan

## Source of Truth
- Technical specification: `C:\Users\BAZA\Desktop\Идеи для  продуктов\business_os_technical_specification.md`
- Workspace: `C:\KonCoOS\business-os`

## Architecture
Multi-service project:
- `backend/` — FastAPI + SQLAlchemy + Alembic + asyncpg
- `bot/` — aiogram 3.x + Redis FSM
- `document_engine/` — Celery + docxtpl + LibreOffice PDF conversion
- `mini-app/` — React 18 + TypeScript + Tailwind + Recharts
- `nginx/` — reverse proxy + static files
- `docker-compose.yml` — dev orchestration

## Phase 1 — Parallel Foundation (Week 1)
All services built in parallel with defined API contracts.

### Module A: Backend Core + Database
**Agent:** `backend_dev`
**Scope:**
- Full SQLAlchemy models (users, clients, payments, expenses, documents, tax_calculations, bank_connections, subscriptions, user_settings, audit_log)
- Alembic migrations (baseline + triggers)
- Pydantic schemas for all entities
- FastAPI main app with routers structure
- Base endpoints: health, auth (telegram initData → JWT), CRUD for clients, payments, expenses, documents
- Tax calculation service (УСН 6%, УСН 15%, НПД)
- Webhook endpoints for banks
- API client models matching TZ Appendix Б

**Output:** `backend/` directory with runnable app.

### Module B: Telegram Bot
**Agent:** `bot_dev`
**Scope:**
- aiogram 3.x structure as per TZ section 5.3
- Commands: /start, /help, /pulse, /clients, /documents, /expenses, /taxes, /settings, /support
- FSM for: document creation (act/invoice), expense input, client addition, settings
- ReplyKeyboard main menu + inline keyboards (pagination, document actions, client selection)
- Middleware: auth (JWT), logging, rate limiting
- Text message handlers (NLP-lite patterns from TZ Appendix В)
- Message templates (Pulse, notification, morning briefing)
- API client service to backend

**Output:** `bot/` directory with runnable bot.

### Module C: Document Engine
**Agent:** `doc_engine_dev`
**Scope:**
- Celery worker setup
- Document generator classes: invoice, act, waybill, gph_contract, monthly_report
- docxtpl templates for each document type (with Jinja2 variables from TZ 8.4.1)
- Table rendering for items (loop)
- LibreOffice headless conversion wrapper (docx → PDF)
- num2words integration (amount to Russian words)
- S3 upload utility (Selectel compatible)
- Celery task: generate_document

**Output:** `document_engine/` directory with templates and generators.

### Module D: Mini App Frontend
**Agent:** `frontend_dev`
**Scope:**
- React 18 + TypeScript + Vite setup
- Tailwind CSS with Telegram theme support (dark/light from WebApp SDK)
- Telegram WebApp SDK integration (useTelegram hook, useAuth hook)
- Axios API client with JWT interceptor
- Pages: Dashboard (Pulse), Clients, ClientDetail, Documents, DocumentDetail, Payments, Expenses, Analytics, Taxes, Settings, BankConnection
- Components: Layout, Header, Navigation, StatCard, ClientCard, DocumentCard, ChartRevenue, ChartExpenses, ChartClients, LoadingSpinner, EmptyState
- Recharts integration (line, bar, pie charts)
- Lazy loading + React Router 6
- Responsive layout for mobile

**Output:** `mini-app/` directory with buildable app.

### Module E: Bank Integration + DevOps
**Agent:** `devops_bank_dev`
**Scope:**
- Bank Adapter Pattern (abstract class + TinkoffAdapter + SberAdapter)
- Tinkoff OAuth flow (auth URL, code exchange, refresh)
- Transaction mapping (TZ 7.2.3 table)
- Webhook signature verification (Tinkoff)
- Token encryption (AES-256-GCM)
- docker-compose.yml with all services (postgres, redis, backend, bot, celery, document_engine, nginx)
- nginx.conf (reverse proxy, SSL, static files for mini-app)
- .env.example with all variables from TZ Appendix А
- Dockerfile for each service (backend, bot, document_engine)
- GitHub Actions CI/CD pipeline (test, build, deploy)

**Output:** `docker-compose.yml`, `nginx/`, `Dockerfile`s, `.env.example`, `.github/workflows/ci.yml`

## API Contracts (all modules must respect these)

### Authentication
```
POST /api/v1/auth/telegram
Body: { init_data: string }
Response: { access_token: string, user: User }
```

### Pulse
```
GET /api/v1/analytics/pulse
Response: PulseData (TZ Appendix Б.1)
```

### Clients
```
GET /api/v1/clients?page={n}&search={q}
POST /api/v1/clients
GET /api/v1/clients/{id}
PUT /api/v1/clients/{id}
DELETE /api/v1/clients/{id}
```

### Documents
```
GET /api/v1/documents?type={type}&page={n}
POST /api/v1/documents
GET /api/v1/documents/{id}
```

### Payments
```
POST /api/v1/payments
GET /api/v1/payments
POST /api/v1/payments/bank-webhook/{bank_code}
```

### Bank Connections
```
POST /api/v1/banks/connect
GET /api/v1/banks/callback
```

## Dependencies
- Backend has no code dependencies on other modules (it defines the API)
- Bot depends on Backend API (HTTP client)
- Document Engine depends on Backend API (notify callback) and Redis
- Mini App depends on Backend API
- Bank Integration lives inside Backend service
- All services depend on docker-compose for orchestration

## Success Criteria
- `docker-compose up` starts all services without errors
- Bot responds to /start
- Backend /health returns OK
- Document engine can generate a PDF from template
- Mini App builds and Dashboard page exists
- Tinkoff OAuth flow is implemented (at least the adapter structure)
