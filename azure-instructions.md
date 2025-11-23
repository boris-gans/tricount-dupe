Below is a clear, step-by-step guide for producing an **x86_64 (amd64)** image of your frontend, pushing it to Azure Container Registry (ACR), and avoiding any ARM-related issues that break Azure Container Apps deployments.

---

# Overview

Your Mac M4 produces **arm64** images by default. Azure Container Apps **does support ARM**, but **only in certain regions and only if you explicitly set workload profiles**—and even then, ARM images regularly cause problems.

The safest, universal approach is:

## Build **multi-architecture images** or explicitly build **amd64** images.

You will do this using **Docker Buildx**, which is specifically designed for cross-platform builds.

---

# 1. Fix Your Dockerfile

Your Dockerfile has one small issue: the `build` stage is unnamed. You reference it with `--from=build`, but you never declare a stage named `build`.

Corrected version:

```dockerfile
FROM mycountregistry.azurecr.io/node:23 AS build

WORKDIR /app

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

# 2. Ensure Your Base Image Exists for amd64

You are pulling:

```
FROM mycountregistry.azurecr.io/node:23
```

Check:

* Does that image exist for **amd64**?
* If not, replace it with the official Node image:

```
FROM node:23
```

Or push a multi-arch node image to your ACR first.

---

# 3. Enable Docker Buildx

Most likely already enabled on your Mac, but verify:

```bash
docker buildx ls
```

If no builder exists, create one:

```bash
docker buildx create --use
```

---

# 4. Build Your Frontend Image for amd64 Only (recommended)

```bash
docker buildx build \
  --platform linux/amd64 \
  -t mycountregistry.azurecr.io/mycount-frontend:latest \
  --push .
```

This creates an image whose architecture is **amd64** and pushes it directly to ACR.

Azure Container Apps will now accept and run it.

---

# 5. OR: Build a Multi-Architecture Image (if you want ARM + AMD)

This creates a single tag with multiple architectures inside:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t mycountregistry.azurecr.io/mycount-frontend:latest \
  --push .
```

Azure will automatically select amd64.

---

# 6. Verify the Image in ACR

In the Azure Portal → Container Registry → Repositories → `mycount-frontend`, open the **Manifests** tab.

You should see entries like:

* `linux/amd64`
* (optionally) `linux/arm64`

If you only built `linux/amd64`, you’ll see only that.

---

# 7. Deploying the Container App

Once the correct image is in ACR, redeploy your frontend Container App:

### Using Azure CLI:

```bash
az containerapp update \
  --name mycount-frontend \
  --resource-group <rg-name> \
  --image mycountregistry.azurecr.io/mycount-frontend:latest
```

Azure will now successfully pull & run the container.

---

# 8. Summary of What You Must Do

| Step                         | Required? | Purpose                            |
| ---------------------------- | --------- | ---------------------------------- |
| Fix Dockerfile               | Yes       | Ensures proper multi-stage build   |
| Build with Buildx            | Yes       | Enables cross-architecture build   |
| Use `--platform linux/amd64` | Yes       | Produces an Azure-compatible image |
| Push to ACR                  | Yes       | Required for Azure Container Apps  |

---

## Setting envs for backend
az containerapp update \
  --name mycount-backend \
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A \
  --set-env-vars "

    "