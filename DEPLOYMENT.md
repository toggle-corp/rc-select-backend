# Backend Deployment

This document covers backend-specific deployment steps.
For the full deployment guide (SSH setup, frontend build, Caddy, environment variables), see the [https://dev.azure.com/IFRC/RC_Select/_git/rc-select-frontend/](../DEPLOYMENT.md).

---

## Docker Compose Setup

The backend uses two compose files:

| File | Purpose |
|------|---------|
| `docker-compose.yaml` | Base config — used in development and as the base for production |
| `docker-compose-prod.override.yaml` | Production overrides — disables mailpit, enables Caddy, sets `APP_ENVIRONMENT=PROD` |

To run in production, both files must be specified:

```bash
COMPOSE_FILE=backend/docker-compose.yaml:backend/docker-compose-prod.override.yaml docker compose up --build -d
```

---

## Services

| Service  | Description                              |
|----------|------------------------------------------|
| `web`    | Django app served via Gunicorn           |
| `worker` | Celery worker for background tasks       |
| `db`     | PostgreSQL 17                            |
| `redis`  | Redis 8 (cache + Celery broker)          |
| `mailpit`| Local email UI — **dev only**, disabled in prod |

---

## Post-Deployment Steps

These must be run manually after each deployment:

```bash
# Apply database migrations
docker compose exec web ./manage.py migrate

# Collect static files (if static assets changed)
docker compose exec web ./manage.py collectstatic --no-input
```

> The production startup script (`deploy/run_prod.sh`) waits for the database and starts Gunicorn but does **not** run migrations automatically.

---

## Custom Management Commands

```bash
# Wait for dependencies before running other commands
./manage.py wait_for_resources --db --redis   # or --all

# Regenerate schema.graphql after schema changes
./manage.py graphql_schema

# Celery worker with autoreload (development only)
./manage.py run_celery_dev
```

---

## Verifying the Deployment

```bash
# Check all containers are running
docker compose ps

# Check web and worker logs
docker compose logs -f web
docker compose logs -f worker

# Ping the Celery worker
docker compose exec worker celery -A main inspect ping
```
