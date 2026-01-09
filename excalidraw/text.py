"""
Text rendering for Excalidraw elements using PIL with Virgil font.
"""

import io
from pathlib import Path
from typing import List, TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from .colors import to_pil_color

if TYPE_CHECKING:
    from .parser import ExcalidrawElement
    from .renderer import ExcalidrawRenderer


# Path to Virgil font - inside this package
FONT_DIR = Path(__file__).parent / "fonts"
VIRGIL_FONT = FONT_DIR / "Virgil.ttf"

# Font cache to avoid reloading
_font_cache: dict = {}


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Get Virgil font at specified size, with caching."""
    if size not in _font_cache:
        if not VIRGIL_FONT.exists():
            raise FileNotFoundError(f"Virgil font not found at {VIRGIL_FONT}")
        _font_cache[size] = ImageFont.truetype(str(VIRGIL_FONT), size)
    return _font_cache[size]


def render_text_overlay(
    png_buffer: io.BytesIO,
    text_elements: List["ExcalidrawElement"],
    renderer: "ExcalidrawRenderer"
) -> Image.Image:
    """
    Overlay text elements on a PNG image using PIL.

    Args:
        png_buffer: BytesIO containing PNG data from cairo
        text_elements: List of text elements to render
        renderer: ExcalidrawRenderer for coordinate transformation

    Returns:
        PIL Image with text overlaid
    """
    # Load the cairo-rendered shapes
    img = Image.open(png_buffer).convert("RGBA")
    draw = ImageDraw.Draw(img)

    for elem in text_elements:
        if not elem.text:
            continue

        # Transform coordinates
        tx, ty = renderer.transform(elem.x, elem.y)

        # Scale font size
        font_size = int(elem.font_size * renderer.scale)
        font = get_font(font_size)

        # Get color
        color = to_pil_color(elem.stroke_color, elem.opacity)

        # Handle multiline text
        lines = elem.text.split("\n")
        line_height = font_size * elem.line_height

        for i, line in enumerate(lines):
            y_offset = ty + i * line_height

            # Handle text alignment
            if elem.text_align == "center":
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_pos = tx + (elem.width * renderer.scale - text_width) / 2
            elif elem.text_align == "right":
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_pos = tx + elem.width * renderer.scale - text_width
            else:
                x_pos = tx

            draw.text((x_pos, y_offset), line, font=font, fill=color)

    return img


def render_bound_text(
    draw: ImageDraw.ImageDraw,
    elem: "ExcalidrawElement",
    container_x: float,
    container_y: float,
    container_width: float,
    container_height: float,
    renderer: "ExcalidrawRenderer"
):
    """
    Render text bound to a container shape.

    For text elements with containerId set, the text should be
    centered within the container bounds.
    """
    if not elem.text:
        return

    font_size = int(elem.font_size * renderer.scale)
    font = get_font(font_size)
    color = to_pil_color(elem.stroke_color, elem.opacity)

    lines = elem.text.split("\n")
    line_height = font_size * elem.line_height

    # Calculate total text height
    total_height = len(lines) * line_height

    # Center vertically in container
    start_y = container_y + (container_height - total_height) / 2

    for i, line in enumerate(lines):
        y_pos = start_y + i * line_height

        # Center horizontally
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_pos = container_x + (container_width - text_width) / 2

        draw.text((x_pos, y_pos), line, font=font, fill=color)
