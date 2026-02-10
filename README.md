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
docker compose exec web python manage.py loaddata seed_data/db_seed.json
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

### Running Tests

```bash
# Run all tests
docker compose exec web python manage.py test

# Run specific test
docker compose exec web python manage.py test tool_picker.tests.test_field_alignment

# Run with coverage
docker compose exec web python -m pytest --cov=tool_picker
```

## 📊 Database Management

### Sample Data

Load the provided sample dataset:

```bash
docker compose exec web python manage.py loaddata seed_data/db_seed.json
```
