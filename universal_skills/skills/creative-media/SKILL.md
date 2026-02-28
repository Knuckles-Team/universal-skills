---
name: creative-media
description: Creates and manipulates creative media assets including animated GIFs, social media videos, image format conversions, and basic video editing workflows. Use when the user requests an animated GIF from images, video clipping, format conversion (PNG to WebP), or creative media processing. Do NOT use for generic data processing or non-creative file management.
categories: [Creative]
tags: [media, gif, video, image-processing, ffmpeg, pillow, conversion]
---

# Creative Media Tools

Handle creative media workflows including image processing, animation creation, and video manipulation using industry-standard tools like FFmpeg and Pillow.

---

## Core Capabilities

### 1. Animated GIF Creation
Convert sequences of images or short video clips into optimized, high-quality GIFs.

**Key considerations:**
- **Optimization**: Use `ffmpeg` palette generation for better color quality at smaller file sizes.
- **Framerate**: Standard output is 10–24 fps for smooth motion without excessive bloat.
- **Looping**: Infinite loop by default.

### 2. Image Processing & Conversion
Batch process images or perform creative transformations.

**Supported Tasks:**
- **Conversion**: PNG / JPG to WebP (highly recommended for web).
- **Resizing**: Content-aware or aspect-ratio locked resizing.
- **Watermarking**: Programmatic overlay of logos or text.
- **Filters**: Grayscale, Blur, Sharpen, Color Correction.

### 3. Basic Video Editing
Clipping, joining, and reformatting video assets for social media or presentation use.

---

## Tool Usage Guide

### FFmpeg (Video & Animation)

**Creating a high-quality GIF from video:**
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
```

**Clipping video:**
```bash
ffmpeg -i input.mp4 -ss [start_time] -t [duration] -c copy output.mp4
```

### Pillow (Image Processing - Python)

**Batch conversion to WebP:**
```python
from PIL import Image
import os

def convert_to_webp(source_path):
    img = Image.open(source_path)
    base = os.path.splitext(source_path)[0]
    img.save(f"{base}.webp", "WEBP", quality=80)
```

---

## Workflow for "Slack-Style" GIF Creation

When creating an animated GIF for internal comms or slack:
1. **Source**: Identify the 1–5 second clip or image sequence.
2. **Standardize**: Scale to max 480px width (Slack friendly).
3. **Generate Palette**: Always use `palettegen` for accurate colors.
4. **Export**: Deliver the `.gif` and provide a direct link.

---

## Best Practices

- **WebP First**: Use WebP for static web images to save ~30% in file size with better quality than JPEG.
- **Conserve Resources**: For large video files, use `-c copy` (stream copying) whenever possible to avoid re-encoding.
- **Aspect Ratio**: Always maintain aspect ratio unless explicitly told to crop or stretch.
- **Silent Video**: Remove audio streams (`-an`) for social media clips unless audio is required.
