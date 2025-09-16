# E-commerce Monorepo

A modern e-commerce platform built with Next.js and Django, following the W1D1 schedule from the 4-week development plan.

## Architecture

This is a monorepo containing:

- **Frontend**: Next.js 15 with App Router, TypeScript, Tailwind CSS
- **Backend**: Django 5 with Django REST Framework
- **Infrastructure**: Docker containers with PostgreSQL and Redis
- **CI/CD**: GitHub Actions for automated testing and building

## Project Structure

```
/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # Django backend
├── infra/
│   └── docker/           # Docker configuration
├── .github/
│   └── workflows/        # CI/CD pipelines
└── docs/                 # Documentation
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- pnpm (package manager)

### Development Setup

1. **Clone and install dependencies:**

   ```bash
   git clone <repository-url>
   cd ecommerce-monorepo
   pnpm install
   ```

2. **Start the development environment:**

   ```bash
   docker compose -f infra/docker/docker-compose.yml up --build
   ```

   This will start:
   - Next.js web app at http://localhost:3000
   - Django API at http://localhost:8000
   - PostgreSQL database
   - Redis cache
   - MailHog for email testing
   - Nginx reverse proxy

3. **Access the applications:**
   - Web app: http://localhost
   - API health check: http://localhost/api/healthz/
   - MailHog UI: http://localhost:8025

### Individual Development

**Frontend (Next.js):**

```bash
cd apps/web
pnpm dev
```

**Backend (Django):**

```bash
cd apps/api
python manage.py runserver
```

## Features Implemented (W1D1)

✅ **Monorepo Setup**

- pnpm workspaces configuration
- Prettier, ESLint, commitlint, Husky
- Root-level CI scripts

✅ **Next.js Application**

- App Router with TypeScript
- Tailwind CSS for styling
- TanStack Query for data fetching
- React Hook Form + Zod for forms
- next-intl for internationalization

✅ **Django Backend**

- Django REST Framework
- Settings split (base/dev/prod)
- Health check endpoint
- CORS configuration
- Multiple apps: users, catalog, orders, payments, reviews

✅ **Docker Infrastructure**

- Multi-stage Dockerfiles for both apps
- Docker Compose with all services
- Nginx reverse proxy
- Health checks for all services

✅ **CI/CD Pipeline**

- GitHub Actions workflow
- Lint, typecheck, test, and build jobs
- PostgreSQL and Redis services for testing

## Next Steps (W1D2)

The next day will focus on:

- Authentication system with session + CSRF
- User roles and permissions
- Frontend auth screens and protected routes

## Development Commands

```bash
# Install dependencies
pnpm install

# Run all linters
pnpm lint

# Run type checking
pnpm typecheck

# Run tests
pnpm test

# Build all applications
pnpm build

# Start development environment
docker compose -f infra/docker/docker-compose.yml up --build
```

## Environment Variables

### Frontend (.env.local)

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### Backend (.env)

```
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Verification

To verify the setup is working:

1. **CI Pipeline**: All GitHub Actions jobs should pass
2. **Docker Compose**: `docker compose up --build` should start all services
3. **Health Check**: `curl http://localhost/api/healthz/` should return 200
4. **Web App**: http://localhost should show the e-commerce homepage

## DoD (Definition of Done) - W1D1

- ✅ CI (lint/typecheck/build) green
- ✅ `docker compose up` starts full stack (web, api, db, redis, mailhog, nginx)
- ✅ `/api/healthz` returns 200 JSON with timestamp/version
