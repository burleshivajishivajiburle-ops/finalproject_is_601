# Calculations App
Full-stack FastAPI project that lets authenticated users perform, track, and review calculator operations through both a REST API and server-rendered pages. The stack combines FastAPI, SQLAlchemy, PostgreSQL (Docker), Redis-ready auth helpers, Tailwind-inspired templates, and Playwright end-to-end coverage. This finalproject continues directly from the Module 14 calculator project, carrying forward all prior features and expanding them with the enhancements.

## Feature Highlights
- **Authentication & Authorization**: JWT-based login/logout, access/refresh tokens, protected dashboard routes.
- **Profile & Password Management**: Update username, email, first/last name, and change passwords (hashing + `password_updated_at` auditing).
- **Calculation Engine (9 total types)**: Addition, subtraction, multiplication, division plus five advanced operations—exponentiation, modulus, minimum, maximum, and average.
- **CRUD UI & API**: Create/read/update/delete calculations with timestamps, result history, and ownership enforcement.
- **Testing Coverage**: 60+ unit tests, integration suites, and Playwright E2E flows validating login → dashboard → profile/password change.
- **Containerized Delivery**: Docker Compose setup (FastAPI, PostgreSQL, pgAdmin) with GitHub Actions CI + Docker Hub publishing.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic, PostgreSQL
- **Frontend**: Jinja2 templates, vanilla JS, Tailwind-inspired CSS
- **Auth/Security**: JWT, Passlib (bcrypt), dependency-based guards
- **Tooling**: Pytest, Playwright, Docker, GitHub Actions

## Repository Layout
```
app/                # FastAPI modules (models, schemas, routes, auth)
templates/          # Jinja2 HTML templates
static/             # CSS / JS assets
tests/              # unit, integration, and Playwright E2E suites
alembic/            # Database migration environment + versions
docker-compose.yml  # FastAPI + Postgres + pgAdmin stack
.github/workflows/  # CI pipeline (tests + Docker build/push)
```

## Prerequisites
- Python **3.12+** (for local development/testing)
- Docker Desktop with Docker Compose v2
- Node.js **not required** (Playwright ships via PyPI)

## Local Development (SQLite quick start)
```bash
python -m venv .venv
source .venv/bin/activate           # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Optional: set environment overrides
cp .env.example .env                # edit DATABASE_URL, JWT secrets, etc.

# Launch FastAPI with SQLite (default DATABASE_URL)
uvicorn app.main:app --reload
```

...
## Docker Compose Workflow (PostgreSQL)

```bash
docker compose up --build -d        # start FastAPI, Postgres, pgAdmin
docker compose restart              # restart services
docker compose down                 # stop + remove containers
```

- App UI: <http://localhost:8080/>
- Health: <http://localhost:8080/health>
- Swagger UI: <http://localhost:8080/docs>
- pgAdmin: <http://localhost:5055/> (admin@example.com / admin)

## Database Migrations (Alembic)
Alembic is configured via `alembic.ini` to use the same `DATABASE_URL` as the app.

**Apply latest migrations:**

```bash
# Local (SQLite or custom DATABASE_URL)
alembic upgrade head

# Docker Postgres
docker compose exec web alembic upgrade head
```

**Create a new migration after model changes:**
```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Run `alembic history` to inspect migration order.

## Testing
```bash
# Activate virtual environment first
pytest                                # unit + integration
pytest tests/unit -v                  # unit only
pytest tests/integration -v           # DB-focused tests
pytest tests/e2e -v --base-url=http://localhost:8080
```

Playwright needs browsers installed once per machine:

```bash
python -m playwright install
```

Coverage reports land in `htmlcov/index.html` when running with `pytest --cov`.

## Continuous Integration & Deployment
`.github/workflows/test.yml` performs the following on push/PR:

1. Install dependencies
2. Run unit + integration + E2E suites
3. Build the Docker image
4. Push the tagged image to Docker Hub **only if** tests pass

## Docker Hub Publishing
Update `<<docker-hub-username>>` with your namespace.

```bash
docker login
docker build -t <<docker-hub-username>>/assignmentlmlm:latest .
docker push <<docker-hub-username>>/assignmentlmlm:latest
```

The README should include the final Docker Hub link, e.g.
```
https://hub.docker.com/r/<your-username>/assignmentlmlm
```

## API Surface (summary)
| Method | Endpoint                      | Description |
|--------|-------------------------------|-------------|
| POST   | `/auth/register`              | Register a new user |
| POST   | `/auth/login`                 | Login with JSON credentials |
| POST   | `/auth/token`                 | OAuth2 form login |
| GET    | `/users/me`                   | Current profile |
| PUT    | `/users/me`                   | Update username/email/names |
| POST   | `/users/me/change-password`   | Change password |
| GET    | `/calculations`               | List user calculations |
| POST   | `/calculations`               | Create calculation (supports 9 types) |
| GET    | `/calculations/{id}`          | Fetch a calculation |
| PUT    | `/calculations/{id}`          | Update calculation |
| DELETE | `/calculations/{id}`          | Remove calculation |
| GET    | `/health`                     | Service health check |

## Troubleshooting
- **Missing DB columns after code changes**: run `alembic upgrade head` in the environment hitting the database (Docker or local).
- **Playwright failures**: ensure the server is reachable at the `--base-url` used during tests and rerun `python -m playwright install` after Playwright upgrades.
- **Login/profile JSON errors**: check FastAPI logs (e.g., `docker compose logs web -f`) to confirm migrations were applied.

## License / Credits
Course assignment project (“assignmentlmlm”) combining FastAPI + Docker best practices. Update this section if you need a specific license notice.
