# PLAN.md

## Frontend (Next.js 14 + Tailwind + shadcn/ui)

### A) App Foundation

**What you do**

Create Next 14 (App Router, TS) with Tailwind + shadcn/ui, ESLint/Prettier.

Set absolute imports (@/), layout, theme tokens, typography scale.

Add TanStack Query, react-hook-form + zod, route loaders, error/loading UIs.

Add CI (typecheck, lint, build), PNPM workspaces (optional monorepo with BE).

**Acceptance (DoD)**

- pnpm build passes, no TS errors, ESLint clean (CI gate).
- Base layout renders, dark/light theme toggles; typography + spacing tokens present.
- Error boundaries and loading skeleton visible on /products when API mocked.
- ENV loading verified: NEXT_PUBLIC_API_BASE_URL etc.

### B) Auth & RBAC

**What you do**

Pages: login, signup, forgot/reset, profile.

Session auth with CSRF (via Django), cookie SameSite=Lax, Secure in prod.

Protected routes (+ role-based nav for admin, seller, customer).

**Acceptance**

- Login/signup/logout work E2E against BE.
- Hitting a protected page while signed-out redirects to /login?next=/account.
- Role badge chip shows in the header; admin-only pages are hidden unless admin.

### C) Responsive + A11y

**What you do**

Mobile-first, semantic landmarks (header/main/nav/footer), skip links, focus rings.

Logical tab order; color contrast pass (WCAG AA).

**Acceptance**

- axe DevTools shows 0 critical issues on Home, PLP, PDP, Checkout.
- Keyboard-only navigation completes checkout without traps.

### D) Catalog UX (PLP/PDP)

**What you do**

PLP: filters (category/price/rating), sort, search; URL query params drive state.

PDP: next/image gallery, variant selection, availability, read-only reviews.

SSR/ISR for PDP; skeleton loaders.

**Acceptance**

- Copying a filtered PLP URL reproduces state on fresh load.
- PDP renders on server with product data; variant switch updates price/stock.

### E) Cart & Checkout

**What you do**

Cart drawer + page, server-synced (session/user), optimistic updates.

Checkout steps: address → shipping → payment → review → receipt.

**Acceptance**

- Cart persists across sessions; cart quantity can't exceed stock.
- Validation errors shown inline per field; "Review" totals match BE-calculated totals.

### F) Real-time & Notifications (grow)

**What you do**

SSE or WebSocket hook for inventory/price change banners; toast notifications.

**Acceptance**

- Changing inventory server-side updates PLP/PDP banners within 2–5s.

### G) Personalization & Localization

**What you do**

next-intl locales, currency formatting; theme persists; "Recently viewed", "Recommended" slots (fed by BE).

**Acceptance**

- Locale switch persists across refresh; recommendations render when BE provides.

### H) SEO & Analytics

**What you do**

Metadata per page, JSON-LD Product/Breadcrumbs, canonical, sitemap/robots (next-sitemap).

Analytics (Plausible or Gtag). Server-side purchase events on checkout success.

**Acceptance**

- Lighthouse SEO ≥ 90 on PLP & PDP.
- /sitemap.xml accessible; purchase events visible in analytics dashboard.

### I) PWA & Push (grow)

**What you do**

next-pwa for offline shell (cached PLP/PDP read).

Web push opt-in banner (wireframe; provider later).

**Acceptance**

- App installable; offline PDP renders last-cached product content.

### J) Gamification (grow)

**What you do**

Points widget; profile badges; discount CTA based on points.

**Acceptance**

- Completing a paid order increases points; profile shows badge.

### K) Design polish

**What you do**

Brand tokens, spacing scale; Framer Motion on add-to-cart and modals.

**Acceptance**

- No layout shifts on add-to-cart; motion durations and easings consistent.

## Backend (Django + DRF + PostgreSQL)

### A) Project/Apps & Settings

**What you do**

Apps: users, catalog, orders, payments, reviews, core.

Settings split (base/dev/prod) using django-environ; JSON logging; /healthz.

pytest baseline and pytest-django; django-cors-headers.

**Acceptance**

- pytest passes locally and in CI; migrations apply; /healthz returns 200 with build info.

### B) Auth & RBAC

**What you do**

Custom User (email login). Use django-allauth (session) or DRF+djoser endpoints.

Roles/permissions via DRF; password reset; optional 2FA (django-otp).

**Acceptance**

- CSRF-protected session auth; DRF views enforce role permissions.
- Password reset email flow works in dev (console/email backend).

### C) Catalog & Inventory

**What you do**

Models: Category, Product, Variant, Attribute, Price, Inventory, Media (image paths), Slugs unique.

Admin with filters + image preview.

