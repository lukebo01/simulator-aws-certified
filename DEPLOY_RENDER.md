# Deploy su Render (Alternativa Gratuita)

Render offre un piano **gratuito** ideale per hostare app Reflex con Python backend attivo.

## Prerequisiti

1. **GitHub Repository**: Il tuo codice deve essere su GitHub
2. **Render Account**: Registrati gratuitamente su [render.com](https://render.com)
3. **Environment Variables**: Prepara le variabili di ambiente necessarie

## Passi di Deploy

### 1. Push su GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Crea un Web Service su Render

1. Accedi a [dashboard.render.com](https://dashboard.render.com)
2. Clicca su **"New +"** → **"Web Service"**
3. Connetti il tuo repository GitHub
4. Seleziona il repo `simulator-aws-certified`

### 3. Configura il Web Service

**Nome del servizio**: `aws-simulator`

**Build Command**:
```bash
pip install --upgrade pip setuptools wheel &&
pip install -r requirements.txt &&
cd reflex_app &&
reflex init &&
reflex export --frontend-only --no-zip
```

**Start Command**:
```bash
cd reflex_app && reflex run --env prod
```

**Istanza**: Free Plan (512 MB RAM, 0.5 CPU)

**Port**: `8000`

### 4. Environment Variables

Clicca su **"Environment"** e aggiungi:

| Key | Value |
|-----|-------|
| `REFLEX_ENV` | `prod` |
| `PYTHONUNBUFFERED` | `1` |

Se usi un database esterno:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `(URL del tuo database)` |

### 5. Deploy Automatico

- Render effettuerà il **deploy automatico** ad ogni push su GitHub
- Visualizza i log su Render Dashboard → **"Logs"**

---

## Caratteristiche del Piano Free

✅ **Include**:
- 750 ore/mese di compute (gratuito)
- Auto-deploy da GitHub
- HTTPS gratuito
- Cronologia dei deploy di 24 ore

❌ **Limitazioni**:
- L'app si mette in pausa dopo 15 minuti di inattività
- Database (se aggiunto) richiede piano a pagamento
- La prima riattivazione dopo pausa può richiedere ~30 sec

---

## Alternative a Render

Se Render non soddisfa le tue esigenze:

| Servizio | Costo Base | Vantaggi |
|----------|-----------|----------|
| **Vercel** | Gratuito | Ottimo per frontend, ma backend limitato |
| **Railway** | ~$5/mese | Generoso con free trial iniziale |
| **Replit** | Gratuito | Semplice, ma performance limitata |
| **PythonAnywhere** | ~$5/mese | Specifico per Python |
| **Heroku** | €7/mese (dopo free tier) | Storico standard, ma ora a pagamento |

---

## Troubleshooting

### Build fallisce: "reflex: command not found"

Assicurati che il build command sia:
```bash
pip install -r requirements.txt &&
cd reflex_app &&
reflex init
```

### App mostra errore 502 Bad Gateway

- Controlla i **Logs** su Render
- Verifica che la porta sia configurata come `8000`
- Riavvia il servizio: Dashboard → Restart

### Database non connesso

Se usi un database esterno:
1. Aggiungi la `DATABASE_URL` negli Environment Variables
2. Assicurati che sia raggiungibile da Render (firewall)
3. Usa un servizio database cloud (Supabase, MongoDB Atlas, etc.)

---

## Configurazione `render.yaml`

Render supporta anche il file `render.yaml` nella root del progetto. Consulta `render.yaml` per la configurazione automatica.

```yaml
services:
  - type: web
    name: aws-simulator
    env: python
    runtime: python-3.11
    buildCommand: pip install -r requirements.txt && cd reflex_app && reflex init
    startCommand: cd reflex_app && reflex run --env prod
    port: 8000
```

---

## Accesso all'App Deployata

Una volta completato il deploy:

**URL**: `https://aws-simulator.onrender.com` (il nome varia)

Visualizza il link su Render Dashboard sotto **"Settings"** → **"Render URL"**

---

## Monitoraggio e Logs

- Clicca su **"Logs"** nel dashboard per vedere i log in tempo reale
- Usa `PYTHONUNBUFFERED=1` per log immediati (già configurato)
- Se l'app non parte, controlla i log per errori

---

## Prossimi Passi

1. ✅ Deploy completato
2. 📊 Monitora performance e usage
3. 💾 Se necessario, aggiungi un database (Supabase, Railway, etc.)
4. 🔐 Configura variabili di ambiente sensibili

Enjoy! 🚀
