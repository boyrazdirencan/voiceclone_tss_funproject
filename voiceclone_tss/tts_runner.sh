#!/bin/bash
# Wrapper script for voice clone TTS system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    echo "Voice Clone TTS System"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  init                 Initialize project structure and install dependencies"
    echo "  preprocess <audio>   Preprocess reference audio to 16kHz mono"
    echo "  synthesize          Run full synthesis pipeline"
    echo "  demo               Create example files and run a demo"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 preprocess my_voice.wav"
    echo "  $0 synthesize"
    echo "  $0 demo"
}

init_project() {
    echo -e "${GREEN}Initializing project...${NC}"
    
    # Create directory structure
    mkdir -p data/ref data/texts data/prompts outputs logs
    
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    if command -v pip &> /dev/null; then
        pip install -r env/requirements.txt
    else
        echo -e "${RED}Error: pip is not available${NC}"
        exit 1
    fi
    
    # Check for TTS installation
    if python -c "import TTS" &> /dev/null; then
        echo -e "${GREEN}TTS is already installed${NC}"
    else
        echo -e "${YELLOW}Installing Coqui TTS...${NC}"
        pip install coqui-tts
    fi
    
    # Check for FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        echo -e "${YELLOW}FFmpeg not found. Please install FFmpeg for full functionality.${NC}"
        echo "On macOS: brew install ffmpeg"
        echo "On Ubuntu: sudo apt install ffmpeg"
    fi
    
    echo -e "${GREEN}Project initialized successfully!${NC}"
}

preprocess_audio() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please provide an audio file path${NC}"
        exit 1
    fi
    
    local audio_file="$1"
    
    if [ ! -f "$audio_file" ]; then
        echo -e "${RED}Error: Audio file does not exist: $audio_file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Preprocessing audio: $audio_file${NC}"
    python scripts/preprocess_audio.py "$audio_file" -o "data/ref/direncan_ref.wav"
    echo -e "${GREEN}Reference audio saved to data/ref/direncan_ref.wav${NC}"
}

run_synthesis() {
    echo -e "${GREEN}Running synthesis pipeline...${NC}"
    python scripts/batch_execute.py
}

run_demo() {
    echo -e "${GREEN}Creating example files...${NC}"
    python create_examples.py
    
    if [ ! -f "data/ref/direncan_ref.wav" ]; then
        echo -e "${YELLOW}No reference audio found. Please run: $0 preprocess <your_audio_file>${NC}"
        echo -e "${YELLOW}For now, creating a dummy reference file...${NC}"
        # Create a dummy file if none exists
        touch data/ref/direncan_ref.wav
        echo "This is a placeholder file, replace with actual reference audio" > data/ref/direncan_ref.txt
    fi
    
    echo -e "${GREEN}Running demo synthesis...${NC}"
    python scripts/synthesize_tss_cli.py -t data/texts -r data/ref/direncan_ref.wav -o outputs -l fr de es it sv tr --dry-run
    echo -e "${YELLOW}Note: This was a dry run. To execute, remove --dry-run from the command in the script.${NC}"
}

case "$1" in
    init)
        init_project
        ;;
    preprocess)
        preprocess_audio "$2"
        ;;
    synthesize)
        run_synthesis
        ;;
    demo)
        run_demo
        ;;
    help|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac