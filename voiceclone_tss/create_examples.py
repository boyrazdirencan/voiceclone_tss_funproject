#!/usr/bin/env python3
"""
Example script to demonstrate voice clone TTS system usage.
"""
import os
from pathlib import Path

def create_example_texts():
    """Create example text files for demonstration."""
    texts_dir = Path("data/texts")
    texts_dir.mkdir(parents=True, exist_ok=True)
    
    examples = {
        "fr": "Bonjour, ceci est un exemple de texte en français pour le système TTS.",
        "de": "Hallo, dies ist ein Beispieltext in Deutsch für das TTS-System.",
        "es": "Hola, este es un ejemplo de texto en español para el sistema TTS.",
        "it": "Ciao, questo è un esempio di testo in italiano per il sistema TTS.",
        "sv": "Hej, detta är ett exempel på text på svenska för TTS-systemet.",
        "tr": "Merhaba, bu Türkçe TTS sistemi için örnek bir metindir."
    }
    
    for lang, text in examples.items():
        file_path = texts_dir / f"{lang}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Created example text for {lang}: {file_path}")

if __name__ == "__main__":
    print("Creating example text files...")
    create_example_texts()
    print("\nExample files created!")
    print("\nTo run the complete pipeline:")
    print("1. Place your reference audio in data/ref/direncan_ref.wav")
    print("2. Run: python scripts/batch_execute.py")
    print("\nTo run just synthesis with example texts:")
    print("python scripts/synthesize_tss_cli.py -t data/texts -r path/to/your/ref.wav -o outputs -l fr de es it sv tr")