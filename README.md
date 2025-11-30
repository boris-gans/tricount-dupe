# MyCount

This project is a full-stack web application designed to help individuals both track and split their expenses within a group. It provides a structured backend for data management and a responsive and sleek frontend for user interaction.

Please view the [report](./REPORT.md) for an in-depth description of the project and its features.

---

## Setup Instructions

### System requirements
- Git 2.40+
- Docker Desktop 24+ (includes Docker Compose v2)
- Optional for local (non-docker) development:
  - Python 3.11 (safer for certain packages)
  - Node.js 23.x and npm
  - Access to a PostgreSQL 15 instance (a container from `docker compose` works)

### 1. Clone the repository
```bash
git clone https://github.com/boris-gans/tricount_dupe.git
cd tricount_dupe
```

### 2. Launch locally with Docker (recommended)
```bash
docker compose build
docker compose up -d
```
- Backend API: http://localhost:8000
- Frontend app: http://localhost:3000
- Prometheus UI: http://localhost:9090 (scrapes `/metrics` from the backend)
- Grafana UI: http://localhost:3001 (default `admin/admin`, preloads a Backend Overview dashboard)
- Database data persists in the `postgres_data` volume.
- Monitoring data persists in the `prom_data` (Prometheus) and `grafana_data` volumes.

To stop the stack:
```bash
docker compose down
```

### 3. Run locally with Python + npm (alternative, no testing data)
1. Start the database using the compose service:
   ```bash
   docker compose up -d db
   ```
2. Configure backend dependencies:
   ```bash
   cd backend
   cp .env.example .env
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Start the backend API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. In a new terminal, set up and run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL` to your backend URL (e.g., the Azure Web App endpoint).

> Tip: If you prefer a locally installed PostgreSQL server, make sure it mirrors the connection settings from `backend/.env` or update the variables accordingly.

### Running the tests
- **Backend with Docker:**
  ```bash
  docker compose build
  docker compose up -d
  docker compose exec backend pytest --cov=app --cov-report=term-missing
  ```
- **Backend locally:** (from `backend` virtualenv)
  ```bash
  pytest
  ```
- **Frontend lint checks:** (from `frontend` directory)
  ```bash
  npm run lint
  ```

When running tests locally, keep the database container running so integration tests can reach PostgreSQL.

## Deploying to Azure Container Apps

Deployment secrets (those used in [deploy.yml](.github/workflows/deploy.yml)) are stored in GitHub secrets.

All runtime secrets live in Azure Container Apps as secrets/env vars. Images are pulled from your own Docker Hub (or ACR) repository. Networking uses external ingress (backend port 8000, frontend port 80).

### Deploy steps
1) **Clone & prepare env files locally**
   ```bash
   git clone https://github.com/boris-gans/tricount_dupe.git
   cd tricount_dupe
   cp backend/.env.example backend/.env
   # set DATABASE_URL_RAW (or DATABASE_USER/DB/PW/NAME), JWT_* and logging values
   ```
   - These values will be set as Azure secrets/env vars later; don’t commit `.env`.

2) **Build and push images to your registry**
   ```bash
   docker login
   docker build -t <dockerhub-username>/mycount-backend:latest backend
   docker push <dockerhub-username>/mycount-backend:latest
   docker build -t <dockerhub-username>/mycount-frontend:latest frontend
   docker push <dockerhub-username>/mycount-frontend:latest
   ```
   - Replace `<dockerhub-username>` with your account (or use ACR and adjust the tags).

3) **Create Azure resources**
   - Resource group + Container Apps environment (any Azure region).
   - A managed Postgres instance (or existing DB) reachable from Container Apps; require SSL.
   - Ensure outbound access to Postgres (default for Container Apps) and open ingress for public HTTPS on the apps you want exposed.

4) **Create secrets and env vars in the backend app**
   - Add secrets: `database-user`, `database-pw`, `database-name`, `database-url`, `jwt-secret-key`, `jwt-algorithm`, `jwt-expiration-minutes`, `log-format`, `base-logger-name`, `frontend-origins`.
   - Expose them as env vars expected by the code: `DATABASE_USER`, `DATABASE_PW`, `DATABASE_NAME`, `DATABASE_URL_RAW`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_MINUTES`, `LOG_FORMAT`, `BASE_LOGGER_NAME`, `FRONTEND_ORIGINS`. Set `PORT=8000`.

5) **Create Container Apps**
   - **Backend:** image `<dockerhub-username>/mycount-backend:latest`, targetPort `8000`, transport `auto/http`, external ingress enabled.
   - **Frontend:** image `<dockerhub-username>/mycount-frontend:latest`, targetPort `80`, external ingress enabled. Point its API calls to the backend URL (update `frontend/.env` before building if you want it baked in).

6) **Deploy/Update**
   - Use `az containerapp up` or `az containerapp update` to apply images, env vars, and ingress settings. Redeploy when you push new images.

7) **Smoke test**
   - Hit the backend health endpoint `/health` on the backend FQDN.
   - Load the frontend FQDN, log in with seeded users, and verify expenses/groups load.

## Health & Metrics
- Health: `GET /health` returns overall status and verifies database connectivity.
- Metrics: `GET /metrics` exposes Prometheus-format metrics including request counts, latency histograms, and error totals for scraping by the Prometheus service.
- A Grafana dashboard titled **Backend Overview** is auto-provisioned when running with Docker Compose.


## App Usage
If you launched the app with Docker the database gets initialized with some testing data allowing you to easily explore the app. This includes Users, Groups and Expenses.


---

The login credentials for the **Users** are:

><ins>Name:</ins> Borja Serra Planelles <ins>Email:</ins> borja@gmail.com <ins>Pw:</ins> 1

><ins>Name:</ins> Boris Gans <ins>Email:</ins> borisgans@gmail.com <ins>Pw:</ins> 1

><ins>Name:</ins> Ryan M <ins>Email:</ins> rm@gmail.com <ins>Pw:</ins> 1

><ins>Name:</ins> Matt Porteous <ins>Email:</ins> mp@gmail.com <ins>Pw:</ins> 1

---

To join existing **Groups** you can use the following credentials, or use the unique invite link accessible through each **Groups** UI:

><ins>Group Name:</ins> Apartment <ins>Pw:</ins> 1

><ins>Group Name:</ins> Spring Break <ins>Pw:</ins> 1

><ins>Group Name:</ins> AWS <ins>Pw:</ins> 1

---
