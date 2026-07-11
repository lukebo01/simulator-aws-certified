#!/usr/bin/env python3
"""
Converti PNG/SVG in favicon.ico

Usa Pillow per convertire un'immagine in favicon.ico di varie dimensioni.
"""

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Pillow non installato. Installa con: pip install Pillow")
    sys.exit(1)


def convert_png_to_favicon(png_path: str, output_path: str = None):
    """Converti un PNG in favicon.ico con varie dimensioni."""
    
    png_file = Path(png_path)
    if not png_file.exists():
        print(f"❌ File non trovato: {png_path}")
        return False
    
    if output_path is None:
        output_path = png_file.parent / "favicon.ico"
    else:
        output_path = Path(output_path)
    
    try:
        print(f"📂 Apro immagine: {png_file}")
        img = Image.open(png_file).convert("RGBA")
        
        # Ridimensiona a 256x256 (favicon standard)
        img = img.resize((256, 256), Image.Resampling.LANCZOS)
        
        # Crea varie dimensioni per il favicon
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icon_sizes = []
        
        for size in sizes:
            icon = img.resize(size, Image.Resampling.LANCZOS)
            icon_sizes.append(icon)
        
        # Salva come ICO
        print(f"🎨 Creazione favicon con dimensioni: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
        img.save(output_path, format="ICO", sizes=sizes)
        
        print(f"✅ Favicon salvato: {output_path}")
        return True
    
    except Exception as e:
        print(f"❌ Errore durante la conversione: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilizzo: python3 convert_to_favicon.py <png_file> [output_ico_file]")
        print("")
        print("Esempio:")
        print("  python3 convert_to_favicon.py assets/images/icon.png reflex_app/assets/favicon.ico")
        sys.exit(1)
    
    png_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_png_to_favicon(png_path, output_path)
    sys.exit(0 if success else 1)
