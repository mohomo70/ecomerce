# 4-Week, Day-by-Day Plan (20 workdays, W1D1 … W4D5)

> Conventions  
> - **Repo layout** (monorepo, recommended):  
>   ```
>   / (git root)
>   ├─ apps/
>   │  ├─ web/            # Next.js
>   │  └─ api/            # Django
>   ├─ infra/
>   │  ├─ docker/         # Dockerfiles, compose
>   │  ├─ k8s/            # k8s manifests (base/overlays)
>   │  └─ helm/           # (optional) umbrella or values files
>   ├─ .github/workflows/ # CI/CD
>   └─ docs/              # runbooks, ADRs, diagrams
>   ```
> - **Envs**: `.env.local` (dev), k8s `Secret` (staging/prod).  
> - **Branches**: `main` (protected), `feature/*`.  
> - **Labels**: `W1D1`…`W4D5` on GH issues/PRs.

---

## Week 1 — Foundations & Catalog

### W1D1 — Repos, build system, dev stack up

**Tasks**
1) **Create monorepo + tooling**
   - `git init`, `pnpm init -w`, workspaces in `package.json`:
     ```json
     { "private": true, "workspaces": ["apps/*"] }
     ```
   - Root tooling: Prettier, ESLint (root), commitlint + Husky:
     ```
     pnpm add -D prettier eslint @commitlint/{config-conventional,cli} husky lint-staged
     npx husky init
     echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.cjs
     ```
   - Root CI checks: `pnpm -r lint`, `pnpm -r typecheck`, `pnpm -r build`.

2) **Next.js app (App Router, TS, Tailwind, shadcn/ui, TanStack Query)**
   - `pnpm create next-app apps/web --ts --eslint --app --src-dir --import-alias "@/*"`
   - Tailwind: `pnpm -F web add tailwindcss postcss autoprefixer` + `npx tailwindcss init -p`
   - shadcn/ui: `pnpm -F web dlx shadcn-ui@latest init`
   - TanStack Query + RHF + Zod:  
     `pnpm -F web add @tanstack/react-query react-hook-form zod @hookform/resolvers next-intl`
   - Set base layout, theme tokens, typography scale, error/loading boundaries.

3) **Django project (DRF, settings split)**
   - `uv venv` or `pipenv`; `django-admin startproject core apps/api`
   - Apps: `users`, `catalog`, `orders`, `payments`, `reviews`, `core`.
   - Install deps: `pip install django djangorestframework django-environ django-cors-headers psycopg2-binary`
   - Settings split (`settings/base.py|dev.py|prod.py`), `/healthz` view; `urls.py` mounted on `/api/`.

4) **Dockerfiles + dev-compose**
   - `infra/docker/Dockerfile.web` (multi-stage: build → runner), runs as non-root `node`.
   - `infra/docker/Dockerfile.api` (multi-stage: builder → slim), runs as `appuser`.
   - `infra/docker/docker-compose.yml` with services:
     - `web` (Next.js), `api` (Django + gunicorn), `postgres`, `redis`, `mailhog`, `nginx` (reverse-proxy for local nice URLs).
   - Volumes for code hot-reload in dev; healthchecks for `web` (`/`), `api` (`/healthz`).

5) **Root CI skeleton (GitHub Actions)**
   - `.github/workflows/ci.yml` with matrix: Node LTS + Python 3.11; jobs: `lint`, `typecheck`, `test`, `build`.

**Artifacts**
- `apps/web/tailwind.config.ts`, `apps/web/src/app/layout.tsx`, `apps/web/src/app/(routes)/page.tsx`.
- `apps/api/core/settings/{base,dev,prod}.py`, `apps/api/core/urls.py`, `apps/api/core/views.py:/healthz`.
- `infra/docker/Dockerfile.web`, `Dockerfile.api`, `docker-compose.yml`.
- `.github/workflows/ci.yml`.

**Verification**
- `docker compose up --build` brings up nginx → web at http://localhost, api at /api/healthz.
- `pnpm -r build` completes; `pytest` (even if 0 tests) runs without error.

**DoD**
- CI (lint/typecheck/build) green.
- `docker compose up` starts full stack (web, api, db, redis, mailhog, nginx).
- `/api/healthz` returns 200 JSON with timestamp/version.

---

### W1D2 — Auth foundation (session + CSRF), FE screens

