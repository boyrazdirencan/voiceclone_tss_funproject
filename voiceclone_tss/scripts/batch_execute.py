#!/usr/bin/env python3
"""
Batch execution and logging system for voice cloning TTS workflow.
Manages the complete pipeline: preprocessing, synthesis, post-processing.
"""
import os
import sys
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import subprocess
import time


# Set up logging
def setup_logging(log_dir='logs'):
    """Set up logging configuration."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_path / f"tts_pipeline_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file


def run_command(cmd, description, timeout=300):
    """
    Run a command with timeout and logging.
    
    Args:
        cmd (list): Command to run
        description (str): Description for logging
        timeout (int): Timeout in seconds
        
    Returns:
        tuple: (success: bool, output: str, error: str)
    """
    logging.info(f"Running: {description}")
    logging.info(f"Command: {' '.join(cmd)}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        end_time = time.time()
        
        elapsed = end_time - start_time
        logging.info(f"Command completed in {elapsed:.2f}s")
        
        if result.returncode == 0:
            logging.info(f"SUCCESS: {description}")
            return True, result.stdout, result.stderr
        else:
            logging.error(f"FAILED: {description}")
            logging.error(f"Return code: {result.returncode}")
            logging.error(f"Error: {result.stderr}")
            return False, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        logging.error(f"TIMEOUT: {description} (timeout after {timeout}s)")
        return False, "", f"Command timed out after {timeout}s"
    except Exception as e:
        logging.error(f"ERROR: {description} - {str(e)}")
        return False, "", str(e)


def load_config(config_file):
    """
    Load configuration from JSON file.
    
    Args:
        config_file (str): Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Return default configuration
        return {
            "reference_audio": "data/ref/direncan_ref.wav",
            "texts_dir": "data/texts",
            "output_dir": "outputs",
            "languages": ["fr", "de", "es", "it", "sv", "tr"],
            "preprocessing": {
                "normalize": True,
                "target_dBFS": -20.0,
                "fade": True,
                "fade_duration": 1000
            }
        }


def run_preprocessing(ref_audio, output_dir):
    """
    Run audio preprocessing.
    
    Args:
        ref_audio (str): Reference audio file
        output_dir (str): Output directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    ref_path = Path(ref_audio)
    if not ref_path.exists():
        logging.error(f"Reference audio does not exist: {ref_audio}")
        return False
    
    # For now, just validate the reference audio
    logging.info(f"Validated reference audio: {ref_audio}")
    return True


def run_text_preparation(texts_dir, languages):
    """
    Run text preparation.
    
    Args:
        texts_dir (str): Texts directory
        languages (list): List of languages
        
    Returns:
        bool: True if successful, False otherwise
    """
    texts_path = Path(texts_dir)
    if not texts_path.exists():
        logging.error(f"Texts directory does not exist: {texts_dir}")
        return False
    
    success = True
    for lang in languages:
        text_file = texts_path / f"{lang}.txt"
        if not text_file.exists():
            logging.warning(f"Text file not found: {text_file}")
            success = False
        else:
            logging.info(f"Found text file for {lang}: {text_file}")
    
    return success


def run_synthesis(texts_dir, ref_audio, output_dir, languages):
    """
    Run synthesis using the TTS CLI script.
    
    Args:
        texts_dir (str): Texts directory
        ref_audio (str): Reference audio file
        output_dir (str): Output directory
        languages (list): List of languages
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_path = Path(__file__).parent / "scripts" / "synthesize_tss_cli.py"
    
    cmd = [
        sys.executable,
        str(script_path),
        '--texts-dir', texts_dir,
        '--reference-audio', ref_audio,
        '--output-dir', output_dir
    ]
    
    if languages:
        cmd.extend(['--languages'] + languages)
    
    success, stdout, stderr = run_command(
        cmd,
        f"TTS synthesis for languages: {', '.join(languages)}",
        timeout=3600  # 1 hour timeout for synthesis
    )
    
    return success


def run_post_processing(output_dir, config):
    """
    Run post-processing on generated audio files.
    
    Args:
        output_dir (str): Output directory with generated audio
        config (dict): Configuration dictionary
        
    Returns:
        bool: True if successful, False otherwise
    """
    script_path = Path(__file__).parent / "scripts" / "post_process.py"
    
    # Build command based on config
    cmd = [
        sys.executable,
        str(script_path),
        output_dir,
        '-o', output_dir,
        '--batch'
    ]
    
    if config.get('preprocessing', {}).get('normalize', False):
        cmd.extend([
            '--normalize',
            '--normalize-target', str(config['preprocessing'].get('target_dBFS', -20.0))
        ])
    
    if config.get('preprocessing', {}).get('fade', False):
        cmd.extend([
            '--fade',
            '--fade-duration', str(config['preprocessing'].get('fade_duration', 1000))
        ])
    
    success, stdout, stderr = run_command(
        cmd,
        f"Post-processing audio in {output_dir}",
        timeout=1800  # 30 minutes timeout
    )
    
    return success


