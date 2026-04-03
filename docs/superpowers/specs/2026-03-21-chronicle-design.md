# Chronicle (岁月史书) — Design Spec

## Overview

A personal knowledge management system built as a **semantic zoom canvas**. Users navigate their entire knowledge landscape — learning, projects, health, ideas — by zooming in and out of a single infinite plane, like a map. Content density changes with zoom level: zoomed out shows domain bubbles, zoomed in reveals full documents.

**Not** a note-taking app. Not a mind map tool. It is an infinite, zoomable knowledge map where information lives spatially and AI continuously enriches it.

## Core Interaction: Semantic Zoom

The single most important feature. Everything else is built on top of this.

### Zoom Levels

| Level | Scale | What You See |
|-------|-------|-------------|
| L0 — Overview | Fully zoomed out | Domain bubbles: "Learning", "Projects", "Health", "Ideas". Each shows a label, a color dot, and a count (e.g., "12 topics"). Connections between domains visible as faint lines. |
| L1 — Domain | Medium zoom | Sub-topics within a domain. "Learning" expands to show "Math Competition", "CS Courses", "Paper Reading". Each is a card with title + 1-line summary. |
| L2 — Topic | Closer zoom | Individual items as preview cards: title + first few lines + metadata. Enough to understand what each item is without opening it. |
| L3 — Document | Fully zoomed in | Full document rendered in-place on the canvas. Readable, editable. The document IS the canvas at this zoom level. Surrounding sibling nodes are visible but smaller and faded. |

### Transition Behavior

- Transitions are **continuous**, not stepped. Content fades in/out smoothly as you zoom.
- At intermediate zoom levels, elements crossfade between representations (e.g., a bubble morphing into a card).
- Pan and zoom via trackpad/scroll wheel. Pinch-to-zoom on touch devices.
- The viewport remembers your last position, persisted to Supabase (`user_settings` table). Reopening the app lands you where you left off.

### Spatial Layout

- Nodes are positioned by the user via drag-and-drop. Positions are persistent.
- New nodes get auto-placed near their parent: offset +200px right from parent center. If that space is occupied, spiral outward until clear.
- No forced grid or tree layout. Freeform spatial positioning — the user decides what goes where.
- Connections between nodes are optional, user-drawn lines (Phase 2).

### Node Creation Flow

- **Double-click empty canvas** → creates a new node at that position. A minimal inline form appears: text field for title, type selector (domain/topic/document). If you double-click inside an existing domain at L1, the new node auto-assigns that domain as `parent_id` and defaults to type `topic`. Similarly inside a topic, defaults to `document`.
- **Toolbar "+" button** → same flow, but node is placed at viewport center.
- Title is the only required field at creation. Content, summary, color are all optional and can be added later.
- Pressing Enter confirms, Escape cancels. No modal.

### Search

- Search bar in the toolbar (Cmd+K to focus).
- Fuzzy search against node titles and content (Supabase full-text search with `tsvector`).
- Results appear as a dropdown list below the search bar. Each result shows: title, type icon (Lucide), parent path (e.g., "Learning > Math").
- Clicking a result animates the viewport to center and zoom into that node (same as double-click zoom-to-fit).
- Search is local-first: Zustand store is searched instantly, Supabase query runs in parallel for completeness.

### Keyboard Shortcuts (Phase 1)

- `Cmd+K` — focus search
- `Delete/Backspace` — delete selected node (with confirmation)
- `Cmd+Z` / `Cmd+Shift+Z` — undo / redo (node moves, creates, deletes)
- `+` / `-` — zoom in / out
- `0` — zoom to fit all nodes
- `Escape` — deselect / cancel editing
- Arrow keys — pan viewport

## Visual Design: Soft Depth

Warm, refined, modern. Not flat, not skeuomorphic — layered with subtle depth.

### Palette