**Tasks**
1) **BE: session auth with CSRF**
   - Add `django-allauth` (or DRF+djoser if preferred); enable email login.
   - `INSTALLED_APPS += ['allauth','allauth.account','rest_framework','corsheaders']`.
   - CSRF: ensure `CsrfViewMiddleware` active; `CORS_ALLOW_CREDENTIALS=True`, `CORS_ALLOWED_ORIGINS=["http://localhost:3000"]`.
   - Routes:
     - `POST /auth/login` → sets `sessionid` cookie, returns `{user}`.
     - `POST /auth/logout` → 204.
     - `POST /auth/register` → creates user (email unique).
     - `POST /auth/password/reset|confirm`.
     - `GET /me` → current user + roles.

2) **Roles & permissions**
   - `users.models.User` (custom), `roles = ArrayField(choices=customer|seller|admin)`.
   - DRF `permission_classes` that check roles for admin endpoints.

3) **FE: auth screens**
   - `/login`, `/signup`, `/forgot-password`, `/reset-password/[token]`, `/account`.
   - Hook up forms via `react-hook-form + zod`; on submit:
     - include `credentials: 'include'`; first GET `/api/csrf` (if used) or rely on `csrftoken` from cookie; send `X-CSRFToken`.
   - Protected routes: wrapper checks `GET /me`; unauth → redirect to `/login?next=…`.
   - Header shows Role chip(s).

**Artifacts**
- BE serializers/views for auth, CSRF helper endpoint if needed.
- FE components: `<AuthForm />`, route guards, `useUser()` hook with TanStack Query.

**Verification**
- Manual: sign up, confirm login, visit `/account`, log out.
- Browser devtools: `sessionid` and `csrftoken` HttpOnly cookies present; `SameSite=Lax`, `Secure` (in staging).

**DoD**
- Sign in/out works E2E.
- `/account` gated (redirect when unauth).
- CSRF cookie set and used on POSTs; role chip visible when applicable.

---

### W1D3 — Catalog models, admin, seed, read APIs (+ search/filters)

**Tasks**
1) **Models**
   - `Category(slug unique, name, parent nullable)`
   - `Product(slug unique, name, description, category FK, attributes JSONB)`
   - `Variant(product FK, sku unique, attributes JSONB, price Decimal(10,2), stock int)`
   - `Media(product FK, url, alt)` (later S3)
   - Indexes: unique slug/sku, btree on price/stock, GIN on `to_tsvector('simple', name || ' ' || description)`.
2) **Admin**
   - List filters (category, in_stock>0), search by name/sku, image preview in change list.
3) **Seed**
   - Mgmt command `python manage.py seed_products --count 100`.
4) **DRF endpoints**
   - `GET /products` with `?search=&category=&min_price=&max_price=&rating=&sort=&page=` (documented).
   - `GET /products/{slug}` → detail with variants, media, rating summary.
   - Full-text search with tsvector; trigram optional.
5) **Performance logging**
   - Log DB time per request; target ≤ 50ms DB time for PLP (seeded).

**Artifacts**
- Migrations, admin customizations, `api/catalog/serializers.py`, `views.py`, `urls.py`.

**Verification**
- `pytest` basic tests: model create/read, `/products` pagination, filter correctness.
- Seed: 100+ products visible in admin and API.
- Inspect logs: DB timing for `/products?category=…` ≤ 50ms (avg).

**DoD**
- `/api/products` fast (≤50ms DB per query typical).
- Admin usable for content ops; slugs unique; search/filter/sort correct.

---

### W1D4 — PLP/PDP (SSR/ISR), SEO basics

**Tasks**
1) **PLP**
   - URL-driven filters/sort/search via `searchParams` in Next App Router.
   - `useQuery` with `keepPreviousData`; skeletons for list.
   - Filter components (checkbox, slider, rating); empty-state when none found.
2) **PDP**
   - `generateStaticParams` for ISR (or SSR on access).
   - Gallery with `next/image`; variant selector updates price/stock; read-only reviews.
3) **SEO**
   - `generateMetadata` per page; JSON-LD (Product, BreadcrumbList); canonical tags.
   - `next-sitemap` setup; `robots.txt`.
4) **Perf polish**
   - Image sizes, `priority` for hero, defer non-critical scripts.

