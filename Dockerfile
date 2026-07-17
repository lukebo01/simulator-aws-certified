# Dockerfile – Production-Grade Architecture
# Frontend compilato a build time (CodeBuild), servito staticamente da Caddy
# Backend Python gira solo in --backend-only mode sulla porta 8000 (locale)
# Caddy fa da reverse proxy sulla porta 3000 (pubblica) verso Fargate ALB

FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:3.12-slim

# 1. Installa le dipendenze di sistema e tool per scaricare Caddy
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    debian-keyring \
    debian-archive-keyring \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# 2. Installa Caddy Server ufficiale (per amd64)
RUN curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update \
    && apt-get install -y caddy \
    && rm -rf /var/lib/apt/lists/*

# 3. Installa Node.js 20 (necessario per la build del frontend)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Crea la cartella di destinazione per il frontend statico
RUN mkdir -p /srv

# 4. Configurazione porte interne per evitare conflitti
# - Caddy ascolterà sulla 3000 (pubblica, richiesta da AWS ALB)
# - Backend Python girerà sulla 8000 (locale, non esposta)
# - API_URL vuoto → frontend usa automaticamente il dominio corrente
ENV REFLEX_BACKEND_PORT=8000
ENV API_URL=""

# 5. Copia i requisiti e installa le dipendenze Python
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copia tutto il codice sorgente
COPY . .

# 7. Crea cartella assets
RUN mkdir -p assets/images

# 8. COMPILAZIONE FRONTEND (la tua app è già configurata, non usare reflex init)

# Esporta il frontend in formato statico e sposta in /srv (opzionale, velocizza lo start)
RUN cd reflex_app && reflex export --frontend-only --no-zip || true

# Espone solo la porta 3000 (unico ingresso pubblico – Caddy)
EXPOSE 3000

# Forza la terminazione pulita al comando di stop
STOPSIGNAL SIGKILL

# 9. LOGGING CONFIGURATION
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 10. AVVIO: Backend + Frontend Reflex sulla porta 8000
CMD cd /app/reflex_app && exec reflex run --env prod
