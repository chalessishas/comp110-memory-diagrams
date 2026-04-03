# LaTeX Rendering in Revideo -- Research Report

**Date**: 2026-03-31
**Goal**: Replace plain monospace text with real math notation in course-video `show_formula` actions.

---

## TL;DR -- Recommended Path

**Use the built-in `Latex` component from `@revideo/2d`.** It already exists, uses `mathjax-full` internally to convert TeX to SVG, and supports tweening animations. Zero new dependencies needed.

---

## Finding 1: Revideo Has a Built-in `Latex` Component

Source: `@revideo/2d/src/lib/components/Latex.ts` (already in node_modules)

The `Latex` class extends `Img`. Internally it:
1. Uses `mathjax-full` (v3.2.2, already a dependency of `@revideo/2d`)
2. Converts TeX string to SVG via MathJax's `liteAdaptor` + `SVG` output
3. Base64-encodes the SVG as a data URI
4. Renders it as an `<img>` element inside the Revideo scene graph
5. Caches rendered SVGs in a static pool for performance

### API

```tsx
import { Latex } from "@revideo/2d";

<Latex
  tex={"\\color{white} E = mc^2"}
  width={400}           // auto-calculates height from aspect ratio
  fill={"#ffe066"}      // color via \color{} in TeX string, NOT this prop
  opacity={0}
/>
```

**Important**: Color is set via `\color{...}` inside the TeX string, not via a `fill` prop (since it renders as an image).

### Props (extends ImgProps)

| Prop | Type | Description |
|------|------|-------------|
| `tex` | `string` | LaTeX expression |
| `options` | `OptionList` | MathJax render options |
| `width` / `height` | `number` | Size (one auto-derives from the other) |
| All `Img` props | -- | opacity, position, scale, rotation, etc. |

### Tweening Support (from Motion Canvas upstream)

```tsx
const ref = createRef<Latex>();

view.add(
  <Latex ref={ref} tex={"{{y=}}{{a}}{{x^2}}"} width={400} />
);

// Animate formula transformation
yield* ref().tex("{{y=}}{{a}}{{x^2}} + {{bx}}", 1);
```

Parts wrapped in `{{...}}` enable morphing animations:
- Parts present in both source and target: smoothly transform
- Parts only in source: fade out
- Parts only in target: fade in

---

## Finding 2: No Extra Dependencies Needed

`mathjax-full@^3.2.2` is a direct dependency of `@revideo/2d@0.10.3` and is installed in `node_modules/mathjax-full`. The Latex component works out of the box.

---

## Finding 3: Alternative Approaches (NOT recommended)

### KaTeX server-side
- `katex.renderToString()` produces **HTML spans, not SVG**
- Would need `<foreignObject>` hack to embed in SVG context
- Requires KaTeX CSS + fonts at render time
- **Verdict**: Wrong output format for Revideo. Skip.

### MathJax standalone (`mathjax` npm package, v4+)
- `MathJax.tex2svgPromise()` produces clean SVG
- Could work as a build-time pre-render step
- **Verdict**: Unnecessarily complex since Revideo already bundles this via its Latex component.

### Manual SVG pre-rendering
- Convert LaTeX to SVG files at build time, use `<Img src={...} />`
- **Verdict**: The Latex component already does exactly this at render time with caching. No benefit.

---

## Implementation Plan

### Step 1: Replace `show_formula` in board.tsx (5 min)

Current code (lines 81-118 of `board.tsx`):
```tsx
// Uses Txt with monospace font -- ugly
<Txt
  ref={ref}
  text={""}
  fill={"#ffe066"}
  fontSize={FORMULA_FONT_SIZE}
  fontFamily={"'IBM Plex Mono', monospace"}
/>
```