**Artifacts**
- `apps/web/src/app/(catalog)/products/page.tsx`, `products/[slug]/page.tsx`.
- SEO util: `lib/seo.ts` to build JSON-LD.

**Verification**
- Copy a filtered PLP URL → new tab reproduces state.
- Lighthouse on PLP/PDP (mobile) → SEO ≥ 90 (record screenshot).
- PDP renders server-side (view source / devtools).

**DoD**
- PLP/PDP shippable, shareable URLs, SSR/ISR working; SEO score met.

---

### W1D5 — Cart API + FE cart with optimistic sync

**Tasks**
1) **BE: cart**
   - Session/user cart model; endpoints:
     - `GET /cart`
     - `POST /cart` (idempotent upsert lines)
     - `PATCH /cart/lines/{id}` (qty)
     - `DELETE /cart/lines/{id}`
   - Server validation: `qty <= stock`, variant exists, min/max checks.
   - Return canonical totals object: `{subtotal, discounts, shipping_estimate, tax_estimate, total}`.
2) **FE: cart**
   - Cart drawer + page; optimistic updates (rollback on server error).
   - Persist cart across sessions; empty state, max stock fences, disabled buttons on OOS.
3) **Tests**
   - Unit tests for reducers/hooks; API contract tests.

**Artifacts**
- BE `orders/cart.py`, DRF views/serializers; FE `components/cart/*`, `hooks/useCart.ts`.

**Verification**
- Try to add > stock → inline error; refresh still enforces server state.
- Unauth then auth → cart merges (if spec’d) or remains session-scoped (documented).

**DoD**
- Cart persists; server enforces stock limits; optimistic UX feels instant (<150ms).

---

## Week 2 — Checkout, Payments, Email

### W2D1 — Checkout wizard + order draft

**Tasks**
1) **FE wizard**
   - Steps: Address → Shipping → Review (Payment next day).
   - RHF forms with zod schemas; “Edit” per section; progress indicator; autosave to server.
2) **BE draft**
   - `POST /orders/draft`: accepts address; calculates shipping options (flat rate or stub); returns `{draft_id, totals, shipping_options}`.
   - Draft recalculation on updates (idempotent).
3) **Edge cases**
   - OOS on review → show diff + block finalize.

**Artifacts**
- Endpoints `/orders/draft`, `/orders/draft/{id}` (PATCH).
- FE pages `/checkout/*`, `components/CheckoutStepper.tsx`.

**Verification**
- Change address → shipping recalculates; totals consistent.
- Refresh mid-checkout → step resumes (server stores draft state).

**DoD**
- Draft totals correct after edits; back/next safe and idempotent.

---

### W2D2 — Stripe Payment Intents + webhook + order state machine

**Tasks**
1) **Payments**
   - `POST /payments/intent` → create PaymentIntent; return `client_secret`.
   - FE adds Stripe Elements/Card; confirm with `stripe.confirmCardPayment`.
   - Store idempotency keys (header hash of draft_id + user + timestamp).
2) **Webhook**
   - `/payments/webhook` (signed, tolerates retries).
   - On `payment_intent.succeeded` → mark payment paid, finalize order from draft:  
     - create `Order` from draft, decrement stock atomically (DB transaction), capture payment ref.
3) **States**
   - Order status machine: `draft → awaiting_payment → paid → fulfilled → cancelled`.
   - Payment status: `requires_action|processing|succeeded|failed`.

**Artifacts**
- BE `payments/views.py`, `orders/services.py` (finalize order).
- FE `/checkout/payment` page; success/failure pages.

**Verification**
- Stripe test cards: success, 3DS (if enabled), failure. Webhook receives and idempotently updates order.
- Stock decremented exactly once even with duplicate webhook.

**DoD**
- Test card completes → order `paid`; failures handled (visible message & retry).

---

### W2D3 — Transactional email via Celery

**Tasks**
1) **Celery**
   - Configure Celery worker + beat (use Redis); health check task.
   - Email backend (Resend/SendGrid); env secrets in dev via Mailhog.
2) **Templates**
   - Order confirmation (subject, text, HTML), include order summary, totals, links.
3) **Triggers**
   - Signal on order `paid` → enqueue email task (retries with exponential backoff).

**Artifacts**
- `apps/api/core/celery.py`, `tasks.py`; email templates under `templates/emails/`.
- k8s Deployments for `worker` later (not yet).

