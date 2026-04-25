import json
from pathlib import Path

from PIL import Image
import pytest

from excalidraw.cli import batch_render
from excalidraw.parser import ExcalidrawElement, calculate_bounds
from excalidraw.renderer import ExcalidrawRenderer
from excalidraw.text import font_paths_for_family, resolve_font_path, svg_font_family_name


def write_document(path: Path, elements: list[dict]):
    path.write_text(
        json.dumps(
            {
                "type": "excalidraw",
                "version": 2,
                "source": "test",
                "elements": elements,
                "appState": {"viewBackgroundColor": "#ffffff"},
            }
        ),
        encoding="utf-8",
    )


def test_calculate_bounds_includes_freedraw_points():
    bounds = calculate_bounds(
        [
            ExcalidrawElement(
                id="free",
                type="freedraw",
                x=10,
                y=20,
                points=[[0, 0], [5, -4], [-3, 2]],
            )
        ],
        padding=0,
    )

    assert bounds.min_x == 7
    assert bounds.min_y == 16
    assert bounds.max_x == 15
    assert bounds.max_y == 22


def test_render_to_png_rejects_unsupported_elements(tmp_path: Path):
    doc = tmp_path / "unsupported.excalidraw"
    write_document(
        doc,
        [
            {
                "id": "img1",
                "type": "image",
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 100,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 1,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "index": "a0",
            }
        ],
    )

    renderer = ExcalidrawRenderer(scale=1.0).load(doc)

    with pytest.raises(ValueError, match="Unsupported element type"):
        renderer.render_to_png(tmp_path / "unsupported.png")


def test_freedraw_renders_visible_stroke(tmp_path: Path):
    doc = tmp_path / "freedraw.excalidraw"
    write_document(
        doc,
        [
            {
                "id": "free1",
                "type": "freedraw",
                "x": 10,
                "y": 10,
                "width": 100,
                "height": 30,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "points": [[0, 0], [40, 20], [100, 0]],
                "index": "a0",
            }
        ],
    )

    out = tmp_path / "freedraw.png"
    ExcalidrawRenderer(scale=1.0).load(doc).render_to_png(out)

    img = Image.open(out).convert("L")
    assert img.getextrema()[0] < 255


def test_batch_render_returns_failure_count(tmp_path: Path):
    good = tmp_path / "good.excalidraw"
    bad = tmp_path / "bad.excalidraw"

    write_document(
        good,
        [
            {
                "id": "rect1",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": 40,
                "height": 20,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "index": "a0",
            }
        ],
    )
    write_document(
        bad,
        [
            {
                "id": "img1",
                "type": "image",
                "x": 0,
                "y": 0,
                "width": 40,
                "height": 20,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "index": "a0",
            }
        ],
    )

    outdir = tmp_path / "out"
    failures = batch_render([good, bad], outdir, "png", scale=1.0)

    assert failures == 1
    assert (outdir / "good.png").exists()
    assert not (outdir / "bad.png").exists()


def test_svg_font_family_name_maps_monospace():
    assert svg_font_family_name(5) == "monospace"


def test_monospace_font_resolution_includes_macos_menlo():
    candidates = font_paths_for_family(5)

    assert Path("/System/Library/Fonts/Menlo.ttc") in candidates
    if Path("/System/Library/Fonts/Menlo.ttc").exists():
        assert resolve_font_path(5) == Path("/System/Library/Fonts/Menlo.ttc")


def test_bound_text_renders_inside_container(tmp_path: Path):
    doc = tmp_path / "bound.excalidraw"
    write_document(
        doc,
        [
            {
                "id": "rect1",
                "type": "rectangle",
                "x": 0,
                "y": 0,
                "width": 200,
                "height": 100,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "index": "a0",
            },
            {
                "id": "text1",
                "type": "text",
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
                "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "strokeStyle": "solid",
                "roughness": 0,
                "opacity": 100,
                "text": "CENTER",
                "fontSize": 20,
                "fontFamily": 5,
                "textAlign": "center",
                "lineHeight": 1.25,
                "containerId": "rect1",
                "index": "a1",
            },
        ],
    )

    out = tmp_path / "bound.png"
    ExcalidrawRenderer(scale=1.0).load(doc).render_to_png(out)

    img = Image.open(out).convert("L")
    crop = img.crop(
        (
            int(img.width * 0.4),
            int(img.height * 0.4),
            int(img.width * 0.6),
            int(img.height * 0.6),
        )
    )
    assert crop.getextrema()[0] < 255
