#!/bin/bash
# Setup script per AWS Simulator

set -e

echo "🚀 AWS Exam Simulator - Setup"
echo "=============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato"
    exit 1
fi

echo "✅ Python3 trovato: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installazione dipendenze..."
pip3 install -r requirements.txt
echo "✅ Dipendenze installate"
echo ""

# Normalize questions
echo "📖 Normalizzazione domande..."
python3 scripts/normalize_questions.py
echo ""

# Create and copy assets
echo "🎨 Preparazione asset directory..."
mkdir -p reflex_app/assets/images

# Copia le immagini da assets/images a reflex_app/assets/images
if [ -d "assets/images" ]; then
    cp -v assets/images/*.svg reflex_app/assets/images/ 2>/dev/null || true
    echo "✅ SVG copiate in reflex_app/assets/images"
fi

# Converti icon.png in favicon.ico se esiste
if [ -f "assets/images/icon.png" ]; then
    echo "🎨 Conversione icon.png → favicon.ico..."
    python3 scripts/convert_to_favicon.py assets/images/icon.png reflex_app/assets/favicon.ico
    echo "✅ Favicon creato"
elif [ -f "assets/images/favicon.ico" ]; then
    echo "📋 favicon.ico già presente"
    cp -v assets/images/favicon.ico reflex_app/assets/ 2>/dev/null || true
else
    echo "⚠️  icon.png o favicon.ico non trovato in assets/images/"
    echo "   Aggiungilo e riesegui questo script"
fi

echo ""
echo "✨ Setup completato!"
echo ""
echo "Prossimi step:"
echo "1. Esegui: cd reflex_app && reflex run"
echo ""


