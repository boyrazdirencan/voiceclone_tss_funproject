#!/usr/bin/env python3
"""
Text preparation utilities for multilingual TTS system.
Handles text cleaning, punctuation, and language-specific formatting.
"""
import re
import os
from pathlib import Path
import argparse


def clean_text(text, language='en'):
    """
    Clean and prepare text for TTS based on language.
    
    Args:
        text (str): Input text to clean
        language (str): Language code for language-specific processing
        
    Returns:
        str: Cleaned text
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Language-specific processing
    if language in ['fr']:  # French
        # Handle French-specific punctuation
        text = re.sub(r'\s+([?!:;])', r'\1', text)
        text = re.sub(r'([«»])\s*', r'\1', text)
    elif language in ['de']:  # German
        # Handle German-specific processing
        pass
    elif language in ['es']:  # Spanish
        # Handle Spanish-specific punctuation
        text = re.sub(r'\s+([¡¿?!])', r'\1', text)
    elif language in ['it']:  # Italian
        # Handle Italian-specific processing
        pass
    elif language in ['sv']:  # Swedish
        # Handle Swedish-specific processing
        pass
    elif language in ['tr']:  # Turkish
        # Handle Turkish-specific processing
        pass
    
    return text


def split_text_by_paragraphs(text, max_length=200):
    """
    Split text into paragraphs or sentences of appropriate length for TTS.
    
    Args:
        text (str): Input text
        max_length (int): Maximum length of text chunks
        
    Returns:
        list: List of text chunks
    """
    # Split by paragraphs first
    paragraphs = text.split('\n')
    
    chunks = []
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # If paragraph is too long, split into sentences
        if len(paragraph) > max_length:
            # Split by sentence endings
            sentences = re.split(r'[.!?]+', paragraph)
            current_chunk = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current_chunk + " " + sentence) <= max_length:
                    if current_chunk:
                        current_chunk += ". " + sentence
                    else:
                        current_chunk = sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        else:
            chunks.append(paragraph)
    
    # Filter out empty chunks
    chunks = [chunk for chunk in chunks if chunk.strip()]
    return chunks


def prepare_text_file(input_path, output_path, language='en', max_length=200):
    """
    Prepare a text file for TTS by cleaning and splitting into chunks.
    
    Args:
        input_path (str): Path to input text file
        output_path (str): Path to output text file
        language (str): Language code
        max_length (int): Maximum length of text chunks
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Clean the text
    cleaned_text = clean_text(text, language)
    
    # Split into chunks
    chunks = split_text_by_paragraphs(cleaned_text, max_length)
    
    # Write to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, chunk in enumerate(chunks):
            f.write(f"{chunk}\n\n")
    
    print(f"Prepared text file: {input_path} -> {output_path}")
    print(f"Created {len(chunks)} text chunks")


def batch_prepare_texts(input_dir, output_dir, language='en', max_length=200):
    """
    Prepare all text files in input directory.
    
    Args:
        input_dir (str): Directory containing input text files
        output_dir (str): Directory to save prepared text files
        language (str): Language code
        max_length (int): Maximum length of text chunks
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all text files
    text_files = list(input_path.glob('*.txt'))
    
    if not text_files:
        print(f"No text files found in {input_dir}")
        return
    
    print(f"Found {len(text_files)} text files to prepare")
    
    for text_file in text_files:
        output_file = output_path / f"{text_file.stem}_prepared.txt"
        prepare_text_file(str(text_file), str(output_file), language, max_length)


def create_multilingual_texts(base_text, languages, output_dir):
    """
    Create text files for multiple languages (placeholder for translation).
    
    Args:
        base_text (str): Base text to be used for all languages
        languages (list): List of language codes
        output_dir (str): Directory to save text files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for lang in languages:
        output_file = output_path / f"{lang}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(base_text)
        print(f"Created text file for {lang}: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Prepare text files for multilingual TTS')
    parser.add_argument('input', help='Input text file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory', required=True)
    parser.add_argument('-l', '--language', help='Language code (e.g., en, fr, de, es, it, sv, tr)', default='en')
    parser.add_argument('--max-length', help='Maximum length of text chunks', type=int, default=200)
    parser.add_argument('--batch', action='store_true', help='Process all text files in directory')
    parser.add_argument('--create-multilingual', nargs='+', help='Create multilingual text files from base text')
    
    args = parser.parse_args()
    
    if args.create_multilingual:
        # Create multilingual text files
        base_text_path = Path(args.input)
        if base_text_path.is_file():
            with open(base_text_path, 'r', encoding='utf-8') as f:
                base_text = f.read()
            create_multilingual_texts(base_text, args.create_multilingual, args.output)
        else:
            print("Input must be a file when using --create-multilingual")
    elif args.batch:
        batch_prepare_texts(args.input, args.output, args.language, args.max_length)
    else:
        input_path = Path(args.input)
        if input_path.is_dir():
            print("Input is a directory. Use --batch flag to process all files in directory.")
        else:
            output_path = Path(args.output)
            prepare_text_file(str(input_path), str(output_path), args.language, args.max_length)


if __name__ == '__main__':
    main()