**Verification**
- On paid order in dev → email appears in Mailhog; kill worker mid-send → retry works and single send.

**DoD**
- Email sent on order paid; retry pathway logged and observable.

---

### W2D4 — i18n, currency, personalization slots

**Tasks**
1) **FE i18n**
   - `next-intl` with locales `en`, `de` (as example); locale switch in header; persist to cookie.
   - Currency formatting via `Intl.NumberFormat` driven by locale.
2) **Personalization**
   - “Recently viewed” in local storage + server fallback; “Recommended” slot fed by `/recommendations` endpoint (stub).
3) **Theme**
   - Toggle (dark/light/system) persists to `localStorage`.

**Artifacts**
- `i18n/messages/en.json`, `de.json`; `middleware.ts` for locale; `components/LocaleSwitcher.tsx`.
- `components/slots/Recommended.tsx`.

**Verification**
- Switch locale → persists across refresh and routes; currency formats change.
- Recommended slot shows items when BE supplies; empty gracefully otherwise.

**DoD**
- Locale switch persists; recommendations render when API provides them.

---

### W2D5 — A11y sweep & UX polish

**Tasks**
1) **A11y**
   - Semantic landmarks; skip link; keyboard order; focus rings; ARIA labels where required.
   - Axe scan on Home, PLP, PDP, Checkout.
2) **Validation & errors**
   - Field-level errors, inline; global error boundaries for network failures; loading skeletons standardized.
3) **QA**
   - Mobile testing (iOS/Android), reduce CLS; image `sizes` attributes tuned.

**Artifacts**
- A11y checklist in `docs/a11y.md`.
- Shared `<FormFieldError />` component.

**Verification**
- axe shows 0 critical on key pages; keyboard-only checkout flow passes; console clean.

**DoD**
- axe clean; 0 console errors; UX crisp.

---

## Week 3 — Kubernetes on VPS

### W3D1 — k3s, certs, DNS

**Tasks**
1) **Install k3s on VPS**
   - `curl -sfL https://get.k3s.io | sh -` (hardened: disable traefik if using nginx-ingress).
   - Namespaces: `infra`, `prod`, `monitoring`.
2) **Ingress Controller & cert-manager**
   - Install nginx-ingress (Helm) or keep Traefik; pick one and stick to it.
   - Install `cert-manager`; create `ClusterIssuer` (Let’s Encrypt HTTP-01).
3) **DNS**
   - Point `*.staging.example.com` to VPS IP; test with a throwaway Nginx `DefaultBackend`.

**Artifacts**
- `infra/k8s/base/namespaces.yaml`
- `infra/k8s/infra/nginx-ingress/*` or Traefik values.
- `infra/k8s/infra/cert-manager/cluster-issuer.yaml`

**Verification**
- `kubectl get pods -A` all running.
- `https://placeholder.staging.example.com` returns 200 with valid TLS.

**DoD**
- Staging domain over HTTPS loads a placeholder page.

---

### W3D2 — Postgres & Redis via Helm, secrets, connectivity

**Tasks**
1) **Helm installs**
   - Bitnami charts with PVCs:
     ```
     helm repo add bitnami https://charts.bitnami.com/bitnami
     helm install pg bitnami/postgresql -n infra -f values-postgres.yaml
     helm install redis bitnami/redis -n infra -f values-redis.yaml
     ```
   - Set resource requests/limits; storage class; backups disabled here (CronJob later).
2) **Secrets**
   - `prod` namespace Secrets: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `REDIS_URL`, `DJANGO_SECRET_KEY`, Stripe keys, email creds.
3) **Connectivity**
   - Port-forward test:
     ```
     kubectl -n infra port-forward svc/pg-postgresql 5433:5432
     psql -h 127.0.0.1 -p 5433 ...
     ```
   - Same for Redis with `redis-cli`.

**Artifacts**
- `infra/k8s/infra/values-postgres.yaml`, `values-redis.yaml`.
- `infra/k8s/prod/secrets.yaml` (templated; real values via SealedSecrets/SOPS later).

**Verification**
- DB/Redis reachable; credentials rotated once and app configs updated.

**DoD**
- DB/Redis ready; credentials stored in k8s Secrets; manual connect verified.

---

### W3D3 — API manifests, media strategy, migration job

