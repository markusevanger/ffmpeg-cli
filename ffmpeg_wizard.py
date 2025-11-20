#!/usr/bin/env python3
"""
FFmpeg CLI Wizard - Interactive image conversion tool
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import questionary
except ImportError:
    print("Error: questionary library is not installed.")
    print("Please install it with: pip install -r requirements.txt")
    sys.exit(1)


# Image extensions supported
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif'}


def check_ffmpeg() -> bool:
    """Check if ffmpeg is installed and available."""
    return shutil.which('ffmpeg') is not None


def get_current_directory_items() -> Tuple[List[Path], List[Path]]:
    """Get directories and image files in current directory."""
    current_dir = Path.cwd()
    directories = []
    image_files = []
    
    try:
        for item in current_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                directories.append(item)
            elif item.is_file():
                if item.suffix.lower() in IMAGE_EXTENSIONS:
                    image_files.append(item)
    except PermissionError:
        pass
    
    return sorted(directories), sorted(image_files)


def get_directory_items(path: Path) -> Tuple[List[Path], List[Path]]:
    """Get directories and image files in a specific directory."""
    directories = []
    image_files = []
    
    try:
        for item in path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                directories.append(item)
            elif item.is_file():
                if item.suffix.lower() in IMAGE_EXTENSIONS:
                    image_files.append(item)
    except PermissionError:
        pass
    
    return sorted(directories), sorted(image_files)


def format_file_size(path: Path) -> str:
    """Format file size for display."""
    try:
        size = path.stat().st_size
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size / (1024 * 1024):.1f}MB"
    except:
        return ""


def select_conversion_type() -> str:
    """Step 1: Choose conversion type."""
    choice = questionary.select(
        "What would you like to convert?",
        choices=[
            questionary.Choice("Single file", "file"),
            questionary.Choice("Directory", "directory"),
        ],
        style=questionary.Style([
            ('question', 'fg:#673ab7 bold'),
            ('selected', 'fg:#ff6f00 bold'),
            ('pointer', 'fg:#ff6f00'),
        ])
    ).ask()
    
    return choice


def browse_for_file(start_path: Path) -> Optional[Path]:
    """Browse directories to select a file, allowing navigation into subdirectories."""
    current_path = start_path
    
    while True:
        directories, image_files = get_directory_items(current_path)
        
        # Build choices list
        choices = []
        
        # Add "go up" option (always available except at filesystem root)
        if current_path != current_path.parent:  # Not at root
            choices.append(
                questionary.Choice("⬆️  .. (go up)", "..")
            )
        
        # Add directories
        for dir in directories:
            choices.append(
                questionary.Choice(f"📁 {dir.name}/", dir)
            )
        
        # Add image files
        for file in image_files:
            choices.append(
                questionary.Choice(
                    f"📄 {file.name} ({format_file_size(file)})",
                    file
                )
            )
        
        if not choices:
            print(f"❌ No files or directories found in {current_path}")
            return None
        
        # Show current path in prompt
        rel_path = current_path.relative_to(start_path) if current_path != start_path else Path(".")
        prompt = f"Select a file (current: {rel_path}/):"
        
        selected = questionary.select(
            prompt,
            choices=choices,
            style=questionary.Style([
                ('question', 'fg:#673ab7 bold'),
                ('selected', 'fg:#ff6f00 bold'),
                ('pointer', 'fg:#ff6f00'),
            ])
        ).ask()
        
        if selected == "..":
            # Go up one directory
            current_path = current_path.parent
            continue
        elif isinstance(selected, Path):
            if selected.is_file():
                # File selected, return it
                return selected
            elif selected.is_dir():
                # Directory selected, navigate into it
                current_path = selected
                continue
        
        return None


def select_file_or_directory(conversion_type: str) -> Optional[Path]:
    """Step 2: Select file or directory."""
    start_path = Path.cwd()
    
    if conversion_type == "file":
        # Use file browser that allows navigating subdirectories
        return browse_for_file(start_path)
    
    else:  # directory
        directories, _ = get_current_directory_items()
        
        if not directories:
            print("❌ No directories found in current directory.")
            return None
        
        choices = [
            questionary.Choice(f"📁 {dir.name}/", dir)
            for dir in directories
        ]
        
        selected = questionary.select(
            "Select a directory:",
            choices=choices,
            style=questionary.Style([
                ('question', 'fg:#673ab7 bold'),
                ('selected', 'fg:#ff6f00 bold'),
                ('pointer', 'fg:#ff6f00'),
            ])
        ).ask()
        
        return selected


def ask_keep_aspect_ratio() -> bool:
    """Step 3: Ask if user wants to keep aspect ratio."""
    return questionary.confirm(
        "Keep aspect ratio?",
        default=True,
        style=questionary.Style([
            ('question', 'fg:#673ab7 bold'),
            ('selected', 'fg:#ff6f00 bold'),
        ])
    ).ask()


def ask_dimensions(keep_aspect_ratio: bool) -> Tuple[int, Optional[int]]:
    """Step 4-5: Ask for height and optionally width."""
    def validate_number(text: str) -> bool:
        try:
            num = int(text)
            return num > 0
        except ValueError:
            return False
    
    height = questionary.text(
        "Enter height (in pixels):",
        validate=validate_number,
        style=questionary.Style([
            ('question', 'fg:#673ab7 bold'),
        ])
    ).ask()
    
    height = int(height)
    width = None
    
    if not keep_aspect_ratio:
        width = questionary.text(
            "Enter width (in pixels):",
            validate=validate_number,
            style=questionary.Style([
                ('question', 'fg:#673ab7 bold'),
            ])
        ).ask()
        width = int(width)
    
    return height, width


def select_format() -> str:
    """Step 6: Select output format."""
    choice = questionary.select(
        "Select output format:",
        choices=[
            questionary.Choice("PNG", "png"),
            questionary.Choice("JPG", "jpg"),
            questionary.Choice("WebP", "webp"),
        ],
        style=questionary.Style([
            ('question', 'fg:#673ab7 bold'),
            ('selected', 'fg:#ff6f00 bold'),
            ('pointer', 'fg:#ff6f00'),
        ])
    ).ask()
    
    return choice


def ask_quality() -> int:
    """Step 7: Ask for quality percentage."""
    def validate_quality(text: str) -> bool:
        try:
            num = int(text)
            return 1 <= num <= 100
        except ValueError:
            return False
    
    quality = questionary.text(
        "Enter quality (1-100, default: 75):",
        default="75",
        validate=validate_quality,
        style=questionary.Style([
            ('question', 'fg:#673ab7 bold'),
        ])
    ).ask()
    
    return int(quality)


def ask_output_directory() -> Path:
    """Step 8: Ask for output directory."""
    output_dir = questionary.text(
        "Enter output directory (default: out/):",
        default="out/",
        style=questionary.Style([
            ('question', 'fg:#673ab7 bold'),
        ])
    ).ask()
    
    return Path(output_dir)


def get_image_files(path: Path) -> List[Path]:
    """Get all image files from a path (file or directory)."""
    if path.is_file():
        return [path]
    elif path.is_dir():
        image_files = []
        for item in path.iterdir():
            if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS:
                image_files.append(item)
        return sorted(image_files)
    return []


def build_ffmpeg_command(
    input_path: Path,
    output_path: Path,
    height: int,
    width: Optional[int],
    format_ext: str,
    quality: int
) -> List[str]:
    """Build ffmpeg command for conversion."""
    cmd = ['ffmpeg', '-i', str(input_path), '-y']  # -y to overwrite
    
    # Build scale filter
    if width is None:
        # Keep aspect ratio
        scale_filter = f"scale=-1:{height}"
    else:
        scale_filter = f"scale={width}:{height}"
    
    cmd.extend(['-vf', scale_filter])
    
    # Add quality/format specific options
    if format_ext == 'png':
        # PNG uses -quality flag (0-100, but inverted: lower = better quality)
        # Convert 1-100 to 0-100 scale where 100 = best quality
        png_quality = 100 - int((quality - 1) * (100 / 99))
        cmd.extend(['-quality', str(png_quality)])
    elif format_ext == 'jpg':
        # JPG uses -q:v (1-31, lower = better quality)
        # Convert 1-100 to 31-1 scale
        jpg_quality = 31 - int((quality - 1) * (30 / 99))
        cmd.extend(['-q:v', str(int(jpg_quality))])
    elif format_ext == 'webp':
        # WebP uses -quality flag (0-100)
        cmd.extend(['-quality', str(quality)])
    
    cmd.append(str(output_path))
    
    return cmd


def convert_images(
    input_path: Path,
    output_dir: Path,
    height: int,
    width: Optional[int],
    format_ext: str,
    quality: int
) -> Tuple[int, int]:
    """Convert images using ffmpeg."""
    image_files = get_image_files(input_path)
    
    if not image_files:
        print("❌ No image files found to convert.")
        return 0, 0
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    failed = 0
    
    print(f"\n🔄 Converting {len(image_files)} image(s)...\n")
    
    for i, image_file in enumerate(image_files, 1):
        # Create output filename with new extension
        output_filename = image_file.stem + f".{format_ext}"
        output_path = output_dir / output_filename
        
        print(f"[{i}/{len(image_files)}] Converting {image_file.name}...", end=" ", flush=True)
        
        try:
            cmd = build_ffmpeg_command(
                image_file,
                output_path,
                height,
                width,
                format_ext,
                quality
            )
            
            # Run ffmpeg (suppress output)
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                print("✅")
                successful += 1
            else:
                print(f"❌ Error: {result.stderr[:100]}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failed += 1
    
    return successful, failed


def main():
    """Main wizard flow."""
    print("\n" + "=" * 60)
    print("🎬 FFmpeg CLI Wizard".center(60))
    print("=" * 60 + "\n")
    
    # Check if ffmpeg is installed
    if not check_ffmpeg():
        print("❌ Error: FFmpeg is not installed or not in PATH.")
        print("Please install FFmpeg: brew install ffmpeg")
        sys.exit(1)
    
    try:
        # Step 1: Conversion type
        conversion_type = select_conversion_type()
        if not conversion_type:
            print("❌ No selection made. Exiting.")
            return
        
        # Step 2: Select file/directory
        selected_path = select_file_or_directory(conversion_type)
        if not selected_path:
            print("❌ No file/directory selected. Exiting.")
            return
        
        # Step 3: Aspect ratio
        keep_aspect_ratio = ask_keep_aspect_ratio()
        
        # Step 4-5: Dimensions
        height, width = ask_dimensions(keep_aspect_ratio)
        
        # Step 6: Format
        format_ext = select_format()
        
        # Step 7: Quality
        quality = ask_quality()
        
        # Step 8: Output directory
        output_dir = ask_output_directory()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Conversion Summary".center(60))
        print("=" * 60)
        print(f"Input:        {selected_path}")
        print(f"Output:       {output_dir}")
        print(f"Dimensions:   {width if width else 'auto'} x {height}")
        print(f"Format:       {format_ext.upper()}")
        print(f"Quality:      {quality}%")
        print(f"Aspect Ratio: {'Preserved' if keep_aspect_ratio else 'Custom'}")
        print("=" * 60 + "\n")
        
        # Confirm before proceeding
        proceed = questionary.confirm(
            "Proceed with conversion?",
            default=True
        ).ask()
        
        if not proceed:
            print("❌ Conversion cancelled.")
            return
        
        # Convert images
        successful, failed = convert_images(
            selected_path,
            output_dir,
            height,
            width,
            format_ext,
            quality
        )
        
        # Final summary
        print("\n" + "=" * 60)
        print("✨ Conversion Complete!".center(60))
        print("=" * 60)
        print(f"✅ Successful: {successful}")
        if failed > 0:
            print(f"❌ Failed:     {failed}")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

