## 🚀 Overview

RC Select is a tool to help program and emergency response teams choose the right solution for their data management needs.


## 📋 Prerequisites

- **Docker & Docker Compose** (Required)
- **PostgreSQL** (Provided via Docker)
- **Python 3.12+** (For local development only)

## 🐳 Quick Start with Docker (Recommended)

### 1. Environment Setup

Create a `.env` file in the backend directory:


Configure your environment variables:

```env
DJANGO_SECRET_KEY=your-secret-key-here
```

### 2. Build and Start Services

```bash
# Build the containers
docker compose build

# Start the services
docker compose up -d
```

The API will be available at: `http://localhost:8000`

### 3. Database Setup

```bash
# Run database migrations
docker compose exec web python manage.py migrate

# Create a superuser account
docker compose exec web python manage.py createsuperuser

# Load sample data (optional)
docker compose exec web python manage.py loaddata seed-data/db_seed.json
```

### Common Docker Commands

```bash
# View running services
docker compose ps

# Access Django shell
docker compose exec web python manage.py shell

# Run database migrations
docker compose exec web python manage.py migrate

# Create new migration
docker compose exec web python manage.py makemigrations

# Collect static files
docker compose exec web python manage.py collectstatic

# View logs
docker compose logs web
docker compose logs db

# Stop services
docker compose down

# Rebuild and restart
docker compose down && docker compose build && docker compose up -d
```

## 📊 Database Management

### Sample Data

Load the provided sample dataset:

```bash
docker compose exec web python manage.py loaddata seed-data/db_seed.json
```

---

## ⚙️ Custom Management Commands

### `wait_for_resources`

Waits for application dependencies to become available before starting services. Used in startup scripts to ensure dependencies are ready.

```bash
# Wait for all dependencies
docker compose exec web python manage.py wait_for_resources --all

# Wait for specific services
docker compose exec web python manage.py wait_for_resources --db
docker compose exec web python manage.py wait_for_resources --redis
docker compose exec web python manage.py wait_for_resources --minio
docker compose exec web python manage.py wait_for_resources --celery-queue

# With custom timeout (default: 600s)
docker compose exec web python manage.py wait_for_resources --all --timeout 300
```

### `graphql_schema`

Generates the `schema.graphql` file from the current Strawberry schema. Run this whenever the GraphQL schema changes.

```bash
docker compose exec web python manage.py graphql_schema

# Output to a custom file
docker compose exec web python manage.py graphql_schema --out /path/to/schema.graphql
```

### `run_celery_dev`

Starts the Celery worker with Django's autoreload — restarts the worker automatically when code changes. **Development only.**

```bash
docker compose exec worker python manage.py run_celery_dev
```

In production, the `worker` service in Docker Compose runs Celery directly via `misc/dev/run_worker.sh`.

---

## 🔧 Services Overview

The `docker-compose.yaml` defines the following services:

| Service   | Description                                      | Port (local) |
|-----------|--------------------------------------------------|--------------|
| `web`     | Django application (Gunicorn in prod)            | 8000         |
| `worker`  | Celery worker for background tasks               | —            |
| `db`      | PostgreSQL 17                                    | —            |
| `redis`   | Redis 8 (cache + Celery broker)                  | —            |
| `mailpit` | Local SMTP/email UI (dev only)                   | 8025         |