**Tasks**
1) **API Deployment**
   - `Deployment` (replicas=2), `Service` (ClusterIP), `Ingress` `api.staging.example.com`.
   - Liveness `/healthz`, readiness `/healthz`.
   - `envFrom` Secrets/ConfigMaps; Gunicorn cmd; run as non-root; read-only root FS + writable /tmp.
2) **Static/media**
   - Static collected to `/static`; media to PVC (for now); health docs on S3 switch later.
3) **Job**
   - `Job` to run `python manage.py migrate && collectstatic`.
4) **NetworkPolicy**
   - Allow only `api` ↔ `postgres`/`redis`.

**Artifacts**
- `infra/k8s/prod/api/deployment.yaml|service.yaml|ingress.yaml|job-migrate.yaml|networkpolicy.yaml`.

**Verification**
- `curl https://api.staging.example.com/healthz` 200.
- `GET /api/products` lists seeded data (forward temp DB or seed again in staging).

**DoD**
- API live under `api.staging.example.com` serving `/healthz` & `/api/products`.

---

### W3D4 — Web manifests, env wiring, Stripe webhook

**Tasks**
1) **Web Deployment**
   - Next.js container (static export + Node server); `NEXT_PUBLIC_API_BASE_URL` via ConfigMap; `Ingress` `www.staging…`.
2) **Webhook exposure**
   - Path `/payments/webhook` routed to API; allowlist Stripe IPs (optional) and require signature.
3) **CSP/headers (basic)**
   - Add nginx annotation or app headers for sensible defaults (tighten W4D3).

**Artifacts**
- `infra/k8s/prod/web/deployment.yaml|service.yaml|ingress.yaml`
- `infra/k8s/prod/configmap.web.yaml` (NEXT_PUBLIC_ vars)

**Verification**
- Site loads on `https://www.staging…`; PLP hits real API.
- Stripe CLI: `stripe listen --forward-to https://api.staging…/payments/webhook` → 2xx received.

**DoD**
- Site live via k8s; Stripe webhook returns 2xx on test events.

---

### W3D5 — CI/CD, HPA, rollback drill

**Tasks**
1) **CI/CD**
   - GH Actions: jobs `test → build → trivy scan → push GHCR → kubectl apply -k infra/k8s/prod`.
   - `KUBECONFIG` secret uploaded to repo; or ArgoCD app points at `infra/k8s`.
2) **Autoscaling**
   - HPA for web/api at 70% CPU target; set requests/limits.
3) **Rollback**
   - `kubectl rollout status deployment/api`; break the image tag, observe, then `kubectl rollout undo`.

**Artifacts**
- `.github/workflows/cicd.yml`
- `infra/k8s/prod/hpa.web.yaml`, `hpa.api.yaml`

**Verification**
- Merge to `main` triggers deploy; pods cycle; service stays up (zero downtime).
- Rollback results in previous version serving traffic.

**DoD**
- Push to `main` rolls a new version with 0 downtime; rollback succeeds.

---

## Week 4 — Observability, Security, Extras

### W4D1 — Sentry, Loki/Grafana, dashboards/alerts

**Tasks**
1) **Sentry**
   - FE: add DSN; wrap with ErrorBoundary + tracing on route changes.
   - BE: `sentry-sdk` with Django integration.
2) **Loki + Grafana**
   - Helm install Loki/Promtail; ship container logs; Grafana dashboards for:
     - API latency (p50/p95), error rate, CPU/Mem, 5xx counts, queue depth (Celery).
3) **Alerts**
   - Grafana alert rules: API p95 > 300ms 5m; 5xx rate > 1%; uptime check /healthz.

**Artifacts**
- `infra/helm/loki/*` or manifests; Grafana dashboards JSON in repo.
- `docs/observability.md` with runbook.

**Verification**
- Intentionally throw an error in staging → shows up in Sentry.
- Query logs in Grafana → filter by `app=api`.

**DoD**
- Errors visible in Sentry; logs searchable; alert fires on forced outage.

---

### W4D2 — Backups + restore; media to S3/MinIO

**Tasks**
1) **DB backup CronJob**
   - Nightly `pg_dump` to S3 (or MinIO) with lifecycle policy; encryption at rest.
   - Retention: 7 daily, 4 weekly; tag with commit SHA + timestamp.
2) **Restore drill**
   - New ephemeral DB in `staging-restore` namespace; restore latest backup; run smoke tests.
