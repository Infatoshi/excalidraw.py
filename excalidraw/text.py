"""
Text rendering for Excalidraw elements using PIL with Excalidraw-style fonts.
"""

import io
from pathlib import Path
from typing import List, TYPE_CHECKING, Optional

from PIL import Image, ImageDraw, ImageFont

from .colors import to_pil_color

if TYPE_CHECKING:
    from .parser import ExcalidrawElement
    from .renderer import ExcalidrawRenderer


# Path to Virgil font - inside this package
FONT_DIR = Path(__file__).parent / "fonts"
VIRGIL_FONT = FONT_DIR / "Virgil.ttf"
SANS_FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Helvetica.ttc"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)
MONO_FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Menlo.ttc"),
    Path("/Library/Fonts/Menlo.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSansMono.ttf"),
)

# Font cache to avoid reloading
_font_cache: dict = {}


def font_paths_for_family(font_family: int) -> List[Path]:
    """Return candidate font paths for an Excalidraw font family."""
    if font_family == 5:
        return list(MONO_FONT_CANDIDATES)
    if font_family == 2:
        return list(SANS_FONT_CANDIDATES)
    return [VIRGIL_FONT]


def svg_font_family_name(font_family: int) -> str:
    """Return a cairo/SVG font family name for an Excalidraw font family."""
    if font_family == 5:
        return "monospace"
    if font_family == 2:
        return "sans-serif"
    return "Virgil"


def resolve_font_path(font_family: int) -> Optional[Path]:
    """Resolve the best available font file for an Excalidraw font family."""
    for candidate in font_paths_for_family(font_family):
        if candidate.exists():
            return candidate
    if VIRGIL_FONT.exists():
        return VIRGIL_FONT
    return None


def get_font(size: int, font_family: int = 1):
    """Get a font at specified size and family, with caching."""
    key = (size, font_family)
    if key not in _font_cache:
        font_path = resolve_font_path(font_family)
        if font_path is not None:
            _font_cache[key] = ImageFont.truetype(str(font_path), size)
        else:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


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
    elements_by_id = {elem.id: elem for elem in renderer.elements}

    for elem in text_elements:
        if not elem.text:
            continue

        if elem.container_id:
            container = elements_by_id.get(elem.container_id)
            if container is not None:
                container_x, container_y = renderer.transform(container.x, container.y)
                container_width = container.width * renderer.scale
                container_height = container.height * renderer.scale
                render_bound_text(
                    draw,
                    elem,
                    container_x,
                    container_y,
                    container_width,
                    container_height,
                    renderer,
                )
                continue

        # Transform coordinates
        tx, ty = renderer.transform(elem.x, elem.y)

        # Scale font size
        font_size = int(elem.font_size * renderer.scale)
        font = get_font(font_size, elem.font_family)

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
    font = get_font(font_size, elem.font_family)
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
