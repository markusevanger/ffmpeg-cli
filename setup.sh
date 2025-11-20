#!/bin/bash

# FFmpeg CLI Wizard Setup Script

echo "Setting up FFmpeg CLI Wizard..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg is not installed. Please install it with: brew install ffmpeg"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Make script executable
echo "Making script executable..."
chmod +x ffmpeg_wizard.py

echo "Setup complete!"
echo ""
echo "To use the wizard, run: ./ffmpeg_wizard.py"
echo "Or add it to your PATH to use it from anywhere."