def generate_report(output_dir, log_file, config, results):
    """
    Generate a summary report of the pipeline execution.
    
    Args:
        output_dir (str): Output directory
        log_file (str): Log file path
        config (dict): Configuration used
        results (dict): Results dictionary
    """
    report_path = Path(output_dir) / "pipeline_report.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "configuration": config,
        "results": results,
        "log_file": str(log_file),
        "output_directory": str(output_dir)
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logging.info(f"Report generated: {report_path}")


def main():
    parser = argparse.ArgumentParser(description='Batch execution and logging for voice cloning TTS')
    parser.add_argument('-c', '--config', help='Configuration file path', default='config.json')
    parser.add_argument('-r', '--reference-audio', help='Reference audio file for voice cloning')
    parser.add_argument('-t', '--texts-dir', help='Texts directory')
    parser.add_argument('-o', '--output-dir', help='Output directory')
    parser.add_argument('-l', '--languages', nargs='+', help='List of language codes')
    parser.add_argument('--skip-preprocessing', action='store_true', help='Skip audio preprocessing step')
    parser.add_argument('--skip-synthesis', action='store_true', help='Skip synthesis step')
    parser.add_argument('--skip-post-processing', action='store_true', help='Skip post-processing step')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be executed without running')
    
    args = parser.parse_args()
    
    # Set up logging
    log_file = setup_logging()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line args if provided
    if args.reference_audio:
        config['reference_audio'] = args.reference_audio
    if args.texts_dir:
        config['texts_dir'] = args.texts_dir
    if args.output_dir:
        config['output_dir'] = args.output_dir
    if args.languages:
        config['languages'] = args.languages
    
    logging.info("Starting voice cloning TTS pipeline")
    logging.info(f"Configuration: {json.dumps(config, indent=2)}")
    
    if args.dry_run:
        print("DRY RUN MODE:")
        print(f"Reference audio: {config['reference_audio']}")
        print(f"Texts directory: {config['texts_dir']}")
        print(f"Output directory: {config['output_dir']}")
        print(f"Languages: {config['languages']}")
        print("Steps to be executed:")
        if not args.skip_preprocessing:
            print("  - Audio preprocessing")
        if not args.skip_synthesis:
            print("  - Synthesis")
        if not args.skip_post_processing:
            print("  - Post-processing")
        return
    
    # Initialize results dictionary
    results = {
        "preprocessing": {"success": True, "details": ""},
        "synthesis": {"success": True, "details": ""},
        "post_processing": {"success": True, "details": ""},
        "completed_at": None
    }
    
    # Execute pipeline
    try:
        # Step 1: Preprocessing (audio validation)
        if not args.skip_preprocessing:
            logging.info("Step 1: Running preprocessing...")
            results["preprocessing"]["success"] = run_preprocessing(
                config['reference_audio'],
                config['output_dir']
            )
            if not results["preprocessing"]["success"]:
                logging.error("Preprocessing failed, stopping pipeline")
                results["preprocessing"]["details"] = "Preprocessing failed"
        else:
            logging.info("Step 1: Skipping preprocessing")
        
        # Step 2: Text preparation
        if results["preprocessing"]["success"] and not args.skip_synthesis:
            logging.info("Step 2: Running text preparation...")
            text_success = run_text_preparation(
                config['texts_dir'],
                config['languages']
            )
            results["synthesis"]["success"] = text_success
            if not text_success:
                logging.error("Text preparation failed, stopping pipeline")
                results["synthesis"]["details"] = "Text preparation failed"
        
        # Step 3: Synthesis
        if results["synthesis"]["success"] and not args.skip_synthesis:
            logging.info("Step 3: Running synthesis...")
            results["synthesis"]["success"] = run_synthesis(
                config['texts_dir'],
                config['reference_audio'],
                config['output_dir'],
                config['languages']
            )
            if not results["synthesis"]["success"]:
                logging.error("Synthesis failed")
                results["synthesis"]["details"] = "Synthesis failed"
        
        # Step 4: Post-processing
        if results["synthesis"]["success"] and not args.skip_post_processing:
            logging.info("Step 4: Running post-processing...")
            results["post_processing"]["success"] = run_post_processing(
                config['output_dir'],
                config
            )
            if not results["post_processing"]["success"]:
                logging.error("Post-processing failed")
                results["post_processing"]["details"] = "Post-processing failed"
        
        # Generate report
        results["completed_at"] = datetime.now().isoformat()
        generate_report(Path(config['output_dir']), log_file, config, results)
        
        # Final status
        all_success = all([
            results["preprocessing"]["success"],
            results["synthesis"]["success"],
            results["post_processing"]["success"]
        ])
        
        if all_success:
            logging.info("Pipeline completed successfully!")
            print("\nPipeline completed successfully!")
            print(f"Output directory: {config['output_dir']}")
            print(f"Log file: {log_file}")
        else:
            logging.error("Pipeline completed with errors!")
            print("\nPipeline completed with errors!")
            print(f"Log file: {log_file}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logging.error("Pipeline interrupted by user")
        print("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Pipeline failed with exception: {str(e)}")
        print(f"\nPipeline failed with exception: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()