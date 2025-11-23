# Requirements Overview

1. Code Quality and Testing
    -   Refactor your code to remove code smells (e.g. duplication, long methods, hardcoded values) and follow SOLID principles.
    -   Add automated unit and integration tests.
    -   Achieve at least 70% code coverage.
    -   Include a test report in your repo.
2. Continuous Integration (CI)
    -   Create a CI pipeline (more details about this to come)
    -   Pipeline must run tests, measure coverage, and build your application.
    -   The pipeline should fail if tests fail or coverage is below 70%.
3. Deployment Automation (CD)
    -   Containerize the app using Docker.
    -   Add a deployment step to a cloud platform (more details about this to come).
    -   Configure secrets and triggers so only the main branch deploys automatically.
4. Monitoring and Health Checks
    -   Add a /health endpoint returning basic app status.
    -   Expose metrics for request count, latency, and errors.
    -   Provide a minimal Prometheus or Grafana setup (config or screenshots).
5. Documentation
    -   Update README.md with clear run, test, and deploy instructions.
    -   Add a short REPORT.md summarizing what was improved and how.

# Steps

1. Review code, look for oppurtunities to implement design patterns and enforce SOLID principles
2. Implement health checks + monitoring
    -   grafana and prometheus
    -   access control for monitoring?
3. Add some more tests and configure html coverage report
4. Look into GH actions, how to configure CI/CD stuff on it? How can it init an Azure deployment?
5. Deploy on azure, only after GH actions have been setup


# Updated Steps
1. Hardening pass (refactor + expand unit/integration tests + coverage tooling) so later work rests on a stable codebase.
2. Observability sprint (health endpoints, /metrics, Prom/Graf stack, docs screenshots).
3. Container/infra alignment (updates to docker-compose, environment variables, secrets, README instructions).
4. CI pipeline (GitHub Actions running tests, coverage gate, Docker builds).
5. Azure deployment automation triggered from CI (only main branch deploys).
6. Final documentation/report polish.


## Explanations
**Prometheus/Grafana**

-   Instrument FastAPI: add a /health handler that checks Postgres via a lightweight query and returns JSON {status, db, version}; then add a /metrics endpoint by wiring prometheus_fastapi_instrumentator (or manual prometheus_client) in backend/main.py. Wrap routers/middlewares to log counters (Counter("http_requests_total", ...)), histograms for latency, and a Gauge for DB connectivity. Include custom labels such as endpoint, method, and status_code so Grafana pivots are meaningful.

-   Capture domain-specific metrics: increment counters when users create/update expenses, track number of active groups, and expose Postgres connection-pool usage. Add try/finally blocks around DB access to observe failures. If you need frontend metrics, emit them via a small /metrics/frontend exporter in the React app using prom-client and let Nginx (or the dev server) proxy it, but the assignment can be satisfied with backend metrics plus container stats.

-   Compose services: extend docker-compose.yml with prometheus and grafana services. Mount monitoring/prometheus.yml that defines scrape jobs for backend:8000/metrics, the Postgres exporter (optional), and the node exporter. Expose Grafana on a different host port (e.g. 3001 (line 3000)), mount a provisioning file so dashboards and the Prometheus data source are created automatically, and configure admin credentials via env vars or Docker secrets.

-   Secure access: keep Prometheus internal (no host port) and only expose Grafana through HTTPS with basic auth or Azure Application Gateway once deployed. Restrict scrape endpoints using FastAPI dependencies that ensure X-Internal-Monitoring headers or network-based allow lists, satisfying the “access control for monitoring?” note in assingment-2-plan.md (lines 28-29).

-   Documentation and validation: capture screenshots of Grafana panels (request rate, latency histogram, error rate, DB status) to satisfy the “Provide a minimal Prometheus or Grafana setup” requirement in assingment-2-plan.md (lines 16-19), and describe how to run the monitoring stack in README.md.

**Azure Deployment**

-   Pick a hosting target that supports multi-container apps: Azure Web App for Containers (docker-compose), Azure Container Apps, or AKS if you anticipate scale. Simplest path is Azure Web App for Containers because it accepts your existing compose file.

-   Pipeline flow: the GitHub Actions workflow should run tests/coverage, build versioned Docker images for backend, frontend, and monitoring exporters, push them to Azure Container Registry (ACR), then run az webapp create/compose up (or az containerapp up) against the registry. Secrets for AZURE_CREDENTIALS, REGISTRY_LOGIN_SERVER, etc. stay in GitHub.

-   Azure resources: provision a Resource Group, ACR, and either an Azure Database for PostgreSQL Flexible Server (recommended) or a managed Postgres container with persistent volumes. Configure environment variables/secrets for DB credentials, Prometheus scrape URLs, and Grafana admin password via the Azure service.

-   Observability in Azure: keep Prometheus and Grafana containers in the same compose deployment (internal network). For long-term storage or alerts, either expose Prometheus via an internal load balancer that Azure Monitor can scrape or push FastAPI metrics to Azure Monitor using the OpenTelemetry exporter alongside Prometheus.