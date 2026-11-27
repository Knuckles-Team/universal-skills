---
name: creative-media
domain: creative
skill_type: skill
description: >-
  Creates and manipulates creative media assets including animated GIFs, social
  media videos, image format conversions, and basic video editing workflows. Use
  when the user requests an animated GIF from images, video clipping, format
  conversion (PNG to WebP), or creative media processing. Do NOT use for generic
  data processing or non-creative file management.
license: MIT
tags: [media, gif, video, image-processing, ffmpeg, pillow, conversion]
metadata:
  version: '1.7.0'
  author: Knuckles-Team
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

## Steps

1. Identify the source files and the target format.
   Run `ffprobe -hide_banner input.mp4` or `file *.png`. Verify that the codec, dimensions, and duration are known.
2. Check that the tools are available.
   Run `ffmpeg -version | head -1` and `python -c "import PIL; print(PIL.__version__)"`. Verify that both print a version.
3. Run the matching command from the Tool Usage Guide, such as the `palettegen` GIF recipe, the `-ss`/`-t` clip, or the Pillow WebP conversion.
   Verify that `ls -l output.*` shows a nonempty file.
4. Inspect the result.
   Run `ffprobe -hide_banner output.gif` or `python -c "from PIL import Image; print(Image.open('output.webp').size)"`. Verify that the dimensions keep the source aspect ratio and the width is at most 480 for Slack GIFs.
5. Deliver the file with its path and size.
   Run `du -h output.*`. Verify that the size is reasonable for the target channel.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| GIF has banding or wrong colors | Palette was not generated | Rerun the `palettegen`/`paletteuse` filter chain from the guide |
| Clipped video is not cut at the requested time | `-c copy` snaps to keyframes | Rerun without `-c copy` to re-encode for frame-accurate cuts |
| `ffmpeg: command not found` | FFmpeg not installed | Install it with the system package manager, e.g. `apt-get install ffmpeg`, then repeat the command |

## Best Practices

- **WebP First**: Use WebP for static web images to save ~30% in file size with better quality than JPEG.
- **Conserve Resources**: For large video files, use `-c copy` (stream copying) whenever possible to avoid re-encoding.
- **Aspect Ratio**: Always maintain aspect ratio unless explicitly told to crop or stretch.
- **Silent Video**: Remove audio streams (`-an`) for social media clips unless audio is required.
