# Voice Clone TTS System (VoiceClone-TSS)

A complete system for multilingual text-to-speech using voice cloning technology with Coqui TTS. This system allows you to generate speech in multiple languages (FR/DE/ES/IT/TR + 11 other languages) using your own voice as a reference.

**Note**: Swedish (SV) is not supported by the XTTS v2 model used in this system.

## Features

- Voice cloning using Coqui TTS XTTS v2 model
- Multilingual support for 16 languages including French, German, Spanish, Italian, Turkish, Portuguese, Polish, Russian, Dutch, Czech, Arabic, Chinese, Hungarian, Korean, Japanese, and Hindi
- Audio preprocessing for optimal voice cloning
- Text preparation and cleaning for multiple languages
- Batch processing capabilities
- Post-processing for enhanced audio quality
- Comprehensive logging and reporting

## Prerequisites

- Python 3.8+
- Coqui TTS installed: `pip install coqui-tts`
- FFmpeg for audio processing: `brew install ffmpeg` (macOS) or equivalent for your system

## Project Structure

```
voiceclone_tss/
├─ data/
│  ├─ ref/                     # Node-1: reference audio (.wav, 16k mono)
│  │  └─ direncan_ref.wav
│  ├─ texts/                   # Node-2: multilingual texts
│  │  ├─ fr.txt  de.txt  es.txt  it.txt  tr.txt  # (sv.txt not supported by XTTS)
│  └─ prompts/                 # (optional) emotion/tempo notes
├─ outputs/                    # Node-5/6: generated wav/mp3
├─ scripts/
│  ├─ preprocess_audio.py      # 16k mono conversion
│  ├─ text_preparation.py      # Text cleaning and preparation
│  ├─ synthesize_tss_cli.py    # TTS CLI batch synthesis
│  ├─ post_process.py          # Audio enhancement
│  └─ batch_execute.py         # Complete pipeline execution
├─ env/
│  └─ requirements.txt         # Python dependencies
├─ config.json                 # Configuration file
├─ create_examples.py          # Sample text creation script
├─ tts_runner.sh               # Convenience wrapper script
└─ README.md
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r env/requirements.txt
   # Install Coqui TTS (if not already installed)
   pip install coqui-tts
   ```

2. **Prepare Reference Audio**
   - Place a 30-90 second clean audio sample of your voice in `data/ref/direncan_ref.wav`
   - The audio should be in 16kHz mono WAV format
   - Use the preprocessing script to convert if needed:
   ```bash
   python scripts/preprocess_audio.py path/to/your/audio.wav -o data/ref/direncan_ref.wav
   ```

3. **Prepare Text Files**
   - Create text files for each language in `data/texts/`:
     - `fr.txt` - French text
     - `de.txt` - German text
     - `es.txt` - Spanish text
     - `it.txt` - Italian text
     - `sv.txt` - Swedish text
     - `tr.txt` - Turkish text

## Usage

### 1. Audio Preprocessing

Convert audio files to 16kHz mono WAV format:

```bash
# Single file
python scripts/preprocess_audio.py input.wav -o output.wav

# Batch processing
python scripts/preprocess_audio.py input_dir -o output_dir --batch
```

### 2. Text Preparation

Prepare text files for TTS:

```bash
# Single file
python scripts/text_preparation.py input.txt -o output.txt -l fr

# Batch processing
python scripts/text_preparation.py input_dir -o output_dir --batch -l fr

# Create multilingual text files from a base text
python scripts/text_preparation.py base_text.txt -o data/texts --create-multilingual fr de es it sv tr
```

### 3. Synthesis (TTS)

Generate speech using voice cloning:

```bash
# Generate for specific languages (sv not supported by XTTS model)
python scripts/synthesize_tss_cli.py -t data/texts -r data/ref/direncan_ref.wav -o outputs -l fr de es it tr

# Generate for all available languages (using config.json)
python scripts/synthesize_tss_cli.py -t data/texts -r data/ref/direncan_ref.wav -o outputs
```

### 4. Post-Processing

Enhance generated audio:

```bash
# Single file
python scripts/post_process.py input.wav -o output.wav --normalize --fade

# Batch processing
python scripts/post_process.py inputs/ -o outputs/ --batch --normalize --fade
```

### 5. Complete Pipeline (Recommended)

Run the entire pipeline with one command:

```bash
# Run complete pipeline
python scripts/batch_execute.py

# Run with custom parameters
python scripts/batch_execute.py \
  -r data/ref/direncan_ref.wav \
  -t data/texts \
  -o outputs \
  -l fr de es it tr

# Dry run (see what would be executed)
python scripts/batch_execute.py --dry-run
```

## Configuration

The system uses a `config.json` file for configuration. Default configuration:

```json
{
  "reference_audio": "data/ref/direncan_ref.wav",
  "texts_dir": "data/texts",
  "output_dir": "outputs",
  "languages": ["fr", "de", "es", "it", "tr"],
  "preprocessing": {
    "normalize": true,
    "target_dBFS": -20.0,
    "fade": true,
    "fade_duration": 1000
  }
}
```

## Supported Languages

The XTTS v2 model supports voice cloning in the following languages:
- French (`fr`) ✅
- German (`de`) ✅
- Spanish (`es`) ✅
- Italian (`it`) ✅
- Turkish (`tr`) ✅
- Portuguese (`pt`)
- Polish (`pl`)
- Russian (`ru`)
- Dutch (`nl`)
- Czech (`cs`)
- Arabic (`ar`)
- Chinese (`zh-cn`)
- Hungarian (`hu`)
- Korean (`ko`)
- Japanese (`ja`)
- Hindi (`hi`)

**Note**: Swedish (`sv`) is not supported by the XTTS v2 model and will result in an error if attempted.

## Output Files

Generated audio files will be in the outputs directory with names like:
- `fr_direncan.wav` - French speech in your voice
- `de_direncan.wav` - German speech in your voice
- `es_direncan.wav` - Spanish speech in your voice
- `it_direncan.wav` - Italian speech in your voice
- `tr_direncan.wav` - Turkish speech in your voice

## Troubleshooting

1. **Model not found**: On first run, the XTTS v2 model will be downloaded automatically
2. **Audio quality issues**: Ensure your reference audio is 16kHz mono WAV format and contains clear speech
3. **Memory issues**: The XTTS model is memory-intensive; ensure sufficient RAM (16GB+ recommended)
4. **Language support**: Swedish (sv) is not supported by the XTTS v2 model and will result in an error. Supported languages include: fr, de, es, it, tr, pt, pl, ru, nl, cs, ar, zh-cn, hu, ko, ja, hi 

## Performance Notes

- First-time generation for each language may take longer due to model loading
- Processing time depends on text length and hardware specifications
- Generated audio quality depends on quality of reference audio
- The system has been tested and verified to work with: French (fr), German (de), Spanish (es), Italian (it), and Turkish (tr)

## License

This project is free to use for personal purposes only.

## Note

This program uses only free and open-source resources. Therefore, the output quality depends on the microphone recording quality and the quality of the packages used.

## Disclaimer

This project and its components are provided for entertainment purposes only. The responsibility for the usage of this system lies solely with the individuals using it. The creators of this project are not responsible for how the system is used or any consequences that may result from its use.