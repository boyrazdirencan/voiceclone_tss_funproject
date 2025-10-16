#!/usr/bin/env python3
"""
Synthesis script for voice cloning TTS system using Coqui TTS CLI.
Processes multilingual text files with voice cloning using reference audio.
"""
import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
import time
from tqdm import tqdm


def run_tts_command(text, output_file, reference_audio, language='en'):
    """
    Run TTS CLI command for voice cloning.
    
    Args:
        text (str): Text to synthesize
        output_file (str): Output file path
        reference_audio (str): Reference audio file for voice cloning
        language (str): Language code
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Determine language code mapping for XTTS
    lang_map = {
        'en': 'en',
        'fr': 'fr',
        'de': 'de',
        'es': 'es',
        'it': 'it',
        'sv': 'sv',
        'tr': 'tr'
    }
    
    tts_lang = lang_map.get(language, 'en')
    
    # Build the TTS command
    cmd = [
        'tts',
        '--text', text,
        '--out_path', output_file,
        '--model_name', 'tts_models/multilingual/multi-dataset/xtts_v2',
        '--speaker_wav', reference_audio,
        '--language_idx', tts_lang
    ]
    
    print(f"Running TTS command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"Successfully generated: {output_file}")
            return True
        else:
            print(f"TTS command failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"TTS command timed out for: {output_file}")
        return False
    except Exception as e:
        print(f"Error running TTS command: {str(e)}")
        return False


def process_multilingual_text_files(texts_dir, reference_audio, output_dir, languages=None):
    """
    Process multiple text files for different languages using voice cloning.
    
    Args:
        texts_dir (str): Directory containing text files
        reference_audio (str): Reference audio file for voice cloning
        output_dir (str): Directory to save output files
        languages (list): List of language codes to process (if None, process all found)
    """
    texts_path = Path(texts_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # If languages not specified, find all .txt files in texts_dir
    if languages is None:
        txt_files = list(texts_path.glob('*.txt'))
        languages = []
        for txt_file in txt_files:
            # Extract language code from filename (e.g., 'fr.txt' -> 'fr')
            lang_code = txt_file.stem.split('.')[0]
            languages.append(lang_code)
    
    # Process each language
    successful_generations = 0
    total_generations = len(languages)
    
    for lang in tqdm(languages, desc="Processing languages"):
        text_file_path = texts_path / f"{lang}.txt"
        
        if not text_file_path.exists():
            print(f"Warning: Text file {text_file_path} does not exist, skipping...")
            continue
        
        # Read the text
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        if not text:
            print(f"Warning: Text file {text_file_path} is empty, skipping...")
            continue
        
        # Generate output filename
        output_file = output_path / f"{lang}_direncan.wav"
        
        # Run TTS for each text chunk
        text_chunks = text.split('\n\n')  # Split by paragraphs
        chunk_outputs = []
        
        for i, chunk in enumerate(text_chunks):
            chunk = chunk.strip()
            if not chunk:
                continue
            
            # Generate unique filename for this chunk
            chunk_output = output_path / f"{lang}_direncan_chunk_{i+1}.wav"
            
            success = run_tts_command(chunk, str(chunk_output), reference_audio, lang)
            if success:
                chunk_outputs.append(str(chunk_output))
            else:
                print(f"Failed to generate chunk {i+1} for language {lang}")
        
        # If we have multiple chunks, we might want to concatenate them
        if len(chunk_outputs) > 1:
            final_output = output_path / f"{lang}_direncan.wav"
            concatenate_wav_files(chunk_outputs, str(final_output))
            
            # Remove individual chunks
            for chunk_file in chunk_outputs:
                os.remove(chunk_file)
            
            print(f"Combined chunks into: {final_output}")
        elif len(chunk_outputs) == 1:
            # Rename single chunk to final output
            final_output = output_path / f"{lang}_direncan.wav"
            os.rename(chunk_outputs[0], str(final_output))
            print(f"Generated: {final_output}")
    
    print(f"Completed! Generated {successful_generations}/{total_generations} languages")


def concatenate_wav_files(input_files, output_file):
    """
    Concatenate multiple WAV files into a single file using ffmpeg.
    
    Args:
        input_files (list): List of input WAV files
        output_file (str): Output WAV file
    """
    # Create a temporary file list for ffmpeg
    list_file = output_file + "_list.txt"
    with open(list_file, 'w') as f:
        for file in input_files:
            f.write(f"file '{file}'\n")
    
    # Run ffmpeg to concatenate
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file,
        '-c', 'copy',
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"FFmpeg concatenation failed: {result.stderr}")
    except Exception as e:
        print(f"Error concatenating WAV files: {str(e)}")
    finally:
        # Remove the temporary list file
        if os.path.exists(list_file):
            os.remove(list_file)


def check_tts_installation():
    """
    Check if TTS is installed and available.
    
    Returns:
        bool: True if TTS is available, False otherwise
    """
    try:
        # First try the command line version
        result = subprocess.run(['tts', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    
    # If command line fails, try importing the Python API
    try:
        from TTS.api import TTS
        return True
    except ImportError:
        return False


def main():
    parser = argparse.ArgumentParser(description='Synthesize multilingual speech using voice cloning')
    parser.add_argument('-t', '--texts-dir', help='Directory containing text files', required=True)
    parser.add_argument('-r', '--reference-audio', help='Reference audio file for voice cloning', required=True)
    parser.add_argument('-o', '--output-dir', help='Directory to save output files', required=True)
    parser.add_argument('-l', '--languages', nargs='+', help='List of language codes to process (e.g., fr de es it sv tr)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be processed without running TTS')
    
    args = parser.parse_args()
    
    # Check if TTS is installed
    if not check_tts_installation():
        print("Error: TTS is not installed or not available in PATH.")
        print("Please install Coqui TTS using: pip install coqui-tts")
        sys.exit(1)
    
    # Validate reference audio
    ref_path = Path(args.reference_audio)
    if not ref_path.exists():
        print(f"Error: Reference audio file does not exist: {args.reference_audio}")
        sys.exit(1)
    
    # Validate texts directory
    texts_path = Path(args.texts_dir)
    if not texts_path.exists():
        print(f"Error: Texts directory does not exist: {args.texts_dir}")
        sys.exit(1)
    
    if args.dry_run:
        print("DRY RUN MODE:")
        print(f"Texts directory: {args.texts_dir}")
        print(f"Reference audio: {args.reference_audio}")
        print(f"Output directory: {args.output_dir}")
        
        if args.languages:
            print(f"Languages to process: {args.languages}")
        else:
            txt_files = list(texts_path.glob('*.txt'))
            languages = [f.stem for f in txt_files]
            print(f"Languages to process (from text files): {languages}")
        
        return
    
    # Process the texts
    process_multilingual_text_files(
        args.texts_dir,
        args.reference_audio,
        args.output_dir,
        args.languages
    )


if __name__ == '__main__':
    main()