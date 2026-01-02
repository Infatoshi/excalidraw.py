# Excalidraw Renderer

A Python CLI tool for rendering Excalidraw `.excalidraw` files to PNG images with proper text rendering.

## Installation

```bash
pip install -e .
```

Or with uv:
```bash
uv pip install -e .
```

## Usage

```bash
python -m excalidraw_renderer input.excalidraw -o output.png
```

Or if installed:
```bash
excalidraw-render input.excalidraw -o output.png
```

## File Structure

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude",
  "elements": [...],
  "appState": {
    "viewBackgroundColor": "#ffffff"
  }
}
```

## Available Shapes

- `rectangle`, `ellipse`, `diamond`, `line`, `arrow`, `text`

## Shape Properties

```json
{
  "id": "unique_id",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 150,
  "height": 80,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0
}
```

### Text Elements

```json
{
  "id": "label1",
  "type": "text",
  "x": 110,
  "y": 110,
  "width": 130,
  "height": 60,
  "text": "Multi-line\ntext here",
  "fontSize": 16,
  "fontFamily": 5,
  "textAlign": "center",
  "strokeColor": "#1e1e1e"
}
```

**fontFamily:** 1=hand-drawn, 2=normal, 5=monospace (use for technical diagrams)

### Arrow/Line Elements

```json
{
  "id": "arrow1",
  "type": "arrow",
  "x": 100,
  "y": 100,
  "width": 0,
  "height": 50,
  "strokeColor": "#1971c2",
  "strokeWidth": 2,
  "roughness": 0,
  "points": [[0, 0], [0, 50]]
}
```

### Dashed Frames

```json
{
  "id": "frame1",
  "type": "rectangle",
  "strokeColor": "#2f9e44",
  "backgroundColor": "transparent",
  "strokeStyle": "dashed",
  "roughness": 0
}
```

## Color Palette

| Domain | Stroke | Fill | Use for |
|--------|--------|------|---------|
| Compute | #2f9e44 | #b2f2bb | GPC, TPC, SM hierarchy |
| Memory | #f08c00 | #ffd8a8, #ffec99 | HBM, L2, caches |
| Tensor Cores | #e03131 | #ffc9c9 | TMEM, tensor ops, PTX |
| CUDA Cores | #1971c2 | #a5d8ff, #d0ebff | Sub-partitions, registers |
| Advanced | #9c36b5 | #e599f7, #eebefa | NVLink, precisions, FP4/8 |
| Neutral | #868e96 | #dee2e6, #e9ecef | Security, secondary info |
| Warning | #f08c00 | #ffe8cc | Warp schedulers, sparsity |

## Spacing Guidelines

- Title fontSize: 28-36
- Section headers: 20-24
- Body text: 12-16
- Minimum padding inside boxes: 10px
- Gap between sections: 20-30px
- Dashed frame padding: 20px inside content

## Arrow Labeling Rules

1. Arrows point AT things, not along them - perpendicular to target
2. Arrow tip touches the target
3. Text and arrow must not overlap

## Tips

1. **fontFamily**: Use 5 (monospace) for technical diagrams, not 1 (hand-drawn).
2. **Text in shapes**: Create separate text elements inside boxes for reliable rendering.
3. **roughness**: Set to 0 for clean technical diagrams.

## License

MIT