3) **Media storage**
   - Switch Django `DEFAULT_FILE_STORAGE` to S3; signed URLs; migrate existing media.

**Artifacts**
- `infra/k8s/prod/cronjob.pg_dump.yaml`; `docs/restore-runbook.md`.
- Django storage settings; bucket policies.

**Verification**
- Backup object exists with correct size; restore completes < 10 minutes and app reads data.
- Media loads via S3 URLs; permissions correct (public-read if desired).

**DoD**
- Backup artifact exists; restore documented and tested end-to-end.

---

### W4D3 — Security hardening

**Tasks**
1) **Headers**
   - CSP (report-only first): `default-src 'self'; img-src 'self' https: data:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; connect-src 'self' https://*.stripe.com https://plausible.io; frame-src https://js.stripe.com;` (tune as needed)
   - HSTS (max-age 15552000; includeSubDomains; preload), X-Content-Type-Options, Referrer-Policy.
2) **Ingress rate limits**
   - Nginx annotations for rate limiting login/password endpoints.
3) **Pod security**
   - `securityContext` (runAsNonRoot, runAsUser, readOnlyRootFilesystem), `PodDisruptionBudget`.
4) **NetworkPolicy**
   - Enforce only required flows (api↔db/redis).
5) **Ratelimit**
   - `django-ratelimit` on auth & reviews; adaptive captcha toggle.

**Artifacts**
- Ingress annotations; `k8s` `NetworkPolicy`, `PDB`, security contexts in Deployments.
- `settings/security.py` for headers.

**Verification**
- `curl -I` shows headers; OWASP ZAP baseline scan basic pass.
- Attempt cross-namespace access fails; rate limit returns 429 after threshold.

**DoD**
- Security headers present; unwanted traffic blocked; baseline scans pass.

---

### W4D4 — PWA + realtime + points skeleton (feature-flagged)

**Tasks**
1) **PWA**
   - `next-pwa` plugin; `manifest.json`; icons; offline routes for PLP/PDP cached.
2) **Realtime inventory**
   - SSE endpoint `/inventory/stream?product=…` or Django Channels WebSocket.
   - FE hook that subscribes on PDP/PLP mount and shows “inventory changed” banner.
3) **Gamification**
   - Points field on User or separate `LoyaltyAccount`; on order `paid`, increment by rule (e.g., 1pt per $1).
   - Badge thresholds (seeded) and profile display.
4) **Feature flags**
   - `NEXT_PUBLIC_FLAGS={"realtime":true,"pwa":true,"points":true}` (ConfigMap in k8s).

**Artifacts**
- Service worker, manifest, `_document` updates.
- SSE/Channels server view; FE `useInventoryStream`.

**Verification**
- Chrome shows “Install” prompt; offline PDP shows cached content.
- Admin reduces stock on a product → PDP banner within 2–5s.
- Place order in staging → points increment; badge shown if threshold crossed.

**DoD**
- App installable; realtime inventory banner updates; points increment on paid order.

---

### W4D5 — Docs, performance pass, Playwright e2e

**Tasks**
1) **OpenAPI + docs**
   - `drf-spectacular` generates `/schema`; static docs page `/docs` (ReDoc).
   - Architecture diagram (`docs/architecture.drawio.png`), ADRs for auth, storage, payments.
   - Onboarding guide: “setup in 30 minutes” with exact commands.
2) **Performance**
   - Add/confirm indexes; ensure `select_related/prefetch_related` on hot endpoints.
   - Redis cache for PLP queries (keyed by filters); target cache hit > 60%.
   - k6 smoke script for PLP (100 VUs, 1m); tune Gunicorn workers/threads.
3) **Playwright e2e**
   - Scenarios: signup/login → add to cart → checkout → Stripe success → webhook → receipt page.
   - Run in CI (headed in staging optional, headless by default).

**Artifacts**
- `/schema`, `/docs`; `docs/*`.
- `k6/plp-smoke.js`; `playwright/e2e.spec.ts`; CI step to run e2e on staging.

**Verification**
- `/schema` accessible; docs link from footer.
- k6 report: p95 public endpoints < 300ms.
- e2e suite green; failure screenshots/videos stored as CI artifacts.

**DoD**
- Docs complete; p95 endpoints < 300 ms; e2e suite green.
