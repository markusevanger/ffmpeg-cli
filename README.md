# FFmpeg CLI Wizard

An interactive command-line tool for batch image conversion using FFmpeg with a beautiful, user-friendly wizard interface.

## Features

- Interactive wizard with arrow-key navigation
- Convert single files or entire directories
- Aspect ratio preservation option
- Custom width/height selection
- Multiple output formats (PNG, JPG, WebP)
- Quality control (default 75%)
- Custom output directory selection

## Installation

1. Install Python 3 (if not already installed)
2. Install FFmpeg:

   ```bash
   brew install ffmpeg
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Make the script executable:

   ```bash
   chmod +x ffmpeg_wizard.py
   ```

## Usage

### Run from project directory

```bash
./ffmpeg_wizard.py
```

### Make it available system-wide

**Option 1: Add to PATH**

```bash
# Add to your ~/.zshrc or ~/.bash_profile
export PATH="$PATH:/Users/markusevanger/personal/ffmpeg-cli"

# Then you can run from anywhere:
ffmpeg_wizard.py
```

**Option 2: Create symlink**

```bash
sudo ln -s /Users/markusevanger/personal/ffmpeg-cli/ffmpeg_wizard.py /usr/local/bin/ffmpeg-wizard
# Then run: ffmpeg-wizard
```

## How It Works

1. Choose to convert a single file or directory
2. Select the file/directory from current folder
3. Choose whether to keep aspect ratio
4. Set dimensions (height, and width if not keeping aspect ratio)
5. Select output format (PNG, JPG, WebP)
6. Set quality percentage (default: 75%)
7. Choose output directory (default: `out/`)

The wizard will then convert all images using FFmpeg with your specified settings.

## Requirements

- Python 3.6+
- FFmpeg installed and available in PATH
- questionary library (installed via requirements.txt)