Public endpoints with filter/sort/search; Postgres FTS (tsvector + trigram).

**Acceptance**

- /products returns paginated list with query params for filter/sort/search.
- Indexed queries show ≤ 50ms DB time in logs for typical PLP (seeded data).

### D) Reviews

**What you do**

CRUD with moderation; rate limit + bad-words list (simple).

**Acceptance**

- New reviews flagged pending_moderation; product average rating recalculates.
- Throttling returns 429 when exceeded.

### E) Cart & Orders

**What you do**

Server cart (session or user); idempotent add/update/remove.

Orders/OrderLines, Address, ShipmentStatus, Coupons/Promotions (simple).

**Acceptance**

- Creating an order finalizes stock atomically; totals (tax/shipping/discount) match FE; coupon applied and validated.

### F) Payments

**What you do**

Stripe Payment Intents; signed webhook updates Payment/Order; idempotency keys persisted.

**Acceptance**

- Test card success → order.status=paid; failures recorded with reason.

### G) Emails & Notifications

**What you do**

Transactional emails via Resend/SendGrid; Celery + Redis for async.

Templates for order paid, order shipped (stub).

**Acceptance**

- Email sent on order=paid; Celery retries on transient failures.

### H) Security

**What you do**

HTTPS only in prod; CSP, HSTS, XFO, XSS-Protection; CSRF on.

django-ratelimit; captcha toggled on auth if abused.

**Acceptance**

- Security headers verified in response; rate-limited endpoints log events.

### I) Performance & Caching

**What you do**

Redis cache for fragments/queries; select_related/prefetch_related; critical indexes.

Simple k6 tests for PLP, PDP, checkout.

**Acceptance**

- p95 < 300 ms for public endpoints at seed load; PLP cache hit > 60%.

### J) AI/ML (grow)

**What you do**

Nightly collaborative/content-based recommendations to a table.

/recommendations?user=… returns ≥ 8 items.

**Acceptance**

- Endpoint returns items with fallback to popular/related if user cold start.

### K) Sustainability (grow)

**What you do**

Estimate order CO₂ by distance & method; "eco" category filter.

**Acceptance**

- Order JSON includes estimated_co2_kg; filter reduces catalog set accordingly.

## DevOps (VPS + k3s)

### A) Cluster & Networking

**What you do**

Install k3s; namespaces: infra, prod, monitoring.

Ingress Controller (nginx or built-in Traefik), cert-manager + ClusterIssuer (Let's Encrypt).

**Acceptance**

- kubectl get pods -A healthy; test Ingress + TLS against staging domain succeeds.

### B) Data Services

**What you do**

Helm: Bitnami Postgres + Redis with PVCs; resource requests/limits.

Nightly DB backups (CronJob pg_dump) to S3; restore guide.

**Acceptance**

- Backup object visible in bucket; restore to staging verified step-by-step.

### C) Containerization

**What you do**

Multi-stage Dockerfiles (web/api). Non-root users; health endpoints exposed.

Trivy scans in CI.

**Acceptance**

- Images run locally; no HIGH/CRITICAL vulns (or documented waivers).

### D) Deployments

**What you do**

K8s Deployments + Services (web/api); Ingress TLS for www & api.

Migrations + collectstatic Job during rollout; HPA at 70% CPU.

**Acceptance**

- Zero-downtime rollout; rollback tested; Stripe webhook path reachable.

### E) Secrets & Config

**What you do**

K8s Secrets: DB, Stripe, Email, Django secret; ConfigMaps for public vars.

Optional SealedSecrets/SOPS for Git.

**Acceptance**

- No secrets in repo; app reads them; kubectl describe secret shows expected keys.

### F) CI/CD

**What you do**

GitHub Actions: test → build → push GHCR → deploy via kubectl (KUBECONFIG secret) or ArgoCD.

**Acceptance**

- Merge to main auto-deploys; PRs show checks and deployment status.

### G) Monitoring & Logging

**What you do**

Sentry FE/BE; Loki + Grafana dashboards (latency, error rate, saturation).

Optional Prometheus metrics (Gunicorn/DRF).

**Acceptance**

- Errors visible in Sentry; logs searchable; uptime alert fires on induced outage.

### H) Security Hardening

**What you do**

securityContext (non-root, read-only FS), PodDisruptionBudget.

NetworkPolicy (api↔db/redis only); Ingress rate-limit.

**Acceptance**

- Cross-namespace traffic blocked; headers verified from edge.

### I) Documentation

**What you do**

OpenAPI (drf-spectacular), README setup/runbook, architecture diagram, ADRs.

**Acceptance**

- /schema serves; /docs pipeline renders; onboarding < 30 minutes.