Replace with:
```tsx
import { Latex } from "@revideo/2d";

case "show_formula": {
  const id = action.id ?? registry.autoId("formula");
  const ref = createRef<Latex>();
  const x = 0; // center
  const y = cursorY - BOARD_HEIGHT / 2;

  view.add(
    <Latex
      ref={ref}
      tex={`\\color{#ffe066} ${action.latex}`}
      width={Math.min(action.latex.length * 18, BOARD_WIDTH - BOARD_PADDING * 2)}
      x={x}
      y={y}
      opacity={0}
    />
  );

  // Fade in (no typewriter -- it's an image now)
  yield* ref().opacity(1, durationS * 0.4);
  yield* waitFor(durationS * 0.6);

  const entry: ElementEntry = {
    id,
    type: "formula",
    x,
    y,
    width: Math.min(action.latex.length * 18, BOARD_WIDTH - BOARD_PADDING * 2),
    height: LINE_HEIGHT + 10,
  };
  registry.register(entry);
  advanceCursor(LINE_HEIGHT + 20);
  break;
}
```

### Step 2: Add import at top of board.tsx

```tsx
import { Txt, Rect, Line, Latex } from "@revideo/2d";
```

### Step 3: Animation Options

For reveal animations beyond simple fade-in:

**Option A -- Scale up from center** (recommended, simple):
```tsx
yield* all(
  ref().opacity(1, 0.3),
  ref().scale(0).scale(1, durationS * 0.5),
);
```

**Option B -- Clip reveal (left to right)**:
```tsx
// Wrap in a Rect with clip, animate width
const clipRef = createRef<Rect>();
view.add(
  <Rect ref={clipRef} clip width={0} height={80} x={x} y={y}>
    <Latex tex={`\\color{#ffe066} ${action.latex}`} width={formulaWidth} />
  </Rect>
);
yield* clipRef().width(formulaWidth, durationS * 0.7);
```

**Option C -- Part-by-part tweening** (most complex, 3Blue1Brown style):
```tsx
// Requires the LLM to output LaTeX with {{part}} delimiters
<Latex ref={ref} tex={"{{E}} {{=}} {{mc^2}}"} width={400} />
yield* ref().tex("{{E}} {{=}} {{mc^2}}", 1); // morph between states
```

---

## Chalkboard Visual Polish

### Chalk-style Fonts (for `write_text` actions)

| Font | Source | Style |
|------|--------|-------|
| **Permanent Marker** | Google Fonts | Bold marker look, reads well |
| **Architects Daughter** | Google Fonts | Clean handwritten, good for body text |
| **Fredericka the Great** | Google Fonts | Textured chalk look, best for titles |
| **Indie Flower** | Google Fonts | Casual handwritten |

Recommendation: **Permanent Marker** for headings, **Architects Daughter** for body text.

Load via: Include the font files in the project or use `@import` in a CSS file that Revideo's Vite config picks up.

### Chalkboard Background

Current: likely a solid dark color. Improvements:

```tsx
// Background rect with subtle texture
<Rect
  width={1920}
  height={1080}
  fill={"#2d3436"}  // dark green-gray chalkboard
/>
```

For a more realistic look, use an actual chalkboard texture image:
```tsx
<Img src={chalkboardTexture} width={1920} height={1080} />
```

Free chalkboard textures available from Unsplash, Pexels, or generated procedurally.

### Chalk Dust Effect on Text

Add a subtle glow/shadow to text elements for a chalk-dust appearance:
```tsx
<Txt
  text={action.text}
  fill={"#f0f0e8"}
  shadowColor={"#f0f0e880"}
  shadowBlur={3}
  fontFamily={"'Permanent Marker', cursive"}
/>
```

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Latex component fails in Revideo's renderer (not editor) | Low | It uses `liteAdaptor`, no real browser DOM needed |
| Complex LaTeX expressions render slowly | Low | SVG pool caching handles this |
| Color mismatch (Latex renders as image, can't style externally) | Medium | Always include `\color{...}` in the TeX string |
| Formula width estimation is off | Medium | Use fixed width + let MathJax auto-scale, or measure after render |

---

## Sources

- [Motion Canvas Latex docs](https://motioncanvas.io/docs/latex/)
- [Revideo components API](https://docs.re.video/api/2d/components/)
- [LaTeX component PR #228](https://github.com/motion-canvas/motion-canvas/pull/228)
- [Latex tweening issue #482](https://github.com/motion-canvas/motion-canvas/issues/482)
- [Motion Canvas v3.17.0 (Latex tweening)](https://motioncanvas.io/blog/version-3.17.0/)
- [KaTeX API](https://katex.org/docs/api)
- [MathJax demos node](https://github.com/mathjax/MathJax-demos-node)
- [Permanent Marker font](https://fonts.google.com/specimen/Permanent+Marker)
- [Fredericka the Great font](https://fonts.google.com/specimen/Fredericka+the+Great)
