#!/usr/bin/env python3
"""
Post-processing script for TTS audio output.
Applies normalization, fades, and format conversion to enhance audio quality.
"""
import os
import argparse
from pathlib import Path
import subprocess
from pydub import AudioSegment
import numpy as np
from tqdm import tqdm


def normalize_audio(input_file, output_file, target_dBFS=-20.0):
    """
    Normalize audio to target loudness.
    
    Args:
        input_file (str): Input audio file path
        output_file (str): Output audio file path
        target_dBFS (float): Target loudness in dBFS
    """
    audio = AudioSegment.from_file(input_file)
    change_in_dBFS = target_dBFS - audio.dBFS
    normalized = audio.apply_gain(change_in_dBFS)
    normalized.export(output_file, format="wav")
    print(f"Normalized: {input_file} -> {output_file}")


def add_fade_in_out(input_file, output_file, fade_duration=1000):
    """
    Add fade-in and fade-out effects to audio.
    
    Args:
        input_file (str): Input audio file path
        output_file (str): Output audio file path
        fade_duration (int): Duration of fade in milliseconds
    """
    audio = AudioSegment.from_file(input_file)
    faded_audio = audio.fade_in(fade_duration).fade_out(fade_duration)
    faded_audio.export(output_file, format="wav")
    print(f"Added fade effects: {input_file} -> {output_file}")


def remove_silence(input_file, output_file, silence_thresh=-40.0, min_silence_len=1000):
    """
    Remove silence from audio.
    
    Args:
        input_file (str): Input audio file path
        output_file (str): Output audio file path
        silence_thresh (float): Silence threshold in dB
        min_silence_len (int): Minimum silence length in milliseconds
    """
    audio = AudioSegment.from_file(input_file)
    
    # Split on silence
    chunks = audio.split_silence(
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=0
    )
    
    # Combine non-silent chunks
    if chunks:
        combined = sum(chunks)
        combined.export(output_file, format="wav")
        print(f"Removed silence: {input_file} -> {output_file}")
    else:
        # If all silence, just copy the file
        audio.export(output_file, format="wav")
        print(f"Audio is mostly silence, copied as is: {input_file} -> {output_file}")


def convert_format(input_file, output_file, format="mp3", bitrate="192k"):
    """
    Convert audio to different format.
    
    Args:
        input_file (str): Input audio file path
        output_file (str): Output audio file path
        format (str): Output format (mp3, wav, etc.)
        bitrate (str): Audio bitrate
    """
    # Use pydub to convert
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format=format, bitrate=bitrate)
    print(f"Converted format: {input_file} -> {output_file}")


def batch_process(input_dir, output_dir, operations):
    """
    Apply post-processing operations to all audio files in a directory.
    
    Args:
        input_dir (str): Input directory
        output_dir (str): Output directory
        operations (list): List of operations to apply
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all audio files
    audio_files = list(input_path.glob('*.wav')) + list(input_path.glob('*.mp3'))
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files to process")
    
    for audio_file in tqdm(audio_files, desc="Post-processing"):
        # Apply operations in sequence
        current_file = str(audio_file)
        
        for i, operation in enumerate(operations):
            if i == 0:
                # First operation uses original file
                next_file = str(output_path / f"{audio_file.stem}_processed.wav")
            elif i == len(operations) - 1:
                # Last operation uses final output name
                next_file = str(output_path / audio_file.name)
            else:
                # Intermediate operations use temporary names
                next_file = str(output_path / f"{audio_file.stem}_temp_{i}.wav")
            
            if operation['type'] == 'normalize':
                normalize_audio(current_file, next_file, operation.get('target_dBFS', -20.0))
            elif operation['type'] == 'fade':
                add_fade_in_out(current_file, next_file, operation.get('fade_duration', 1000))
            elif operation['type'] == 'remove_silence':
                remove_silence(current_file, next_file, operation.get('silence_thresh', -40.0), operation.get('min_silence_len', 1000))
            elif operation['type'] == 'convert_format':
                convert_format(current_file, next_file, operation.get('format', 'mp3'), operation.get('bitrate', '192k'))
            
            # Update current file for next operation
            current_file = next_file


def main():
    parser = argparse.ArgumentParser(description='Post-process TTS audio output')
    parser.add_argument('input', help='Input audio file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory', required=True)
    
    # Add arguments for different operations
    parser.add_argument('--normalize', action='store_true', help='Normalize audio loudness')
    parser.add_argument('--normalize-target', type=float, default=-20.0, help='Target loudness in dBFS (default: -20.0)')
    
    parser.add_argument('--fade', action='store_true', help='Add fade-in and fade-out')
    parser.add_argument('--fade-duration', type=int, default=1000, help='Fade duration in ms (default: 1000)')
    
    parser.add_argument('--remove-silence', action='store_true', help='Remove silence from audio')
    parser.add_argument('--silence-thresh', type=float, default=-40.0, help='Silence threshold in dB (default: -40.0)')
    parser.add_argument('--min-silence-len', type=int, default=1000, help='Minimum silence length in ms (default: 1000)')
    
    parser.add_argument('--convert-format', help='Convert to format (mp3, wav, etc.)')
    parser.add_argument('--bitrate', default='192k', help='Bitrate for output format (default: 192k)')
    
    parser.add_argument('--batch', action='store_true', help='Process all audio files in directory')
    
    args = parser.parse_args()
    
    # Build operations list based on arguments
    operations = []
    
    if args.normalize:
        operations.append({
            'type': 'normalize',
            'target_dBFS': args.normalize_target
        })
    
    if args.fade:
        operations.append({
            'type': 'fade',
            'fade_duration': args.fade_duration
        })
    
    if args.remove_silence:
        operations.append({
            'type': 'remove_silence',
            'silence_thresh': args.silence_thresh,
            'min_silence_len': args.min_silence_len
        })
    
    if args.convert_format:
        operations.append({
            'type': 'convert_format',
            'format': args.convert_format,
            'bitrate': args.bitrate
        })
    
    if not operations:
        print("No operations specified. Use --normalize, --fade, --remove-silence, or --convert-format.")
        return
    
    input_path = Path(args.input)
    
    if args.batch:
        batch_process(str(input_path), args.output, operations)
    else:
        if input_path.is_dir():
            print("Input is a directory. Use --batch flag to process all files in directory.")
        else:
            # Apply operations sequentially to single file
            current_file = str(input_path)
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            for i, operation in enumerate(operations):
                if i == len(operations) - 1:
                    # Last operation uses final output name
                    next_file = args.output
                else:
                    # Intermediate operations use temporary names
                    next_file = str(output_path.parent / f"{output_path.stem}_temp.wav")
                
                if operation['type'] == 'normalize':
                    normalize_audio(current_file, next_file, operation.get('target_dBFS', -20.0))
                elif operation['type'] == 'fade':
                    add_fade_in_out(current_file, next_file, operation.get('fade_duration', 1000))
                elif operation['type'] == 'remove_silence':
                    remove_silence(current_file, next_file, operation.get('silence_thresh', -40.0), operation.get('min_silence_len', 1000))
                elif operation['type'] == 'convert_format':
                    convert_format(current_file, next_file, operation.get('format', 'mp3'), operation.get('bitrate', '192k'))
                
                # Update current file for next operation
                current_file = next_file


if __name__ == '__main__':
    main()