- **Background**: Warm off-white (#f8f6f1) with fine dot grid overlay (opacity ~15%)
- **Cards/Nodes**: Near-white (#fffefc) with layered box-shadows for floating effect
- **Text**: Deep warm brown (#1a1814) for headings, muted (#9a9080) for secondary
- **Accent**: Muted gold (#c4a97d) for separators, active states, highlights
- **Domain colors**: Each domain gets a subtle dot color (gold, sage green, slate blue, etc.) — never garish, always muted
- **Depth**: Soft radial gradient blobs on the background, subtle and slow-moving

### Typography

- System UI font stack (no custom fonts loaded initially)
- Headings: weight 500-600, subtle letter-spacing
- Body: weight 400, generous line-height (1.7-1.8)
- Labels: 10px uppercase with letter-spacing for metadata

### Rules

- **No emoji anywhere in the UI.** Use Lucide icons or plain text only.
- No harsh borders. Use shadows and subtle background differences for separation.
- No bright/saturated colors. Everything muted and warm.

## Data Model (Supabase)

### Core Tables

**nodes**
- `id` (uuid, PK)
- `user_id` (uuid, FK → auth.users)
- `parent_id` (uuid, nullable, FK → nodes) — for hierarchical grouping
- `type` (enum: 'domain', 'topic', 'document')
- `title` (text)
- `content` (text, nullable) — markdown content for documents
- `summary` (text, nullable) — AI-generated or user-written preview
- `position_x` (float) — spatial position on canvas
- `position_y` (float)
- `color` (text, nullable) — accent color code
- `metadata` (jsonb) — extensible metadata (source URL, tags, etc.)
- `created_at`, `updated_at` (timestamptz)

**user_settings**
- `user_id` (uuid, PK, FK → auth.users)
- `viewport_x` (float) — last viewport position
- `viewport_y` (float)
- `viewport_zoom` (float)
- `updated_at` (timestamptz)

**undo_history** (client-side only, not persisted to Supabase)
- Managed in Zustand as a stack of actions (create/delete/move/edit). Max 50 entries.

### Tables Deferred to Later Phases

`connections` (Phase 2), `feed_preferences`, `feed_items` (Phase 3) — schemas will be defined when those phases are designed.

### Row-Level Security (RLS)

All tables enforce RLS. Policies:
- `nodes`: Users can only SELECT, INSERT, UPDATE, DELETE rows where `user_id = auth.uid()`.
- `user_settings`: Users can only access their own row (`user_id = auth.uid()`).
- No public/anonymous access. All operations require authentication.

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | Next.js 14+ (App Router) | Consistent with user's other projects (TOEFL, ai-text-detector) |
| Canvas Rendering | HTML Canvas API + custom zoom engine | PixiJS/WebGL is overkill for initial scope. Start with Canvas 2D, upgrade if perf demands |
| State Management | Zustand | Lightweight, fits canvas state well (viewport position, zoom level, selected node) |
| Database | Supabase (PostgreSQL) | Auth, realtime, storage, edge functions — all-in-one |
| Styling | Tailwind CSS | For UI chrome (toolbar, panels). Canvas content is rendered programmatically |
| Icons | Lucide React | Clean, consistent, no emoji |
| Deployment | Vercel | Seamless Next.js deploy, user's existing platform |

## Phase 1 Scope: Semantic Zoom Canvas

Phase 1 delivers the core experience: an infinite canvas you can zoom in/out of, with nodes at different hierarchical levels.

### What's In

- Canvas with pan and zoom (trackpad + scroll wheel)
- Semantic zoom: 4 levels of detail (L0-L3)
- Create, edit, delete, move nodes
- Node types: domain, topic, document
- Document editing at L3 (basic markdown → rendered)
- Supabase auth (email/password or magic link)
- Data persistence (nodes, positions, content)
- Responsive (works on desktop browsers, tablet is stretch)

### What's Out (Future Phases)

- Auto information aggregation (Phase 3)
- AI chat / dialogue with canvas (Phase 4)
- Connections/lines between nodes (Phase 2)
- Mobile-optimized experience
- Collaboration / multi-user editing
- Export / import

### Key Technical Challenges

1. **Canvas performance at scale**: Hundreds or thousands of nodes need efficient culling — only render what's in the viewport. Quadtree spatial index for hit testing and visibility.

2. **Smooth semantic transitions**: Cross-fading between zoom levels needs careful interpolation. Each node calculates its current "representation" based on viewport zoom level and renders accordingly.

3. **Rich text on canvas**: Canvas API doesn't natively support rich text. At L3 (document level), we overlay a DOM-based editor (Tiptap) positioned over the canvas node's bounding box. See "Editor Overlay Contract" below.

4. **Zoom-to-fit**: Double-clicking a node should smoothly animate the viewport to center and zoom into that node. Needs eased animation curves.

### Editor Overlay Contract

When the user clicks a document node at L3 zoom:
1. Canvas stops rendering that node's content (draws only a transparent placeholder with matching bounds).
2. A DOM-positioned Tiptap editor appears, absolutely positioned to match the canvas node's screen coordinates.
3. As the user pans/zooms while editing, the overlay repositions in real-time via `requestAnimationFrame` sync with the canvas viewport transform.
4. Content auto-saves via debounce (1.5s after last keystroke) to Zustand, then syncs to Supabase.
5. If the user zooms out past L2 threshold while editing: auto-save triggers, editor dismisses, node reverts to canvas-rendered preview.
6. Clicking outside the editor or pressing Escape: same — save and dismiss.

### Data Sync Strategy

- **Optimistic updates**: All changes apply to Zustand immediately. Supabase sync is debounced (2s).
- **Failure handling**: If Supabase write fails, a subtle toast appears ("Changes saved locally, sync pending"). Retry with exponential backoff (3 attempts). Data remains in Zustand until successful sync.
- **Tab close protection**: `beforeunload` event checks for unsynced changes and warns the user.
- **No offline mode in Phase 1**: The app requires initial data load from Supabase. After load, it works with local state and syncs back.

### Performance Target

Phase 1 targets **smooth interaction with up to 500 nodes**. Canvas 2D with quadtree culling is sufficient for this scale. If usage grows beyond 1,000 nodes, WebGL upgrade path is available but not designed in Phase 1.

### Minimap

- Always visible in bottom-right corner, 160x120px.
- Shows all nodes as colored dots proportional to their type (domains larger, documents smaller).
- Current viewport shown as a semi-transparent rectangle.
- Click anywhere on minimap → viewport animates to that position (ease-out, 300ms).

## Architecture

```
┌─────────────────────────────────────────────┐
│                  Next.js App                 │
│                                              │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐ │
│  │ Canvas   │  │ UI Chrome │  │ Editor    │ │
│  │ Renderer │  │ (Toolbar, │  │ Overlay   │ │
│  │          │  │  Minimap) │  │ (Tiptap)  │ │
│  └────┬─────┘  └─────┬─────┘  └─────┬─────┘ │
│       │              │              │        │
│  ┌────┴──────────────┴──────────────┴────┐   │
│  │         Zustand Store                  │   │
│  │  - viewport (x, y, zoom)              │   │
│  │  - nodes (Map<id, Node>)              │   │
│  │  - selectedNode                       │   │
│  │  - editingNode                        │   │
│  └────────────────┬───────────────────────┘   │
│                   │                           │
│  ┌────────────────┴───────────────────────┐   │
│  │         Supabase Client                │   │
│  │  - Auth, Realtime, CRUD               │   │
│  └────────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Key Components

- **CanvasRenderer**: Manages the HTML Canvas element. Handles pan/zoom input, renders nodes based on current viewport. Uses requestAnimationFrame loop. Implements spatial culling.
- **NodeRenderer**: Given a node + current zoom level, returns the appropriate visual representation (bubble → card → preview → full content).
- **EditorOverlay**: A positioned DOM element that appears over a node when zoomed to L3 and the user clicks to edit. Uses Tiptap for markdown editing.
- **Minimap**: Small overview in the corner showing your current viewport position relative to all nodes. Click to jump.
- **Toolbar**: Top bar with controls — add node, zoom controls, search, settings.
- **ZustandStore**: Single source of truth for viewport state, node data, UI state. Syncs to Supabase on changes (debounced).
