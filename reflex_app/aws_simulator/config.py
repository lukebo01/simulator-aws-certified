"""Configurazione applicazione AWS Simulator."""
from __future__ import annotations

import os
from pathlib import Path

# Directories - Relativi a config.py
CONFIG_DIR = Path(__file__).parent  # aws_simulator/
PROJECT_ROOT = CONFIG_DIR.parent.parent  # reflex_app/
DATA_DIR = CONFIG_DIR / "data"  # aws_simulator/data/

# Debug
print(f"📍 config.py location: {__file__}")
print(f"📍 CONFIG_DIR: {CONFIG_DIR}")
print(f"📍 DATA_DIR: {DATA_DIR}")
print(f"📍 DATA_DIR exists: {DATA_DIR.exists()}")

# Configurazione esami disponibili
EXAMS = {
    "saa_c03": {
        "id": "saa_c03",
        "code": "SAA-C03",
        "name": "AWS Certified Solutions Architect - Associate",
        "speciality": "Solutions Architect",
        "level": "Associate",
        "icon": "/images/solution_architect_associate.png",
        "color": "#FF9900",
        "description": "Progettazione di architetture cloud scalabili e sicure",
        "price": "$150 USD",
        "duration": 130,  # minuti
        "duration_esl": 160,  # minuti con bonus ESL
        "questions": 65,
        "passing_score": 720,
        "max_score": 1000,
        "domains": [
            {"name": "Design Secure Architectures", "percentage": 30},
            {"name": "Design Resilient Architectures", "percentage": 26},
            {"name": "Design High-Performing Architectures", "percentage": 24},
            {"name": "Design Cost-Optimized Architectures", "percentage": 20},
        ],
    },
    "aip_c01": {
        "id": "aip_c01",
        "code": "AIP-C01",
        "name": "AWS Certified Generative AI Developer - Professional",
        "speciality": "Generative AI Developer",
        "level": "Professional",
        "icon": "/images/generative_ai_developer_professional.png",
        "color": "#FF9900",
        "description": "Sviluppo e implementazione di soluzioni AI generativa su AWS",
        "price": "$300 USD",
        "duration": 180,  # minuti
        "duration_esl": 210,  # minuti con bonus ESL
        "questions": 65,  # 65 conteggiate su 75 totali (10 non conteggiate)
        "passing_score": 750,
        "max_score": 1000,
        "domains": [
            {"name": "Model Integration & Compliance", "percentage": 31},
            {"name": "Implementation & Integration", "percentage": 26},
            {"name": "AI Safety & Security", "percentage": 20},
            {"name": "Operational Efficiency", "percentage": 12},
            {"name": "Testing & Troubleshooting", "percentage": 11},
        ],
    },
}

# Configurazione UI
THEME_COLOR = "#FF9900"
BACKGROUND_GRADIENT = "linear-gradient(135deg, #0a1428 0%, #1a2332 100%)"
