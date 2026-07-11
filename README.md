# AWS Exam Simulator

Web app Reflex **production-ready** per praticare gli esami di certificazione AWS. Simulatore interattivo con domande normalizzate da ExamTopics.

## 🎯 Features

✅ **2 Esami Certificazione AWS**
- AWS Solutions Architect - Associate (SAA-C03) → 897 domande
- AWS Certified AI Practitioner (AIP-C01) → 86 domande

✅ **Quiz Interattivo**
- Selezione esame con immagini badge
- Navigazione domande (avanti/indietro)
- Visualizzazione spiegazioni con risposta corretta
- Tracking punteggio in tempo reale
- Risultati finali con percentuale

✅ **Architecture Production-Ready**
- Reflex framework con state management
- Caddy reverse proxy (porta 3000)
- Backend Python isolato (porta 8000, localhost)
- Dockerfile per ECS Express mode
- Terraform-ready (future: deployment AWS)

✅ **Asset Management**
- Favicon.ico generato automaticamente
- Immagini badge esami (PNG)
- Struttura conforme a DIRE Client

## 📋 Struttura Progetto

```
simulator-aws-certified/
├── reflex_app/                          # Cartella app Reflex
│   ├── rxconfig.py                      # Config Reflex + favicon
│   ├── assets/
│   │   ├── favicon.ico                  # Icon scheda browser
│   │   └── images/
│   │       ├── icon.png                 # Favicon source
│   │       ├── solution_architect_associate.png
│   │       └── generative_ai_developer_professional.png
│   └── aws_simulator/
│       ├── aws_simulator.py             # Entry point
│       ├── config.py                    # Configurazione app
│       ├── state.py                     # Reflex state
│       └── pages/
│           ├── home.py                  # Selezione esami
│           └── quiz.py                  # Quiz interattiva
├── scripts/
│   ├── normalize_questions.py           # Markdown → JSON
│   └── convert_to_favicon.py            # PNG → ICO
├── data/
│   ├── raw/from_examtopics/
│   │   ├── aws_saa_c03.md               # Raw markdown
│   │   └── aws_aip_c01.md
│   └── json_normalized/
│       ├── aws_saa_c03.json             # 897 domande
│       └── aws_aip_c01.json             # 86 domande
├── Dockerfile                           # Production image
├── Caddyfile                            # Reverse proxy config
├── requirements.txt                     # Dipendenze Python
├── setup.sh                             # Setup automation
└── README.md                            # Questo file
```

## 🚀 Quick Start

### 1. Setup (Una volta)

```bash
cd /Users/lucaborrelli/Desktop/repositories/simulator-aws-certified
chmod +x setup.sh
./setup.sh
```

Output atteso:
```
📦 Installazione dipendenze...
✅ Dipendenze installate

📖 Normalizzazione domande...
✅ Salvato: aws_saa_c03.json (897 domande)
✅ Salvato: aws_aip_c01.json (86 domande)

🎨 Preparazione asset directory...
✅ Favicon creato

✨ Setup completato!
```

### 2. Avvio App

```bash
cd reflex_app
reflex run
```

L'app sarà disponibile su: **http://localhost:3000**

## 📖 Utilizzo

1. **Home**: Scegli tra i 2 esami disponibili
2. **Quiz**: 
   - Leggi la domanda
   - Seleziona risposta (A/B/C/D)
   - Clicca "Invia risposta"
   - Visualizza spiegazione + risposta corretta
   - Naviga avanti/indietro
3. **Risultati**: Score percentuale + num risposte corrette

## 🔧 Configurazione

### Aggiungere nuovi esami

1. Aggiungi file markdown in `data/raw/from_examtopics/aws_<codice>.md`
2. Aggiorna `reflex_app/aws_simulator/config.py`:

```python
EXAMS = {
    "tuo_codice": {
        "id": "tuo_codice",
        "code": "TUO-CODICE",
        "name": "Nome Esame",
        "speciality": "Specialità",
        "level": "Associate/Professional",
        "icon": "/images/tuo_icon.png",
        "description": "Descrizione",
    }
}
```

3. Esegui normalizzazione:

```bash
python3 scripts/normalize_questions.py
```

### Favicon custom

Se vuoi cambiare il favicon:

```bash
python3 scripts/convert_to_favicon.py assets/images/tuo_icon.png reflex_app/assets/favicon.ico
```

## 🐳 Docker Build & Deploy

### Build locale

```bash
docker build -t aws-simulator:latest .
docker run -it -p 3000:3000 aws-simulator:latest
```

### Deploy AWS ECS Express (Futuro)

```bash
# Build in CodeBuild (7GB+ RAM per compilare frontend)
# Push su ECR
# Deploy su Fargate con ALB
```

Vedi: `Dockerfile`, `Caddyfile`, futuri file `terraform/`

## 📊 Dati Domande

### Formato JSON normalizzato

```json
{
  "exam": "AWS Certified Solutions Architect - Associate (SAA-C03)",
  "exam_code": "SAA-C03",
  "total_questions": 897,
  "questions": [
    {
      "id": "aws_saa_c03-001",
      "number": 1,
      "topic": 1,
      "text": "A company collects data for temperature...",
      "options": {
        "A": "Turn on S3 Transfer Acceleration...",
        "B": "Upload the data from each site...",
        "C": "Schedule AWS Snowball Edge...",
        "D": "Upload the data from each site..."
      },
      "correct_answer": "A",
      "explanation": "S3 Transfer Acceleration provides...",
      "source": "ExamTopics",
      "timestamp": "2022-10-10"
    }
  ]
}
```

### Normalizzazione

Lo script `normalize_questions.py`:
- Parse markdown raw da ExamTopics
- Estrae domanda, opzioni, risposta, spiegazione
- Pulisce formattazione
- Output JSON interrogabile

## 🎨 UI/UX

**Colori AWS**:
- Orange: `#FF9900`
- Navy: `#0a1428`
- Light: `#f8f9fa`

**Font**: Inter (system font fallback)

**Layout**: Grid 2 colonne (responsive con Radix UI)

## 🔐 Security

- Backend isolato su localhost (8000)
- Caddy proxy su porta pubblica (3000)
- No API keys in frontend
- CSRF protection via Reflex framework

## 🚧 Roadmap

- [x] Setup struttura Reflex
- [x] Script normalizzazione markdown
- [x] Home con selezione esami
- [x] Quiz interattiva
- [x] Favicon + asset images
- [x] Dockerfile + Caddyfile
- [ ] ECS Express Terraform
- [ ] Analytics/Dashboard
- [ ] Export risultati PDF
- [ ] Dark mode
- [ ] Integrazione con backend AI

## 📝 Note

- I dati raw vengono normalizzati **una volta** con `scripts/normalize_questions.py`
- I JSON normalizzati sono stati committati e serviti da `data/json_normalized/`
- Il favicon è generato automaticamente da `icon.png` durante setup
- Tutte le immagini vanno in `reflex_app/assets/images/`

## 💡 Troubleshooting

**"Module not found: aws_simulator"**
```bash
# Assicurati di essere in reflex_app/
cd reflex_app
reflex run
```

**Immagini non caricate**
```bash
# Verifica che siano in reflex_app/assets/images/
ls reflex_app/assets/images/
# Riavvia reflex run
```

**Favicon non appare**
```bash
# Verifica che favicon.ico esista
ls reflex_app/assets/favicon.ico
# Hard refresh nel browser (Cmd+Shift+R su Mac)
```

## 📄 License

MIT
