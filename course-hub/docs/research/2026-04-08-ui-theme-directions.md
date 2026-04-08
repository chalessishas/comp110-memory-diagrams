# CourseHub UI Theme Directions

> Research date: 2026-04-08
> Context: CourseHub skeleton is black/white/gray only. Designing 5 distinct theme directions as candidates.

## Research Sources

- [Lollypop: Education App Design Trends 2025](https://lollypop.design/blog/2025/august/top-education-app-design-trends-2025/)
- [FRAM: UI/UX Design Trends for E-Learning](https://framcreative.com/insights/latest-trends-best-practices-and-top-experiences-in-ui-ux-design-for-e-learning)
- [Figr: Best UI Kits 2025 (Duolingo, TikTok, Airbnb)](https://figr.design/blog/best-ui-kits-for-2025-inspired-by-duolingo-tiktok-airbnb-and-more)
- [Dark Mode vs. Light Mode 2025](https://medium.com/@huedserve/dark-mode-vs-light-mode-2025-best-for-ux-design-07f17617023c)
- [getcolors.dev: SaaS Dashboard Palette](https://www.getcolors.dev/en/colors/saas-dashboard)
- [Lounge Lizard: 2026 Web Design Color Trends](https://www.loungelizard.com/blog/web-design-color-trends/)
- [Elegant Themes: 2026 Balanced Web Design Palettes](https://www.elegantthemes.com/blog/design/color-palettes-for-balanced-web-design)

## Key Trend Findings

1. **Light mode still wins for education**: 55% of users prefer light mode in educational apps for perceived clarity and professionalism
2. **Muted backgrounds + bold accents**: Soft blues, teals, and grays for backgrounds; strategic bold colors for CTAs
3. **Design tokens via HSL**: Modern systems use HSL-based variables for instant recoloring and light/dark support
4. **Neon micro-accents**: Back in SaaS/tech UI as small highlights, not dominant colors
5. **Accessibility first**: WCAG contrast ratios are no longer optional; systems start with readability
6. **Gamification signals**: Progress bars, badges, streaks are table-stakes for student engagement
7. **Simplicity reduces cognitive load**: Minimalist interfaces with clear visual hierarchy

---

## Theme A: "Scholar" -- Clean Academic

**Vibe**: The Notion/Linear productivity aesthetic applied to learning. Quiet confidence, maximum information density, zero decoration noise.

**Inspiration**: Notion, Linear, Todoist, Craft

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#FFFFFF` | Page background |
| `--bg-surface` | `#F7F7F5` | Card/panel backgrounds |
| `--bg-surface-hover` | `#EFEDEA` | Card hover state |
| `--text-primary` | `#1A1A1A` | Headings, primary content |
| `--text-secondary` | `#5C5C5C` | Body text, descriptions |
| `--text-muted` | `#9B9B9B` | Timestamps, placeholders |
| `--accent` | `#2F6EEB` | Links, primary buttons, focus rings |
| `--accent-hover` | `#1B5BD4` | Button hover |
| `--accent-subtle` | `#EBF1FD` | Accent background tint |
| `--success` | `#2EA043` | Completed, correct |
| `--warning` | `#D4A017` | Due soon, caution |
| `--danger` | `#CF222E` | Overdue, errors |
| `--border` | `#E5E5E3` | Default borders |
| `--border-strong` | `#D0D0CC` | Emphasized dividers |

### Typography

```
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--letter-spacing-tight: -0.02em;    /* headings */
--letter-spacing-normal: -0.01em;   /* body */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
```

Weight distribution: Headings at 600, body at 400, labels/buttons at 500. No bold (700) anywhere -- medium weights only.

### Border Radius

```
--radius-sm: 4px;    /* inputs, small chips */
--radius-md: 6px;    /* cards, dropdowns */
--radius-lg: 8px;    /* modals, large containers */
```

### Shadows

```
--shadow-card: 0 1px 2px rgba(0,0,0,0.04);
--shadow-elevated: 0 4px 12px rgba(0,0,0,0.08);
--shadow-focus: 0 0 0 2px var(--accent-subtle), 0 0 0 4px var(--accent);
```

### Unique Design Signature

- **Keyboard-first feel**: Visible focus rings, slash-command style search bar
- **Monochrome icons**: No colored icons except status indicators
- **Left-aligned sidebar navigation** with subtle active-state background highlight
- **Horizontal rule separators** instead of card containers for list items
- **Type hierarchy does all the work**: No decorative elements, spacing and weight alone create structure

### CSS Custom Properties

```css
:root[data-theme="scholar"] {
  --bg-primary: #FFFFFF;
  --bg-surface: #F7F7F5;
  --bg-surface-hover: #EFEDEA;
  --text-primary: #1A1A1A;
  --text-secondary: #5C5C5C;
  --text-muted: #9B9B9B;
  --accent: #2F6EEB;
  --accent-hover: #1B5BD4;
  --accent-subtle: #EBF1FD;
  --success: #2EA043;
  --warning: #D4A017;
  --danger: #CF222E;
  --border: #E5E5E3;
  --border-strong: #D0D0CC;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --letter-spacing-tight: -0.02em;
  --letter-spacing-normal: -0.01em;
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --shadow-card: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-elevated: 0 4px 12px rgba(0,0,0,0.08);
}
```

### Fit Analysis

- **Target student**: CS/engineering majors, productivity enthusiasts, students who use Notion daily
- **Light/dark mode**: Designed for light; dark variant possible with `#1A1A1A` bg, `#2A2A28` surface, `#E5E5E3` text
- **Potential problem**: Can feel sterile and impersonal. Lacks the warmth that makes students want to return daily. Risk of "another productivity tool" fatigue.

---

## Theme B: "Campus" -- Warm & Friendly Learning

**Vibe**: Approachable, encouraging, like a well-lit library with wooden tables and warm lamps. Makes studying feel less intimidating.

**Inspiration**: Khan Academy, Duolingo (structure), Headspace (warmth), Apple Education

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#FBF8F3` | Warm off-white page background |
| `--bg-surface` | `#FFFFFF` | Cards pop against warm bg |
| `--bg-surface-hover` | `#F5F0E8` | Card hover |
| `--text-primary` | `#2D2A24` | Warm near-black |
| `--text-secondary` | `#6B6560` | Warm gray body |
| `--text-muted` | `#A8A099` | Warm muted |
| `--accent` | `#E07D3A` | Warm orange -- inviting, energetic |
| `--accent-hover` | `#C96A2E` | Deeper orange |
| `--accent-subtle` | `#FDF0E6` | Orange tint background |
| `--success` | `#3B9B5E` | Earthy green |
| `--warning` | `#D4980A` | Amber |
| `--danger` | `#C53030` | Warm red |
| `--border` | `#E8E2D9` | Warm border |
| `--border-strong` | `#D5CEC4` | Emphasized warm border |

### Typography

```
--font-sans: 'DM Sans', 'Nunito', -apple-system, sans-serif;
--font-display: 'Fraunces', 'Playfair Display', Georgia, serif;
--letter-spacing-tight: -0.01em;
--letter-spacing-normal: 0em;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-bold: 700;
```

Weight distribution: Page titles use `--font-display` at 700, section headings use sans at 600, body at 400. The serif display font adds personality to key headings.

### Border Radius

```
--radius-sm: 8px;    /* generous rounding */
--radius-md: 12px;   /* cards feel soft */
--radius-lg: 16px;   /* modals, hero sections */
```

### Shadows

```
--shadow-card: 0 2px 8px rgba(45,42,36,0.06), 0 1px 2px rgba(45,42,36,0.04);
--shadow-elevated: 0 8px 24px rgba(45,42,36,0.10), 0 2px 8px rgba(45,42,36,0.06);
```

### Unique Design Signature

- **Serif + sans pairing**: Display headings in serif, everything else in rounded sans-serif
- **Warm cream backgrounds** instead of pure white -- reduces eye strain
- **Illustration-friendly**: The warm palette naturally accommodates hand-drawn or flat illustrations
- **Rounded progress indicators**: Pill-shaped progress bars with gentle gradients
- **Subtle texture**: Cards have a barely-visible paper-like noise texture (CSS `background-image` grain)
- **Emoji-native**: Section headers naturally incorporate emoji as visual anchors

### CSS Custom Properties

```css
:root[data-theme="campus"] {
  --bg-primary: #FBF8F3;
  --bg-surface: #FFFFFF;
  --bg-surface-hover: #F5F0E8;
  --text-primary: #2D2A24;
  --text-secondary: #6B6560;
  --text-muted: #A8A099;
  --accent: #E07D3A;
  --accent-hover: #C96A2E;
  --accent-subtle: #FDF0E6;
  --success: #3B9B5E;
  --warning: #D4980A;
  --danger: #C53030;
  --border: #E8E2D9;
  --border-strong: #D5CEC4;
  --font-sans: 'DM Sans', 'Nunito', -apple-system, sans-serif;
  --font-display: 'Fraunces', 'Playfair Display', Georgia, serif;
  --letter-spacing-tight: -0.01em;
  --letter-spacing-normal: 0em;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow-card: 0 2px 8px rgba(45,42,36,0.06), 0 1px 2px rgba(45,42,36,0.04);
  --shadow-elevated: 0 8px 24px rgba(45,42,36,0.10), 0 2px 8px rgba(45,42,36,0.06);
}
```

### Fit Analysis

- **Target student**: Humanities/social science majors, first-year students overwhelmed by college, anyone who finds tech UIs cold
- **Light/dark mode**: Light-only by design. A dark variant would lose the warmth (dark + orange becomes Halloween). Could do a "evening mode" with `#2A2520` bg and muted amber tones.
- **Potential problem**: The warm/friendly aesthetic can read as "not serious" to STEM students. The serif headings add visual interest but increase font loading cost. Orange accent may clash with red danger states if not carefully managed.

---

## Theme C: "Midnight" -- Dark Mode Minimal

**Vibe**: Late-night study session energy. Premium feel, easy on the eyes, makes data and progress indicators pop against the dark canvas.

**Inspiration**: Vercel, Raycast, Linear (dark), Arc Browser, GitHub Dark

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0A0A0B` | Deep near-black background |
| `--bg-surface` | `#141416` | Elevated surface |
| `--bg-surface-hover` | `#1E1E21` | Hover/active state |
| `--text-primary` | `#EDEDEF` | High-contrast headings |
| `--text-secondary` | `#A0A0A6` | Body text |
| `--text-muted` | `#5C5C63` | Subtle labels |
| `--accent` | `#7C6BFF` | Soft purple -- distinctive, not overused |
| `--accent-hover` | `#9588FF` | Lighter on hover (inverse of light mode pattern) |
| `--accent-subtle` | `rgba(124,107,255,0.12)` | Purple tint |
| `--success` | `#3ECF71` | Bright green on dark |
| `--warning` | `#F5A623` | Amber -- high visibility |
| `--danger` | `#EF4444` | Bright red |
| `--border` | `#222226` | Subtle border |
| `--border-strong` | `#333338` | Visible divider |

### Typography

```
--font-sans: 'Geist', 'Inter', -apple-system, sans-serif;
--font-mono: 'Geist Mono', 'JetBrains Mono', monospace;
--letter-spacing-tight: -0.025em;
--letter-spacing-normal: -0.01em;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
```

Weight distribution: Vercel-style tight tracking. Headings at 600 with tight letter-spacing. Body at 400. Everything feels compact and precise.

### Border Radius

```
--radius-sm: 6px;
--radius-md: 8px;
--radius-lg: 12px;
```

### Shadows

```
--shadow-card: 0 0 0 1px var(--border);  /* border-only, no box shadow */
--shadow-elevated: 0 0 0 1px var(--border-strong), 0 8px 24px rgba(0,0,0,0.4);
```

Shadows in dark mode are primarily borders. Traditional drop shadows don't work on dark backgrounds.

### Unique Design Signature

- **Glow effects**: Accent buttons have a subtle `box-shadow: 0 0 20px rgba(124,107,255,0.15)` glow
- **Border-defined cards**: Cards are outlined, not shadowed. `1px solid var(--border)` instead of box-shadow
- **Gradient text** on hero/key headings: `background: linear-gradient(to right, #EDEDEF, #7C6BFF)` with `-webkit-background-clip: text`
- **Dot-grid or subtle noise background**: Barely-visible pattern on `--bg-primary`
- **Neon status indicators**: Success/warning/danger are brighter than in light themes, acting as visual beacons
- **Transparent layering**: Surfaces use slight transparency (`rgba`) so layers feel stacked

### CSS Custom Properties

```css
:root[data-theme="midnight"] {
  --bg-primary: #0A0A0B;
  --bg-surface: #141416;
  --bg-surface-hover: #1E1E21;
  --text-primary: #EDEDEF;
  --text-secondary: #A0A0A6;
  --text-muted: #5C5C63;
  --accent: #7C6BFF;
  --accent-hover: #9588FF;
  --accent-subtle: rgba(124,107,255,0.12);
  --success: #3ECF71;
  --warning: #F5A623;
  --danger: #EF4444;
  --border: #222226;
  --border-strong: #333338;
  --font-sans: 'Geist', 'Inter', -apple-system, sans-serif;
  --font-mono: 'Geist Mono', 'JetBrains Mono', monospace;
  --letter-spacing-tight: -0.025em;
  --letter-spacing-normal: -0.01em;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-card: 0 0 0 1px var(--border);
  --shadow-elevated: 0 0 0 1px var(--border-strong), 0 8px 24px rgba(0,0,0,0.4);
}
```

### Fit Analysis

- **Target student**: Night-owl coders, CS students, anyone who already uses dark mode everywhere. Students who study late and want reduced eye strain.
- **Light/dark mode**: Dark-only. Attempting a light variant of this would be a separate theme entirely (see Theme A).
- **Potential problem**: Studies show light mode increases engagement by 15% in educational apps (vs 25% dark mode boost in entertainment). Students may subconsciously treat a dark-themed study app as entertainment. Purple accent is distinctive but harder to achieve accessible contrast ratios on dark backgrounds -- need to verify WCAG AA (4.5:1 for normal text). `#7C6BFF` on `#141416` = ~5.2:1, passes AA.

---

## Theme D: "Spark" -- Bold & Energetic

**Vibe**: The app that makes you *want* to open it. High energy, playful but not childish, celebrates progress loudly.

**Inspiration**: Figma, Canva, Notion calendar, Spotify (layout energy), Duolingo (gamification)

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#FAFAFA` | Clean light background |
| `--bg-surface` | `#FFFFFF` | Cards |
| `--bg-surface-hover` | `#F0F0F0` | Hover state |
| `--text-primary` | `#111111` | Near-black, high contrast |
| `--text-secondary` | `#555555` | Body |
| `--text-muted` | `#999999` | Labels |
| `--accent` | `#6C47FF` | Electric purple -- Figma-inspired |
| `--accent-hover` | `#5835DB` | Deeper purple |
| `--accent-subtle` | `#F0ECFF` | Light purple tint |
| `--accent-secondary` | `#FF5C8A` | Hot pink for celebration/badges |
| `--accent-tertiary` | `#00C2A8` | Teal for progress/streaks |
| `--success` | `#00C853` | Vivid green |
| `--warning` | `#FF9500` | Bright orange |
| `--danger` | `#FF3B30` | iOS-style red |
| `--border` | `#E5E5E5` | Standard border |
| `--border-strong` | `#CCCCCC` | Dividers |

Note: This theme deliberately uses THREE accent colors. The multi-accent approach creates visual energy and supports gamification (purple = actions, pink = achievements, teal = progress).

### Typography

```
--font-sans: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
--font-mono: 'Fira Code', monospace;
--letter-spacing-tight: -0.03em;    /* aggressive tightening on headings */
--letter-spacing-normal: -0.01em;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-bold: 700;
--font-weight-extra-bold: 800;      /* for hero numbers and stats */
```

Weight distribution: Uses the full weight spectrum. Stats/numbers at 800, headings at 700, subheadings at 500, body at 400. The wide weight range creates strong visual hierarchy.

### Border Radius

```
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-full: 9999px;   /* pill buttons, badges, avatars */
```

### Shadows

```
--shadow-card: 0 2px 4px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
--shadow-elevated: 0 12px 32px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.04);
--shadow-accent: 0 4px 14px rgba(108,71,255,0.25);  /* purple glow on primary buttons */
```

### Unique Design Signature

- **Pill-shaped buttons**: All buttons use `border-radius: 9999px`
- **Multi-color accent system**: Purple primary, pink celebrations, teal progress
- **Bold stat numbers**: GPA, streak count, completion % displayed in extra-bold (800) with large font size
- **Celebration micro-animations**: Confetti/sparkle on milestones (CSS keyframes, not JS)
- **Gradient badges**: Achievement badges use `linear-gradient(135deg, #6C47FF, #FF5C8A)`
- **Card left-side accent bars**: 3px left border in accent color on active/highlighted cards
- **Playful empty states**: Illustrations or emoji for zero-data states

### CSS Custom Properties

```css
:root[data-theme="spark"] {
  --bg-primary: #FAFAFA;
  --bg-surface: #FFFFFF;
  --bg-surface-hover: #F0F0F0;
  --text-primary: #111111;
  --text-secondary: #555555;
  --text-muted: #999999;
  --accent: #6C47FF;
  --accent-hover: #5835DB;
  --accent-subtle: #F0ECFF;
  --accent-secondary: #FF5C8A;
  --accent-tertiary: #00C2A8;
  --success: #00C853;
  --warning: #FF9500;
  --danger: #FF3B30;
  --border: #E5E5E5;
  --border-strong: #CCCCCC;
  --font-sans: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
  --font-mono: 'Fira Code', monospace;
  --letter-spacing-tight: -0.03em;
  --letter-spacing-normal: -0.01em;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  --shadow-card: 0 2px 4px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
  --shadow-elevated: 0 12px 32px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.04);
  --shadow-accent: 0 4px 14px rgba(108,71,255,0.25);
}
```

### Fit Analysis

- **Target student**: Freshmen, social science/business students, anyone motivated by gamification and visual progress. Students who use Canva and Figma.
- **Light/dark mode**: Primarily light. Dark variant works well because the multi-accent colors pop even harder against dark backgrounds.
- **Potential problem**: Three accent colors is a coordination tax. Every new component needs rules for "which accent?". Risk of looking like a children's app if the boldness isn't balanced with enough whitespace. Performance: loading Plus Jakarta Sans at weights 400-800 is ~100kb.

---

## Theme E: "Moss" -- Organic Calm (Wildcard)

**Vibe**: Forest floor after rain. Biophilic design applied to a study app. The antidote to screen fatigue -- feels like studying in a botanical garden.

**Inspiration**: Calm app, Notion Gallery templates, Are.na, muji.com, Japanese stationery design

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#F4F2ED` | Warm stone background |
| `--bg-surface` | `#FAFAF7` | Slightly lifted surface |
| `--bg-surface-hover` | `#ECEADE` | Warm hover |
| `--text-primary` | `#2B3027` | Dark forest green-black |
| `--text-secondary` | `#5A6356` | Muted green-gray |
| `--text-muted` | `#8E9689` | Sage gray |
| `--accent` | `#4A7C59` | Deep moss green |
| `--accent-hover` | `#3D6A4B` | Darker moss |
| `--accent-subtle` | `#E8F0E9` | Green tint |
| `--success` | `#5B9A3C` | Leaf green |
| `--warning` | `#C49A2A` | Warm gold (autumn leaf) |
| `--danger` | `#B84233` | Brick red (earthy) |
| `--border` | `#DDD9D0` | Warm stone border |
| `--border-strong` | `#C7C2B8` | Emphasized border |

### Typography

```
--font-sans: 'Source Sans 3', 'Noto Sans', -apple-system, sans-serif;
--font-display: 'Literata', 'Source Serif 4', Georgia, serif;
--letter-spacing-tight: 0em;        /* relaxed, no tightening */
--letter-spacing-normal: 0.01em;    /* slightly open for readability */
--letter-spacing-wide: 0.08em;      /* labels and captions */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
```

Weight distribution: Deliberately restrained. Nothing above 600. The calm vibe demands light typographic touch. Labels use small caps with wide letter-spacing.

### Border Radius

```
--radius-sm: 4px;    /* subtle rounding */
--radius-md: 8px;
--radius-lg: 12px;
```

### Shadows

```
--shadow-card: none;    /* no shadows -- borders only */
--shadow-elevated: 0 4px 16px rgba(43,48,39,0.08);
```

The near-shadowless design is intentional. Cards are defined by background color difference against `--bg-primary`, not by elevation. This creates a flatter, calmer visual rhythm.

### Unique Design Signature

- **Small-caps labels**: Category labels and section headers use `font-variant: small-caps` with wide letter-spacing
- **Borderless cards**: Cards distinguished by background color, not borders or shadows
- **Nature-derived color naming** in code: `--moss`, `--stone`, `--bark`, `--leaf` aliases
- **Generous whitespace**: Padding and margins are 1.5x the typical SaaS spacing
- **Muted iconography**: Icons at 50% opacity by default, full opacity on hover
- **Serif headings for long-form content**: Study notes, summaries rendered in the serif display font for a book-like reading experience
- **Horizontal rhythm**: Content areas use a visible or implied grid with wide gutters

### CSS Custom Properties

```css
:root[data-theme="moss"] {
  --bg-primary: #F4F2ED;
  --bg-surface: #FAFAF7;
  --bg-surface-hover: #ECEADE;
  --text-primary: #2B3027;
  --text-secondary: #5A6356;
  --text-muted: #8E9689;
  --accent: #4A7C59;
  --accent-hover: #3D6A4B;
  --accent-subtle: #E8F0E9;
  --success: #5B9A3C;
  --warning: #C49A2A;
  --danger: #B84233;
  --border: #DDD9D0;
  --border-strong: #C7C2B8;
  --font-sans: 'Source Sans 3', 'Noto Sans', -apple-system, sans-serif;
  --font-display: 'Literata', 'Source Serif 4', Georgia, serif;
  --letter-spacing-tight: 0em;
  --letter-spacing-normal: 0.01em;
  --letter-spacing-wide: 0.08em;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --shadow-card: none;
  --shadow-elevated: 0 4px 16px rgba(43,48,39,0.08);
}
```

### Fit Analysis

- **Target student**: Stressed-out students who need calm. Pre-med, grad students, anyone studying 6+ hours/day who wants their tools to not add visual noise. Also appeals to design/architecture students.
- **Light/dark mode**: Light only. The entire palette is built on warm earth tones that lose meaning in dark mode. A dark variant would need to be a completely separate "night forest" palette (`#1A1F1B` bg, `#2A332C` surface).
- **Potential problem**: Green accent on green-tinted backgrounds demands careful contrast checking. `#4A7C59` on `#FAFAF7` = ~4.6:1, barely passes WCAG AA for normal text. May need to darken to `#3D6A4B` for body text links. The relaxed spacing means less content fits per screen -- not ideal for information-dense views like grade tables.

---

## Comparison Matrix

| Dimension | Scholar | Campus | Midnight | Spark | Moss |
|-----------|---------|--------|----------|-------|------|
| **Mood** | Professional | Welcoming | Premium | Energetic | Calm |
| **Density** | High | Medium | High | Medium | Low |
| **Font load** | ~40kb | ~80kb | ~50kb | ~100kb | ~60kb |
| **Accessibility** | Excellent | Good | Good* | Good | Borderline* |
| **Dark mode** | Variant possible | Not natural | Native | Variant possible | Not natural |
| **Gamification fit** | Low | Medium | Medium | High | Low |
| **Study session fit** | Excellent | Good | Excellent | Fair | Excellent |
| **First impression** | "Serious tool" | "Friendly tutor" | "Premium tech" | "Fun app" | "Mindful space" |

*Midnight: Purple on dark needs careful tuning. Moss: Green-on-warm requires contrast verification.

## Recommendation

For a college course management platform, **start with Theme A (Scholar) as the default, with Theme C (Midnight) as the dark mode**. This covers the widest audience -- students expect productivity tools to look like productivity tools.

Then offer Theme D (Spark) as an opt-in "fun mode" for students who want gamification energy, and Theme E (Moss) for students who want a calming study environment.

Theme B (Campus) is best kept as a seasonal/onboarding variant rather than a permanent option -- its warmth is great for first impressions but may feel too casual for daily power users.

## Implementation Strategy

1. Define all CSS custom properties under `[data-theme="X"]` selectors
2. Store user's theme preference in localStorage and Supabase profile
3. Load theme on page init from `document.documentElement.dataset.theme`
4. Shared component library references ONLY CSS variables, never hard-coded colors
5. Theme switching is a single `dataset.theme` change -- no component re-renders needed
