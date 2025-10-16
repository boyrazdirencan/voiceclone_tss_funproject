#!/usr/bin/env python3
"""
Audio preprocessing script for voice cloning TTS system.
Converts audio files to 16kHz mono WAV format required by XTTS.
"""
import os
import argparse
from pathlib import Path
import librosa
import soundfile as sf


def convert_to_16k_mono(input_path, output_path):
    """
    Convert audio file to 16kHz mono WAV format.
    
    Args:
        input_path (str): Path to input audio file
        output_path (str): Path to output audio file
    """
    print(f"Converting {input_path} to 16kHz mono...")
    
    # Load audio file
    y, sr = librosa.load(input_path, sr=16000, mono=True)
    
    # Write to output file
    sf.write(output_path, y, sr, subtype='PCM_16')
    print(f"Saved to {output_path}")


def batch_convert(input_dir, output_dir):
    """
    Convert all audio files in input directory to 16kHz mono format.
    
    Args:
        input_dir (str): Directory containing input audio files
        output_dir (str): Directory to save converted audio files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported audio formats
    extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac', '.ogg']
    
    # Find all audio files
    audio_files = []
    for ext in extensions:
        audio_files.extend(input_path.glob(f'**/*{ext}'))
        audio_files.extend(input_path.glob(f'**/*{ext.upper()}'))
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files to convert")
    
    for audio_file in audio_files:
        # Create output filename
        output_file = output_path / f"{audio_file.stem}_16k_mono.wav"
        
        try:
            convert_to_16k_mono(str(audio_file), str(output_file))
        except Exception as e:
            print(f"Error converting {audio_file}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Preprocess audio files for voice cloning')
    parser.add_argument('input', help='Input audio file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory', required=True)
    parser.add_argument('--batch', action='store_true', help='Process all audio files in directory')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_convert(args.input, args.output)
    else:
        input_path = Path(args.input)
        if input_path.is_dir():
            print("Input is a directory. Use --batch flag to process all files in directory.")
        else:
            output_path = Path(args.output)
            convert_to_16k_mono(str(input_path), str(output_path))


if __name__ == '__main__':
    main()