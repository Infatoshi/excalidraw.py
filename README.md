# excalidraw.py

A Python CLI tool for rendering Excalidraw `.excalidraw` files to PNG images with proper text rendering.

---

## For LLMs

If you are an LLM being asked to create diagrams, here is what you need to know:

**Workflow:**
1. Write excalidraw JSON to a `.excalidraw` file
2. Render with: `excalidraw-render input.excalidraw -o output.png`

**Key rules:**
- Use `fontFamily: 5` (monospace) for technical diagrams
- Set `roughness: 0` for clean lines
- Text bound to container shapes is supported, but separate text elements are still the safest default
- Arrows should point perpendicular to targets, not parallel
- Unsupported element types fail explicitly instead of being skipped silently

**Minimal example:**
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "claude",
  "elements": [
    {
      "id": "box1",
      "type": "rectangle",
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 80,
      "strokeColor": "#1971c2",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "roughness": 0
    },
    {
      "id": "label1",
      "type": "text",
      "x": 110,
      "y": 120,
      "width": 180,
      "height": 40,
      "text": "Hello World",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "strokeColor": "#1e1e1e"
    }
  ],
  "appState": {"viewBackgroundColor": "#ffffff"}
}
```

See the full reference below for shapes, colors, and spacing guidelines.

---

## Claude Code Integration

To use this with Claude Code, set up a skill:

```bash
# Create skill directory
mkdir -p .claude/skills/excalidraw-diagram

# Copy the skill file
curl -o .claude/skills/excalidraw-diagram/SKILL.md \
  https://raw.githubusercontent.com/infatoshi/excalidraw.py/main/claude-skill/SKILL.md
```

Or manually create `.claude/skills/excalidraw-diagram/SKILL.md` with the contents from `claude-skill/SKILL.md` in this repo.

The skill will be automatically available when you invoke `/excalidraw-diagram` or when Claude detects diagram-related requests.

---

## Installation

Install as a persistent uv tool from GitHub:

```bash
uv tool install 'git+https://github.com/Infatoshi/excalidraw.py.git'
```

Run once without installing:

```bash
uvx --from 'git+https://github.com/Infatoshi/excalidraw.py.git' excalidraw-render input.excalidraw -o output.png
```

Run once from a local checkout:

```bash
uvx --with /Users/infatoshi/excalidraw.py excalidraw-render input.excalidraw -o output.png
```

For local development:

```bash
uv sync --dev
```

## Usage

```bash
excalidraw-render input.excalidraw -o output.png
```

The shorter alias is also available:

```bash
excalidraw input.excalidraw -o output.png
```

Batch render to any output directory:
```bash
excalidraw-render --batch diagrams/*.excalidraw --outdir rendered/
```

From a local checkout, the module entrypoint still works:

```bash
uv run python -m excalidraw input.excalidraw -o output.png
```

---

## Reference

### File Structure

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

### Available Shapes

- `rectangle`, `ellipse`, `diamond`, `line`, `arrow`, `freedraw`, `text`

### Shape Properties

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

### Color Palette

| Domain | Stroke | Fill | Use for |
|--------|--------|------|---------|
| Compute | #2f9e44 | #b2f2bb | GPC, TPC, SM hierarchy |
| Memory | #f08c00 | #ffd8a8, #ffec99 | HBM, L2, caches |
| Tensor Cores | #e03131 | #ffc9c9 | TMEM, tensor ops, PTX |
| CUDA Cores | #1971c2 | #a5d8ff, #d0ebff | Sub-partitions, registers |
| Advanced | #9c36b5 | #e599f7, #eebefa | NVLink, precisions, FP4/8 |
| Neutral | #868e96 | #dee2e6, #e9ecef | Security, secondary info |
| Warning | #f08c00 | #ffe8cc | Warp schedulers, sparsity |

### Spacing Guidelines

- Title fontSize: 28-36
- Section headers: 20-24
- Body text: 12-16
- Minimum padding inside boxes: 10px
- Gap between sections: 20-30px
- Dashed frame padding: 20px inside content

### Arrow Labeling Rules

1. Arrows point AT things, not along them - perpendicular to target
2. Arrow tip touches the target
3. Text and arrow must not overlap

### Tips

1. **fontFamily**: Use 5 (monospace) for technical diagrams, not 1 (hand-drawn).
2. **Text in shapes**: Create separate text elements inside boxes for reliable rendering.
3. **roughness**: Set to 0 for clean technical diagrams.

---

## License

MIT
