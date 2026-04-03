# Chronicle Phase 1 — Semantic Zoom Canvas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an infinite semantic zoom canvas where users navigate their knowledge landscape by zooming in/out — from domain bubbles down to full editable documents — all on a single plane.

**Architecture:** Next.js App Router serves a single-page canvas app. Canvas 2D handles rendering with a custom viewport transform (pan/zoom). Zustand manages all client state (viewport, nodes, selection, undo). Supabase provides auth, PostgreSQL storage with RLS, and debounced sync. A Tiptap DOM overlay handles rich text editing at L3 zoom. A quadtree provides spatial indexing for culling and hit-testing.

**Tech Stack:** Next.js 15+ (App Router), TypeScript, Canvas 2D API, Zustand, Supabase (auth + DB), Tiptap, Tailwind CSS, Lucide React

**Spec:** `docs/superpowers/specs/2026-03-21-chronicle-design.md`

---

## File Structure

```
chronicle/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── postcss.config.mjs
├── .env.local                      # NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
├── .gitignore
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql  # nodes, user_settings tables + RLS
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout, fonts, metadata
│   │   ├── globals.css             # Tailwind imports + custom canvas styles
│   │   ├── page.tsx                # Landing/auth gate → redirect to /canvas
│   │   ├── login/
│   │   │   └── page.tsx            # Login/signup page
│   │   └── canvas/
│   │       ├── layout.tsx          # Auth guard wrapper
│   │       └── page.tsx            # Canvas page — mounts CanvasApp
│   ├── components/
│   │   ├── CanvasApp.tsx           # Top-level: canvas + toolbar + minimap + editor overlay
│   │   ├── CanvasRenderer.tsx      # Canvas element, rAF loop, pan/zoom input
│   │   ├── Toolbar.tsx             # Top bar: add node, zoom, search, user menu
│   │   ├── SearchBar.tsx           # Cmd+K search with dropdown results
│   │   ├── Minimap.tsx             # Bottom-right minimap with viewport indicator
│   │   ├── EditorOverlay.tsx       # Tiptap editor positioned over canvas node
│   │   ├── NodeCreationForm.tsx    # Inline form for creating nodes (title + type)
│   │   ├── DeleteConfirmation.tsx  # Simple confirmation dialog for node deletion
│   │   └── Toast.tsx               # Minimal toast for sync status
│   ├── canvas/
│   │   ├── viewport.ts            # Viewport transform: screen↔world coords, zoom limits
│   │   ├── render.ts              # Main render function: clear, draw bg, draw nodes
│   │   ├── node-renderer.ts       # Draw a single node at current zoom level (L0-L3)
│   │   ├── hit-test.ts            # Click/double-click → which node was hit
│   │   ├── quadtree.ts            # Spatial index for culling + hit testing
│   │   ├── animation.ts           # Smooth viewport animations (zoom-to-fit, ease curves)
│   │   ├── auto-place.ts          # Auto-placement: offset from parent, spiral if occupied
│   │   └── constants.ts           # Zoom thresholds, node sizes, colors, grid config
│   ├── store/
│   │   ├── canvas-store.ts        # Zustand: viewport, nodes, selection, editing state
│   │   ├── undo-store.ts          # Undo/redo stack (max 50 actions)
│   │   └── sync.ts                # Debounced Supabase sync, beforeunload guard
│   ├── lib/
│   │   ├── supabase-browser.ts    # Supabase browser client singleton
│   │   ├── supabase-server.ts     # Supabase server client (for auth guard)
│   │   └── types.ts               # Node, NodeType, UserSettings, UndoAction types
│   └── hooks/
│       ├── useCanvasInput.ts      # Mouse/trackpad/keyboard event handlers
│       ├── useKeyboardShortcuts.ts # Cmd+K, Delete, Cmd+Z, arrows, +/-, 0, Esc
│       └── useAutoSave.ts         # Debounced save to Supabase with retry
```

---

## Task 1: Project Scaffold + Supabase Schema

**Files:**
- Create: `chronicle/` (entire scaffold via `create-next-app`)
- Create: `chronicle/supabase/migrations/001_initial_schema.sql`
- Create: `chronicle/src/lib/types.ts`
- Create: `chronicle/src/lib/supabase-browser.ts`
- Create: `chronicle/.env.local`

- [ ] **Step 1: Scaffold Next.js project**

```bash
cd "/Users/shaoq/Desktop/VScode Workspace"
npx create-next-app@latest chronicle --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
```

- [ ] **Step 2: Install dependencies**

```bash
cd chronicle
npm install zustand @supabase/supabase-js @supabase/ssr lucide-react @tiptap/react @tiptap/starter-kit @tiptap/extension-placeholder
```

- [ ] **Step 3: Create TypeScript types**

Write `src/lib/types.ts`:

```typescript
export type NodeType = 'domain' | 'topic' | 'document';

export interface ChronicleNode {
  id: string;
  user_id: string;
  parent_id: string | null;
  type: NodeType;
  title: string;
  content: string | null;
  summary: string | null;
  position_x: number;
  position_y: number;
  color: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface UserSettings {
  user_id: string;
  viewport_x: number;
  viewport_y: number;
  viewport_zoom: number;
  updated_at: string;
}

export type UndoActionType = 'create' | 'delete' | 'move' | 'edit';

export interface UndoAction {
  type: UndoActionType;
  nodeId: string;
  before: Partial<ChronicleNode> | null;
  after: Partial<ChronicleNode> | null;
  timestamp: number;
}

export interface Viewport {
  x: number;
  y: number;
  zoom: number;
}
```

- [ ] **Step 4: Create Supabase migration**

Write `supabase/migrations/001_initial_schema.sql`:

```sql
-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Nodes table
create table public.nodes (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  parent_id uuid references public.nodes(id) on delete set null,
  type text not null check (type in ('domain', 'topic', 'document')),
  title text not null,
  content text,
  summary text,
  position_x float not null default 0,
  position_y float not null default 0,
  color text,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Full-text search index
alter table public.nodes add column fts tsvector
  generated always as (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))) stored;
create index nodes_fts_idx on public.nodes using gin(fts);

-- Spatial query index
create index nodes_user_idx on public.nodes(user_id);
create index nodes_parent_idx on public.nodes(parent_id);

-- User settings table
create table public.user_settings (
  user_id uuid primary key references auth.users(id) on delete cascade,
  viewport_x float not null default 0,
  viewport_y float not null default 0,
  viewport_zoom float not null default 1,
  updated_at timestamptz not null default now()
);

-- RLS policies
alter table public.nodes enable row level security;
alter table public.user_settings enable row level security;

create policy "Users can CRUD own nodes"
  on public.nodes for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "Users can CRUD own settings"
  on public.user_settings for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Auto-update updated_at
create or replace function public.update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger nodes_updated_at
  before update on public.nodes
  for each row execute function public.update_updated_at();

create trigger user_settings_updated_at
  before update on public.user_settings
  for each row execute function public.update_updated_at();
```

- [ ] **Step 5: Create Supabase browser client**

Write `src/lib/supabase-browser.ts`:

```typescript
import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

- [ ] **Step 6: Create `.env.local` template**

```
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

- [ ] **Step 7: Verify build**

```bash
npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 8: Commit**

```bash
git add package.json tsconfig.json next.config.ts tailwind.config.ts postcss.config.mjs .gitignore .env.local supabase/ src/lib/types.ts src/lib/supabase-browser.ts src/app/
git commit -m "feat: scaffold Chronicle project with Supabase schema and types"
```

---

## Task 2: Canvas Constants + Viewport Transform

**Files:**
- Create: `src/canvas/constants.ts`
- Create: `src/canvas/viewport.ts`

- [ ] **Step 1: Create canvas constants**

Write `src/canvas/constants.ts`:

```typescript
// Zoom level thresholds (continuous, these are transition boundaries)
export const ZOOM_L0_MAX = 0.3;   // Below: pure bubbles
export const ZOOM_L1_MIN = 0.3;
export const ZOOM_L1_MAX = 0.8;   // Domain cards
export const ZOOM_L2_MIN = 0.8;
export const ZOOM_L2_MAX = 2.0;   // Preview cards
export const ZOOM_L3_MIN = 2.0;   // Full document

export const ZOOM_MIN = 0.05;
export const ZOOM_MAX = 8.0;
export const ZOOM_SPEED = 0.002;

// Node sizes (in world units)
export const NODE_BUBBLE_RADIUS = 60;
export const NODE_CARD_WIDTH = 220;
export const NODE_CARD_HEIGHT = 140;
export const NODE_PREVIEW_WIDTH = 320;
export const NODE_PREVIEW_HEIGHT = 240;
export const NODE_DOCUMENT_WIDTH = 600;
export const NODE_DOCUMENT_HEIGHT = 800;

// Visual
export const BG_COLOR = '#f8f6f1';
export const CARD_BG = '#fffefc';
export const TEXT_PRIMARY = '#1a1814';
export const TEXT_SECONDARY = '#9a9080';
export const ACCENT_GOLD = '#c4a97d';
export const DOT_GRID_COLOR = '#b0a890';
export const DOT_GRID_SIZE = 20;
export const DOT_GRID_OPACITY = 0.15;
export const DOT_GRID_RADIUS = 0.5;

// Domain colors (muted)
export const DOMAIN_COLORS = [
  '#c4a97d', // gold
  '#7d9c8a', // sage green
  '#8a9cb8', // slate blue
  '#b89c7d', // warm brown
  '#9c7d8a', // dusty rose
  '#7db8a0', // teal
];

// Animation
export const ANIMATION_DURATION_MS = 300;
export const EASE_OUT = (t: number) => 1 - Math.pow(1 - t, 3);

// Auto-placement
export const AUTO_PLACE_OFFSET_X = 200;
export const SPIRAL_STEP = 80;
```

- [ ] **Step 2: Create viewport module**

Write `src/canvas/viewport.ts`:

```typescript
import { Viewport } from '@/lib/types';
import { ZOOM_MIN, ZOOM_MAX, ZOOM_SPEED } from './constants';

export function screenToWorld(
  screenX: number,
  screenY: number,
  viewport: Viewport,
  canvasWidth: number,
  canvasHeight: number
): { x: number; y: number } {
  return {
    x: (screenX - canvasWidth / 2) / viewport.zoom + viewport.x,
    y: (screenY - canvasHeight / 2) / viewport.zoom + viewport.y,
  };
}

export function worldToScreen(
  worldX: number,
  worldY: number,
  viewport: Viewport,
  canvasWidth: number,
  canvasHeight: number
): { x: number; y: number } {
  return {
    x: (worldX - viewport.x) * viewport.zoom + canvasWidth / 2,
    y: (worldY - viewport.y) * viewport.zoom + canvasHeight / 2,
  };
}

export function getVisibleBounds(
  viewport: Viewport,
  canvasWidth: number,
  canvasHeight: number
): { minX: number; minY: number; maxX: number; maxY: number } {
  const halfW = canvasWidth / 2 / viewport.zoom;
  const halfH = canvasHeight / 2 / viewport.zoom;
  return {
    minX: viewport.x - halfW,
    minY: viewport.y - halfH,
    maxX: viewport.x + halfW,
    maxY: viewport.y + halfH,
  };
}

export function clampZoom(zoom: number): number {
  return Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoom));
}

export function applyZoomDelta(
  viewport: Viewport,
  delta: number,
  pivotScreenX: number,
  pivotScreenY: number,
  canvasWidth: number,
  canvasHeight: number
): Viewport {
  const newZoom = clampZoom(viewport.zoom * Math.exp(-delta * ZOOM_SPEED));
  // Zoom toward cursor position
  const worldBefore = screenToWorld(pivotScreenX, pivotScreenY, viewport, canvasWidth, canvasHeight);
  const worldAfter = screenToWorld(pivotScreenX, pivotScreenY, { ...viewport, zoom: newZoom }, canvasWidth, canvasHeight);
  return {
    x: viewport.x + (worldBefore.x - worldAfter.x),
    y: viewport.y + (worldBefore.y - worldAfter.y),
    zoom: newZoom,
  };
}

export function getZoomLevel(zoom: number): 0 | 1 | 2 | 3 {
  if (zoom < 0.3) return 0;
  if (zoom < 0.8) return 1;
  if (zoom < 2.0) return 2;
  return 3;
}
```

- [ ] **Step 3: Commit**

```bash
git add src/canvas/constants.ts src/canvas/viewport.ts
git commit -m "feat: canvas viewport transform and visual constants"
```

---

## Task 3: Quadtree Spatial Index

**Files:**
- Create: `src/canvas/quadtree.ts`

- [ ] **Step 1: Implement quadtree**

Write `src/canvas/quadtree.ts`:

```typescript
export interface Rect {
  x: number;      // center x
  y: number;      // center y
  width: number;
  height: number;
}

interface QuadtreeItem {
  id: string;
  bounds: Rect;
}

const MAX_ITEMS = 8;
const MAX_DEPTH = 8;

export class Quadtree {
  private items: QuadtreeItem[] = [];
  private children: Quadtree[] | null = null;

  constructor(
    private bounds: Rect,
    private depth: number = 0
  ) {}

  clear(): void {
    this.items = [];
    this.children = null;
  }

  insert(item: QuadtreeItem): void {
    if (this.children) {
      const idx = this.getIndex(item.bounds);
      if (idx !== -1) {
        this.children[idx].insert(item);
        return;
      }
    }
    this.items.push(item);
    if (this.items.length > MAX_ITEMS && this.depth < MAX_DEPTH && !this.children) {
      this.subdivide();
      const remaining: QuadtreeItem[] = [];
      for (const it of this.items) {
        const idx = this.getIndex(it.bounds);
        if (idx !== -1) {
          this.children![idx].insert(it);
        } else {
          remaining.push(it);
        }
      }
      this.items = remaining;
    }
  }

  query(range: Rect): QuadtreeItem[] {
    const found: QuadtreeItem[] = [];
    if (!this.intersects(range)) return found;
    for (const item of this.items) {
      if (this.rectIntersects(item.bounds, range)) {
        found.push(item);
      }
    }
    if (this.children) {
      for (const child of this.children) {
        found.push(...child.query(range));
      }
    }
    return found;
  }

  private subdivide(): void {
    const { x, y, width, height } = this.bounds;
    const hw = width / 2;
    const hh = height / 2;
    this.children = [
      new Quadtree({ x: x - hw / 2, y: y - hh / 2, width: hw, height: hh }, this.depth + 1),
      new Quadtree({ x: x + hw / 2, y: y - hh / 2, width: hw, height: hh }, this.depth + 1),
      new Quadtree({ x: x - hw / 2, y: y + hh / 2, width: hw, height: hh }, this.depth + 1),
      new Quadtree({ x: x + hw / 2, y: y + hh / 2, width: hw, height: hh }, this.depth + 1),
    ];
  }

  private getIndex(rect: Rect): number {
    const cx = this.bounds.x;
    const cy = this.bounds.y;
    const left = rect.x - rect.width / 2;
    const right = rect.x + rect.width / 2;
    const top = rect.y - rect.height / 2;
    const bottom = rect.y + rect.height / 2;

    const fitsTop = top < cy && bottom < cy;
    const fitsBottom = top > cy;
    const fitsLeft = left < cx && right < cx;
    const fitsRight = left > cx;

    if (fitsLeft && fitsTop) return 0;
    if (fitsRight && fitsTop) return 1;
    if (fitsLeft && fitsBottom) return 2;
    if (fitsRight && fitsBottom) return 3;
    return -1;
  }

  private intersects(range: Rect): boolean {
    return this.rectIntersects(this.bounds, range);
  }

  private rectIntersects(a: Rect, b: Rect): boolean {
    return !(
      a.x - a.width / 2 > b.x + b.width / 2 ||
      a.x + a.width / 2 < b.x - b.width / 2 ||
      a.y - a.height / 2 > b.y + b.height / 2 ||
      a.y + a.height / 2 < b.y - b.height / 2
    );
  }
}
```

- [ ] **Step 2: Implement auto-placement**

Write `src/canvas/auto-place.ts`:

```typescript
import { ChronicleNode } from '@/lib/types';
import { AUTO_PLACE_OFFSET_X, SPIRAL_STEP, NODE_CARD_WIDTH } from './constants';

export function findAutoPlacePosition(
  parentX: number,
  parentY: number,
  existingNodes: ChronicleNode[],
): { x: number; y: number } {
  let x = parentX + AUTO_PLACE_OFFSET_X;
  let y = parentY;
  let angle = 0;
  let radius = 0;

  for (let attempt = 0; attempt < 50; attempt++) {
    const occupied = existingNodes.some(
      (n) => Math.abs(n.position_x - x) < NODE_CARD_WIDTH && Math.abs(n.position_y - y) < NODE_CARD_WIDTH
    );
    if (!occupied) return { x, y };
    // Spiral outward
    angle += 0.8;
    radius += SPIRAL_STEP / (2 * Math.PI);
    x = parentX + AUTO_PLACE_OFFSET_X + Math.cos(angle) * radius;
    y = parentY + Math.sin(angle) * radius;
  }
  return { x, y };
}
```

- [ ] **Step 3: Add `getNodePath` helper to canvas store**

Add this function to `src/store/canvas-store.ts`:

```typescript
// Add to the store interface and implementation:
getNodePath: (nodeId: string) => string;

// Implementation:
getNodePath: (nodeId) => {
  const parts: string[] = [];
  let current = get().nodes.get(nodeId);
  while (current) {
    parts.unshift(current.title);
    current = current.parent_id ? get().nodes.get(current.parent_id) : undefined;
  }
  return parts.join(' > ');
},
```

- [ ] **Step 4: Commit**

```bash
git add src/canvas/quadtree.ts src/canvas/auto-place.ts src/store/canvas-store.ts
git commit -m "feat: quadtree spatial index, auto-placement, and node path helper"
```

---

## Task 4: Zustand Store (Canvas State + Undo)

**Files:**
- Create: `src/store/canvas-store.ts`
- Create: `src/store/undo-store.ts`

- [ ] **Step 1: Create canvas store**

Write `src/store/canvas-store.ts`:

```typescript
import { create } from 'zustand';
import { ChronicleNode, Viewport, NodeType } from '@/lib/types';

interface CanvasState {
  // Viewport
  viewport: Viewport;
  setViewport: (v: Viewport) => void;

  // Nodes
  nodes: Map<string, ChronicleNode>;
  setNodes: (nodes: ChronicleNode[]) => void;
  addNode: (node: ChronicleNode) => void;
  updateNode: (id: string, updates: Partial<ChronicleNode>) => void;
  deleteNode: (id: string) => void;
  getNode: (id: string) => ChronicleNode | undefined;
  getChildNodes: (parentId: string) => ChronicleNode[];
  getChildCount: (parentId: string) => number;

  // Selection
  selectedNodeId: string | null;
  setSelectedNodeId: (id: string | null) => void;

  // Editing
  editingNodeId: string | null;
  setEditingNodeId: (id: string | null) => void;

  // Creating
  creatingAt: { x: number; y: number; parentId: string | null; defaultType: NodeType } | null;
  setCreatingAt: (pos: { x: number; y: number; parentId: string | null; defaultType: NodeType } | null) => void;

  // Dirty tracking for sync
  dirtyNodeIds: Set<string>;
  markDirty: (id: string) => void;
  clearDirty: (ids: string[]) => void;
}

export const useCanvasStore = create<CanvasState>((set, get) => ({
  viewport: { x: 0, y: 0, zoom: 0.5 },
  setViewport: (v) => set({ viewport: v }),

  nodes: new Map(),
  setNodes: (nodes) => set({ nodes: new Map(nodes.map((n) => [n.id, n])) }),
  addNode: (node) =>
    set((s) => {
      const next = new Map(s.nodes);
      next.set(node.id, node);
      return { nodes: next };
    }),
  updateNode: (id, updates) =>
    set((s) => {
      const node = s.nodes.get(id);
      if (!node) return s;
      const next = new Map(s.nodes);
      next.set(id, { ...node, ...updates });
      return { nodes: next };
    }),
  deleteNode: (id) =>
    set((s) => {
      const next = new Map(s.nodes);
      next.delete(id);
      return { nodes: next };
    }),
  getNode: (id) => get().nodes.get(id),
  getChildNodes: (parentId) =>
    Array.from(get().nodes.values()).filter((n) => n.parent_id === parentId),
  getChildCount: (parentId) =>
    Array.from(get().nodes.values()).filter((n) => n.parent_id === parentId).length,

  selectedNodeId: null,
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),

  editingNodeId: null,
  setEditingNodeId: (id) => set({ editingNodeId: id }),

  creatingAt: null,
  setCreatingAt: (pos) => set({ creatingAt: pos }),

  dirtyNodeIds: new Set(),
  markDirty: (id) =>
    set((s) => {
      const next = new Set(s.dirtyNodeIds);
      next.add(id);
      return { dirtyNodeIds: next };
    }),
  clearDirty: (ids) =>
    set((s) => {
      const next = new Set(s.dirtyNodeIds);
      ids.forEach((id) => next.delete(id));
      return { dirtyNodeIds: next };
    }),
}));
```

- [ ] **Step 2: Create undo store**

Write `src/store/undo-store.ts`:

```typescript
import { create } from 'zustand';
import { UndoAction, ChronicleNode } from '@/lib/types';
import { useCanvasStore } from './canvas-store';

const MAX_UNDO = 50;

interface UndoState {
  past: UndoAction[];
  future: UndoAction[];
  push: (action: UndoAction) => void;
  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;
}

export const useUndoStore = create<UndoState>((set, get) => ({
  past: [],
  future: [],

  push: (action) =>
    set((s) => ({
      past: [...s.past.slice(-(MAX_UNDO - 1)), action],
      future: [],
    })),

  undo: () => {
    const { past } = get();
    if (past.length === 0) return;
    const action = past[past.length - 1];
    const store = useCanvasStore.getState();

    switch (action.type) {
      case 'create':
        store.deleteNode(action.nodeId);
        break;
      case 'delete':
        if (action.before) store.addNode(action.before as ChronicleNode);
        break;
      case 'move':
      case 'edit':
        if (action.before) store.updateNode(action.nodeId, action.before);
        break;
    }
    store.markDirty(action.nodeId);

    set((s) => ({
      past: s.past.slice(0, -1),
      future: [action, ...s.future],
    }));
  },

  redo: () => {
    const { future } = get();
    if (future.length === 0) return;
    const action = future[0];
    const store = useCanvasStore.getState();

    switch (action.type) {
      case 'create':
        if (action.after) store.addNode(action.after as ChronicleNode);
        break;
      case 'delete':
        store.deleteNode(action.nodeId);
        break;
      case 'move':
      case 'edit':
        if (action.after) store.updateNode(action.nodeId, action.after);
        break;
    }
    store.markDirty(action.nodeId);

    set((s) => ({
      past: [...s.past, action],
      future: s.future.slice(1),
    }));
  },

  canUndo: () => get().past.length > 0,
  canRedo: () => get().future.length > 0,
}));
```

- [ ] **Step 3: Commit**

```bash
git add src/store/
git commit -m "feat: Zustand canvas store with viewport, nodes, selection, and undo/redo"
```

---

## Task 5: Supabase Sync + Auth

**Files:**
- Create: `src/store/sync.ts`
- Create: `src/hooks/useAutoSave.ts`
- Create: `src/lib/supabase-server.ts`
- Create: `src/app/login/page.tsx`
- Modify: `src/app/page.tsx`
- Create: `src/app/canvas/layout.tsx`

- [ ] **Step 1: Create sync module**

Write `src/store/sync.ts`:

```typescript
import { createClient } from '@/lib/supabase-browser';
import { ChronicleNode, UserSettings } from '@/lib/types';
import { useCanvasStore } from './canvas-store';

const supabase = createClient();
const SYNC_DEBOUNCE_MS = 2000;
const MAX_RETRIES = 3;

let syncTimer: ReturnType<typeof setTimeout> | null = null;

export async function loadInitialData(): Promise<void> {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) throw new Error('Not authenticated');

  const [nodesRes, settingsRes] = await Promise.all([
    supabase.from('nodes').select('*').eq('user_id', user.id),
    supabase.from('user_settings').select('*').eq('user_id', user.id).single(),
  ]);

  if (nodesRes.error) throw nodesRes.error;
  const store = useCanvasStore.getState();
  store.setNodes(nodesRes.data as ChronicleNode[]);

  if (settingsRes.data) {
    const s = settingsRes.data as UserSettings;
    store.setViewport({ x: s.viewport_x, y: s.viewport_y, zoom: s.viewport_zoom });
  }
}

export function scheduleSync(): void {
  if (syncTimer) clearTimeout(syncTimer);
  syncTimer = setTimeout(() => syncDirtyNodes(), SYNC_DEBOUNCE_MS);
}

async function syncDirtyNodes(retryCount = 0): Promise<void> {
  const store = useCanvasStore.getState();
  const dirtyIds = Array.from(store.dirtyNodeIds);
  if (dirtyIds.length === 0) return;

  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;

  const nodesToSync = dirtyIds
    .map((id) => store.nodes.get(id))
    .filter(Boolean) as ChronicleNode[];

  // Handle deleted nodes (dirty but not in store)
  const deletedIds = dirtyIds.filter((id) => !store.nodes.has(id));

  try {
    if (nodesToSync.length > 0) {
      const { error } = await supabase.from('nodes').upsert(
        nodesToSync.map((n) => ({ ...n, user_id: user.id }))
      );
      if (error) throw error;
    }

    if (deletedIds.length > 0) {
      const { error } = await supabase
        .from('nodes')
        .delete()
        .in('id', deletedIds)
        .eq('user_id', user.id);
      if (error) throw error;
    }

    store.clearDirty(dirtyIds);
  } catch (err) {
    if (retryCount < MAX_RETRIES) {
      const delay = Math.pow(2, retryCount) * 1000;
      setTimeout(() => syncDirtyNodes(retryCount + 1), delay);
    }
    // Toast will be shown by useAutoSave hook
    throw err;
  }
}

export async function saveViewport(): Promise<void> {
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return;
  const { viewport } = useCanvasStore.getState();
  await supabase.from('user_settings').upsert({
    user_id: user.id,
    viewport_x: viewport.x,
    viewport_y: viewport.y,
    viewport_zoom: viewport.zoom,
  });
}

export function setupBeforeUnload(): () => void {
  const handler = (e: BeforeUnloadEvent) => {
    const { dirtyNodeIds } = useCanvasStore.getState();
    if (dirtyNodeIds.size > 0) {
      e.preventDefault();
    }
  };
  window.addEventListener('beforeunload', handler);
  return () => window.removeEventListener('beforeunload', handler);
}

export async function searchNodes(query: string): Promise<ChronicleNode[]> {
  // Local-first search
  const store = useCanvasStore.getState();
  const lowerQ = query.toLowerCase();
  const localResults = Array.from(store.nodes.values())
    .filter((n) => n.title.toLowerCase().includes(lowerQ) ||
      n.content?.toLowerCase().includes(lowerQ))
    .slice(0, 10);

  // Parallel Supabase search
  const { data } = await supabase
    .from('nodes')
    .select('*')
    .textSearch('fts', query, { type: 'websearch' })
    .limit(10);

  if (!data) return localResults;

  // Merge, dedupe by id, prefer local version
  const seen = new Set(localResults.map((n) => n.id));
  const merged = [...localResults];
  for (const node of data as ChronicleNode[]) {
    if (!seen.has(node.id)) {
      merged.push(node);
      seen.add(node.id);
    }
  }
  return merged.slice(0, 10);
}
```

- [ ] **Step 2: Create useAutoSave hook**

Write `src/hooks/useAutoSave.ts`:

```typescript
'use client';
import { useEffect } from 'react';
import { useCanvasStore } from '@/store/canvas-store';
import { scheduleSync, setupBeforeUnload, saveViewport } from '@/store/sync';

export function useAutoSave() {
  const dirtyNodeIds = useCanvasStore((s) => s.dirtyNodeIds);
  const viewport = useCanvasStore((s) => s.viewport);

  // Sync dirty nodes
  useEffect(() => {
    if (dirtyNodeIds.size > 0) {
      scheduleSync();
    }
  }, [dirtyNodeIds]);

  // Save viewport on change (debounced separately)
  useEffect(() => {
    const timer = setTimeout(() => saveViewport(), 3000);
    return () => clearTimeout(timer);
  }, [viewport]);

  // Warn before unload
  useEffect(() => {
    return setupBeforeUnload();
  }, []);
}
```

- [ ] **Step 3: Create Supabase server client**

Write `src/lib/supabase-server.ts`:

```typescript
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createServerSupabase() {
  const cookieStore = await cookies();
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options);
          });
        },
      },
    }
  );
}
```

- [ ] **Step 4: Create login page**

Write `src/app/login/page.tsx`:

```typescript
'use client';
import { useState } from 'react';
import { createClient } from '@/lib/supabase-browser';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const supabase = createClient();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const { error } = isSignUp
      ? await supabase.auth.signUp({ email, password })
      : await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (error) {
      setError(error.message);
    } else {
      router.push('/canvas');
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: '#f8f6f1' }}>
      <form onSubmit={handleSubmit} className="w-full max-w-sm p-8 rounded-xl" style={{
        background: '#fffefc',
        boxShadow: '0 1px 2px #0000000a, 0 4px 16px #0000000a, 0 8px 32px #00000005',
      }}>
        <h1 className="text-xl font-medium mb-6" style={{ color: '#1a1814', letterSpacing: '0.3px' }}>
          Chronicle
        </h1>
        <div className="h-0.5 w-8 rounded mb-6" style={{ background: '#c4a97d' }} />
        {error && <p className="text-sm mb-4" style={{ color: '#b44' }}>{error}</p>}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="w-full mb-3 px-4 py-2.5 rounded-lg text-sm outline-none"
          style={{ background: '#f8f6f1', color: '#1a1814', border: '1px solid #e8e4de' }} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-4 px-4 py-2.5 rounded-lg text-sm outline-none"
          style={{ background: '#f8f6f1', color: '#1a1814', border: '1px solid #e8e4de' }} required minLength={6} />
        <button type="submit" disabled={loading}
          className="w-full py-2.5 rounded-lg text-sm font-medium transition-opacity"
          style={{ background: '#1a1814', color: '#fffefc' }}>
          {loading ? '...' : isSignUp ? 'Create Account' : 'Sign In'}
        </button>
        <button type="button" onClick={() => setIsSignUp(!isSignUp)}
          className="w-full mt-3 text-xs" style={{ color: '#9a9080' }}>
          {isSignUp ? 'Already have an account? Sign in' : 'Need an account? Sign up'}
        </button>
      </form>
    </div>
  );
}
```

- [ ] **Step 5: Create canvas auth guard layout**

Write `src/app/canvas/layout.tsx`:

```typescript
import { redirect } from 'next/navigation';
import { createServerSupabase } from '@/lib/supabase-server';

export default async function CanvasLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');
  return <>{children}</>;
}
```

- [ ] **Step 6: Update root page**

Write `src/app/page.tsx`:

```typescript
import { redirect } from 'next/navigation';
import { createServerSupabase } from '@/lib/supabase-server';

export default async function Home() {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();
  redirect(user ? '/canvas' : '/login');
}
```

- [ ] **Step 7: Commit**

```bash
git add src/store/sync.ts src/hooks/useAutoSave.ts src/lib/supabase-server.ts src/app/login/page.tsx src/app/canvas/layout.tsx src/app/page.tsx
git commit -m "feat: Supabase auth, data sync, auto-save, and login page"
```

---

## Task 6: Canvas Renderer + Background

**Files:**
- Create: `src/canvas/render.ts`
- Create: `src/components/CanvasRenderer.tsx`
- Create: `src/hooks/useCanvasInput.ts`

- [ ] **Step 1: Create background + render orchestrator**

Write `src/canvas/render.ts`:

```typescript
import { ChronicleNode, Viewport } from '@/lib/types';
import { getVisibleBounds, worldToScreen, getZoomLevel } from './viewport';
import { Quadtree, Rect } from './quadtree';
import { drawNodeAtLevel } from './node-renderer';
import {
  BG_COLOR, DOT_GRID_COLOR, DOT_GRID_SIZE, DOT_GRID_OPACITY, DOT_GRID_RADIUS,
  NODE_BUBBLE_RADIUS, NODE_CARD_WIDTH, NODE_CARD_HEIGHT,
  NODE_PREVIEW_WIDTH, NODE_PREVIEW_HEIGHT,
  NODE_DOCUMENT_WIDTH, NODE_DOCUMENT_HEIGHT,
} from './constants';

export function getNodeBounds(node: ChronicleNode, zoomLevel: number): Rect {
  let width: number, height: number;
  if (zoomLevel < 0.3) {
    width = height = NODE_BUBBLE_RADIUS * 2;
  } else if (zoomLevel < 0.8) {
    width = NODE_CARD_WIDTH;
    height = NODE_CARD_HEIGHT;
  } else if (zoomLevel < 2.0) {
    width = NODE_PREVIEW_WIDTH;
    height = NODE_PREVIEW_HEIGHT;
  } else {
    width = NODE_DOCUMENT_WIDTH;
    height = NODE_DOCUMENT_HEIGHT;
  }
  return { x: node.position_x, y: node.position_y, width, height };
}

export function renderFrame(
  ctx: CanvasRenderingContext2D,
  viewport: Viewport,
  nodes: Map<string, ChronicleNode>,
  editingNodeId: string | null,
  selectedNodeId: string | null,
  canvasWidth: number,
  canvasHeight: number,
  getChildCount: (parentId: string) => number,
): void {
  ctx.clearRect(0, 0, canvasWidth, canvasHeight);

  // Background
  ctx.fillStyle = BG_COLOR;
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  // Dot grid
  drawDotGrid(ctx, viewport, canvasWidth, canvasHeight);

  // Build quadtree and query visible nodes
  const bounds = getVisibleBounds(viewport, canvasWidth, canvasHeight);
  const worldW = bounds.maxX - bounds.minX;
  const worldH = bounds.maxY - bounds.minY;

  const qt = new Quadtree({
    x: (bounds.minX + bounds.maxX) / 2,
    y: (bounds.minY + bounds.maxY) / 2,
    width: worldW * 2,
    height: worldH * 2,
  });

  const allNodes = Array.from(nodes.values());
  for (const node of allNodes) {
    qt.insert({ id: node.id, bounds: getNodeBounds(node, viewport.zoom) });
  }

  const visibleItems = qt.query({
    x: (bounds.minX + bounds.maxX) / 2,
    y: (bounds.minY + bounds.maxY) / 2,
    width: worldW,
    height: worldH,
  });

  const zoomLevel = getZoomLevel(viewport.zoom);

  for (const item of visibleItems) {
    const node = nodes.get(item.id);
    if (!node) continue;
    if (node.id === editingNodeId) continue; // Skip — DOM overlay is showing

    const screen = worldToScreen(node.position_x, node.position_y, viewport, canvasWidth, canvasHeight);
    const isSelected = node.id === selectedNodeId;

    ctx.save();
    ctx.translate(screen.x, screen.y);
    ctx.scale(viewport.zoom, viewport.zoom);
    drawNodeAtLevel(ctx, node, zoomLevel, viewport.zoom, isSelected, getChildCount);
    ctx.restore();
  }
}

function drawDotGrid(
  ctx: CanvasRenderingContext2D,
  viewport: Viewport,
  canvasWidth: number,
  canvasHeight: number,
): void {
  const gridSize = DOT_GRID_SIZE * viewport.zoom;
  if (gridSize < 4) return; // Too small to see

  ctx.save();
  ctx.globalAlpha = DOT_GRID_OPACITY;
  ctx.fillStyle = DOT_GRID_COLOR;

  const offsetX = (-viewport.x * viewport.zoom + canvasWidth / 2) % gridSize;
  const offsetY = (-viewport.y * viewport.zoom + canvasHeight / 2) % gridSize;

  const radius = DOT_GRID_RADIUS * viewport.zoom;

  for (let x = offsetX; x < canvasWidth; x += gridSize) {
    for (let y = offsetY; y < canvasHeight; y += gridSize) {
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  ctx.restore();
}
```

- [ ] **Step 2: Create canvas input hook**

Write `src/hooks/useCanvasInput.ts`:

```typescript
'use client';
import { useCallback, useRef } from 'react';
import { useCanvasStore } from '@/store/canvas-store';
import { useUndoStore } from '@/store/undo-store';
import { applyZoomDelta, screenToWorld, getZoomLevel } from '@/canvas/viewport';
import { hitTest } from '@/canvas/hit-test';
import { zoomToFitNode } from '@/canvas/animation';
import { findAutoPlacePosition } from '@/canvas/auto-place';

type Mode = 'idle' | 'panning' | 'dragging';

export function useCanvasInput(canvasRef: React.RefObject<HTMLCanvasElement | null>) {
  const mode = useRef<Mode>('idle');
  const lastMouse = useRef({ x: 0, y: 0 });
  const dragNodeStart = useRef<{ x: number; y: number } | null>(null);
  const clickTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const onWheel = useCallback((e: WheelEvent) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const store = useCanvasStore.getState();

    if (e.ctrlKey || Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
      // Zoom (pinch or scroll)
      const rect = canvas.getBoundingClientRect();
      const newVP = applyZoomDelta(
        store.viewport, e.deltaY, e.clientX - rect.left, e.clientY - rect.top,
        canvas.width / devicePixelRatio, canvas.height / devicePixelRatio
      );
      store.setViewport(newVP);
    } else {
      // Pan (horizontal scroll / trackpad swipe)
      store.setViewport({
        ...store.viewport,
        x: store.viewport.x + e.deltaX / store.viewport.zoom,
        y: store.viewport.y + e.deltaY / store.viewport.zoom,
      });
    }
  }, [canvasRef]);

  const onMouseDown = useCallback((e: MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const sx = e.clientX - rect.left;
    const sy = e.clientY - rect.top;
    lastMouse.current = { x: e.clientX, y: e.clientY };

    const store = useCanvasStore.getState();
    const cw = canvas.width / devicePixelRatio;
    const ch = canvas.height / devicePixelRatio;
    const world = screenToWorld(sx, sy, store.viewport, cw, ch);
    const hitId = hitTest(world.x, world.y, store.nodes, store.viewport.zoom);

    if (hitId) {
      store.setSelectedNodeId(hitId);
      mode.current = 'dragging';
      const node = store.getNode(hitId)!;
      dragNodeStart.current = { x: node.position_x, y: node.position_y };
    } else {
      store.setSelectedNodeId(null);
      mode.current = 'panning';
    }
  }, [canvasRef]);

  const onMouseMove = useCallback((e: MouseEvent) => {
    const dx = e.clientX - lastMouse.current.x;
    const dy = e.clientY - lastMouse.current.y;
    lastMouse.current = { x: e.clientX, y: e.clientY };
    const store = useCanvasStore.getState();

    if (mode.current === 'panning') {
      store.setViewport({
        ...store.viewport,
        x: store.viewport.x - dx / store.viewport.zoom,
        y: store.viewport.y - dy / store.viewport.zoom,
      });
    } else if (mode.current === 'dragging' && store.selectedNodeId) {
      store.updateNode(store.selectedNodeId, {
        position_x: (store.getNode(store.selectedNodeId)?.position_x ?? 0) + dx / store.viewport.zoom,
        position_y: (store.getNode(store.selectedNodeId)?.position_y ?? 0) + dy / store.viewport.zoom,
      });
    }
  }, []);

  const onMouseUp = useCallback(() => {
    const store = useCanvasStore.getState();
    if (mode.current === 'dragging' && store.selectedNodeId && dragNodeStart.current) {
      const node = store.getNode(store.selectedNodeId);
      if (node) {
        useUndoStore.getState().push({
          type: 'move', nodeId: node.id,
          before: { position_x: dragNodeStart.current.x, position_y: dragNodeStart.current.y },
          after: { position_x: node.position_x, position_y: node.position_y },
          timestamp: Date.now(),
        });
        store.markDirty(node.id);
      }
    }
    mode.current = 'idle';
    dragNodeStart.current = null;
  }, []);

  const onDoubleClick = useCallback((e: MouseEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const sx = e.clientX - rect.left;
    const sy = e.clientY - rect.top;
    const store = useCanvasStore.getState();
    const cw = canvas.width / devicePixelRatio;
    const ch = canvas.height / devicePixelRatio;
    const world = screenToWorld(sx, sy, store.viewport, cw, ch);
    const hitId = hitTest(world.x, world.y, store.nodes, store.viewport.zoom);

    if (hitId) {
      // Zoom into node
      const node = store.getNode(hitId)!;
      zoomToFitNode(node.position_x, node.position_y);
    } else {
      // Create new node at this position
      const zl = getZoomLevel(store.viewport.zoom);
      // Detect parent context based on proximity
      let parentId: string | null = null;
      let defaultType: 'domain' | 'topic' | 'document' = 'domain';
      if (zl >= 1) {
        // Find nearest domain/topic node within range
        for (const n of store.nodes.values()) {
          const dist = Math.hypot(n.position_x - world.x, n.position_y - world.y);
          if (n.type === 'domain' && dist < 400) { parentId = n.id; defaultType = 'topic'; break; }
          if (n.type === 'topic' && dist < 300) { parentId = n.id; defaultType = 'document'; break; }
        }
      }
      store.setCreatingAt({ x: world.x, y: world.y, parentId, defaultType });
    }
    // Cancel any pending single-click
    if (clickTimer.current) { clearTimeout(clickTimer.current); clickTimer.current = null; }
  }, [canvasRef]);

  return { onWheel, onMouseDown, onMouseMove, onMouseUp, onDoubleClick };
}
```

- [ ] **Step 3: Create CanvasRenderer component**

Write `src/components/CanvasRenderer.tsx`: A React component that:
- Creates a `<canvas>` element sized to fill the container
- Runs a `requestAnimationFrame` loop calling `renderFrame`
- Attaches `useCanvasInput` handlers
- Handles DPR scaling for retina displays

- [ ] **Step 4: Verify canvas renders with background**

```bash
npm run dev
# Open http://localhost:3000/canvas — should see warm background with dot grid
```

- [ ] **Step 5: Commit**

```bash
git add src/canvas/render.ts src/components/CanvasRenderer.tsx src/hooks/useCanvasInput.ts
git commit -m "feat: canvas renderer with dot grid background, pan/zoom input"
```

---

## Task 7: Node Renderer (L0-L3 semantic zoom)

**Files:**
- Create: `src/canvas/node-renderer.ts`
- Create: `src/canvas/hit-test.ts`

- [ ] **Step 1: Implement multi-level node rendering**

Write `src/canvas/node-renderer.ts`:

```typescript
import { ChronicleNode } from '@/lib/types';
import {
  NODE_BUBBLE_RADIUS, NODE_CARD_WIDTH, NODE_CARD_HEIGHT,
  NODE_PREVIEW_WIDTH, NODE_PREVIEW_HEIGHT, NODE_DOCUMENT_WIDTH, NODE_DOCUMENT_HEIGHT,
  CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_GOLD, DOMAIN_COLORS,
  ZOOM_L0_MAX, ZOOM_L1_MAX, ZOOM_L2_MAX,
} from './constants';

// Crossfade factor: 0 at level start, 1 at level end
function crossfade(zoom: number, min: number, max: number): number {
  return Math.max(0, Math.min(1, (zoom - min) / (max - min)));
}

export function drawNodeAtLevel(
  ctx: CanvasRenderingContext2D,
  node: ChronicleNode,
  zoomLevel: 0 | 1 | 2 | 3,
  zoom: number,
  isSelected: boolean,
  getChildCount: (parentId: string) => number,
): void {
  const color = node.color || DOMAIN_COLORS[Math.abs(hashCode(node.id)) % DOMAIN_COLORS.length];

  if (isSelected) {
    ctx.save();
    ctx.strokeStyle = ACCENT_GOLD;
    ctx.lineWidth = 2 / zoom;
    ctx.setLineDash([6 / zoom, 4 / zoom]);
    const w = zoomLevel < 1 ? NODE_BUBBLE_RADIUS * 2.4 : zoomLevel < 2 ? NODE_CARD_WIDTH + 12 : NODE_PREVIEW_WIDTH + 12;
    const h = zoomLevel < 1 ? NODE_BUBBLE_RADIUS * 2.4 : zoomLevel < 2 ? NODE_CARD_HEIGHT + 12 : NODE_PREVIEW_HEIGHT + 12;
    roundRect(ctx, -w / 2, -h / 2, w, h, 12);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
  }

  if (zoomLevel === 0) {
    drawBubble(ctx, node, color, getChildCount);
    // Crossfade: if approaching L1, start fading in card
    if (zoom > ZOOM_L0_MAX * 0.7) {
      const alpha = crossfade(zoom, ZOOM_L0_MAX * 0.7, ZOOM_L0_MAX);
      ctx.globalAlpha = alpha;
      drawCard(ctx, node, color);
      ctx.globalAlpha = 1;
    }
  } else if (zoomLevel === 1) {
    drawCard(ctx, node, color);
    if (zoom > ZOOM_L1_MAX * 0.7) {
      const alpha = crossfade(zoom, ZOOM_L1_MAX * 0.7, ZOOM_L1_MAX);
      ctx.globalAlpha = alpha;
      drawPreview(ctx, node, color);
      ctx.globalAlpha = 1;
    }
  } else if (zoomLevel === 2) {
    drawPreview(ctx, node, color);
    if (zoom > ZOOM_L2_MAX * 0.7) {
      const alpha = crossfade(zoom, ZOOM_L2_MAX * 0.7, ZOOM_L2_MAX);
      ctx.globalAlpha = alpha;
      drawDocument(ctx, node, color);
      ctx.globalAlpha = 1;
    }
  } else {
    drawDocument(ctx, node, color);
  }
}

function drawBubble(ctx: CanvasRenderingContext2D, node: ChronicleNode, color: string, getChildCount: (id: string) => number) {
  const r = NODE_BUBBLE_RADIUS;
  ctx.beginPath();
  ctx.arc(0, 0, r, 0, Math.PI * 2);
  ctx.fillStyle = CARD_BG;
  ctx.shadowColor = '#0000001a';
  ctx.shadowBlur = 16;
  ctx.fill();
  ctx.shadowBlur = 0;
  // Color dot
  ctx.beginPath();
  ctx.arc(0, -r * 0.3, 6, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
  // Label
  ctx.fillStyle = TEXT_PRIMARY;
  ctx.font = '500 14px system-ui';
  ctx.textAlign = 'center';
  ctx.fillText(node.title, 0, 8, r * 1.6);
  // Count
  const count = getChildCount(node.id);
  if (count > 0) {
    ctx.fillStyle = TEXT_SECONDARY;
    ctx.font = '400 10px system-ui';
    ctx.fillText(`${count} items`, 0, 26);
  }
}

function drawCard(ctx: CanvasRenderingContext2D, node: ChronicleNode, color: string) {
  const w = NODE_CARD_WIDTH, h = NODE_CARD_HEIGHT;
  ctx.fillStyle = CARD_BG;
  ctx.shadowColor = '#0000001a';
  ctx.shadowBlur = 12;
  roundRect(ctx, -w / 2, -h / 2, w, h, 10);
  ctx.fill();
  ctx.shadowBlur = 0;
  // Accent line
  ctx.fillStyle = color;
  ctx.fillRect(-w / 2 + 16, -h / 2 + 44, 24, 2);
  // Title
  ctx.fillStyle = TEXT_PRIMARY;
  ctx.font = '500 14px system-ui';
  ctx.textAlign = 'left';
  ctx.fillText(node.title, -w / 2 + 16, -h / 2 + 36, w - 32);
  // Summary
  if (node.summary) {
    ctx.fillStyle = TEXT_SECONDARY;
    ctx.font = '400 11px system-ui';
    ctx.fillText(node.summary, -w / 2 + 16, -h / 2 + 68, w - 32);
  }
}

function drawPreview(ctx: CanvasRenderingContext2D, node: ChronicleNode, color: string) {
  const w = NODE_PREVIEW_WIDTH, h = NODE_PREVIEW_HEIGHT;
  ctx.fillStyle = CARD_BG;
  ctx.shadowColor = '#0000001a';
  ctx.shadowBlur = 16;
  roundRect(ctx, -w / 2, -h / 2, w, h, 12);
  ctx.fill();
  ctx.shadowBlur = 0;
  // Title
  ctx.fillStyle = TEXT_PRIMARY;
  ctx.font = '600 16px system-ui';
  ctx.textAlign = 'left';
  ctx.fillText(node.title, -w / 2 + 20, -h / 2 + 36, w - 40);
  // Accent line
  ctx.fillStyle = color;
  ctx.fillRect(-w / 2 + 20, -h / 2 + 48, 30, 2);
  // Content preview (first 3 lines)
  if (node.content) {
    ctx.fillStyle = TEXT_PRIMARY;
    ctx.font = '400 12px system-ui';
    const lines = node.content.split('\n').slice(0, 3);
    lines.forEach((line, i) => {
      ctx.fillText(line.slice(0, 60), -w / 2 + 20, -h / 2 + 74 + i * 20, w - 40);
    });
  }
  // Type label
  ctx.fillStyle = TEXT_SECONDARY;
  ctx.font = '600 9px system-ui';
  ctx.letterSpacing = '1px';
  ctx.fillText(node.type.toUpperCase(), -w / 2 + 20, -h / 2 + h - 16);
}

function drawDocument(ctx: CanvasRenderingContext2D, node: ChronicleNode, _color: string) {
  const w = NODE_DOCUMENT_WIDTH, h = NODE_DOCUMENT_HEIGHT;
  ctx.fillStyle = CARD_BG;
  ctx.shadowColor = '#0000001a';
  ctx.shadowBlur = 24;
  roundRect(ctx, -w / 2, -h / 2, w, h, 12);
  ctx.fill();
  ctx.shadowBlur = 0;
  // Canvas-rendered simplified view (actual editing uses Tiptap DOM overlay)
  ctx.fillStyle = TEXT_PRIMARY;
  ctx.font = '600 20px system-ui';
  ctx.textAlign = 'left';
  ctx.fillText(node.title, -w / 2 + 28, -h / 2 + 44, w - 56);
  if (node.content) {
    ctx.fillStyle = TEXT_PRIMARY;
    ctx.font = '400 14px system-ui';
    const lines = node.content.split('\n').slice(0, 20);
    lines.forEach((line, i) => {
      ctx.fillText(line, -w / 2 + 28, -h / 2 + 80 + i * 24, w - 56);
    });
  }
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function hashCode(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (Math.imul(31, h) + s.charCodeAt(i)) | 0;
  return h;
}
```

- [ ] **Step 2: Implement hit testing**

Write `src/canvas/hit-test.ts`: Given a click position (world coords), find which node was hit using the quadtree. Return the node ID or null.

- [ ] **Step 3: Test semantic zoom visually**

Create a few test nodes manually in the store. Zoom in/out and verify all 4 levels render and transition smoothly.

- [ ] **Step 4: Commit**

```bash
git add src/canvas/node-renderer.ts src/canvas/hit-test.ts
git commit -m "feat: semantic zoom node rendering (L0 bubble → L3 document)"
```

---

## Task 8: Animation + Zoom-to-Fit

**Files:**
- Create: `src/canvas/animation.ts`

- [ ] **Step 1: Implement viewport animations**

Write `src/canvas/animation.ts`:

```typescript
import { Viewport } from '@/lib/types';
import { ANIMATION_DURATION_MS, EASE_OUT } from './constants';
import { useCanvasStore } from '@/store/canvas-store';

let animationFrame: number | null = null;

export function animateViewportTo(target: Viewport): void {
  if (animationFrame) cancelAnimationFrame(animationFrame);

  const start = { ...useCanvasStore.getState().viewport };
  const startTime = performance.now();

  function tick(now: number) {
    const elapsed = now - startTime;
    const t = Math.min(1, elapsed / ANIMATION_DURATION_MS);
    const eased = EASE_OUT(t);

    useCanvasStore.getState().setViewport({
      x: start.x + (target.x - start.x) * eased,
      y: start.y + (target.y - start.y) * eased,
      zoom: start.zoom + (target.zoom - start.zoom) * eased,
    });

    if (t < 1) {
      animationFrame = requestAnimationFrame(tick);
    } else {
      animationFrame = null;
    }
  }

  animationFrame = requestAnimationFrame(tick);
}

export function zoomToFitNode(nodeX: number, nodeY: number, targetZoom = 2.5): void {
  animateViewportTo({ x: nodeX, y: nodeY, zoom: targetZoom });
}

export function zoomToFitAll(nodes: { position_x: number; position_y: number }[]): void {
  if (nodes.length === 0) return;
  const minX = Math.min(...nodes.map((n) => n.position_x));
  const maxX = Math.max(...nodes.map((n) => n.position_x));
  const minY = Math.min(...nodes.map((n) => n.position_y));
  const maxY = Math.max(...nodes.map((n) => n.position_y));
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  const spread = Math.max(maxX - minX, maxY - minY, 200);
  const zoom = Math.min(0.8, 800 / spread);
  animateViewportTo({ x: cx, y: cy, zoom });
}
```

- [ ] **Step 2: Commit**

```bash
git add src/canvas/animation.ts
git commit -m "feat: smooth viewport animations with ease-out curves"
```

---

## Task 9: Toolbar + Node Creation + Deletion

**Files:**
- Create: `src/components/Toolbar.tsx`
- Create: `src/components/NodeCreationForm.tsx`
- Create: `src/components/DeleteConfirmation.tsx`
- Create: `src/components/Toast.tsx`

- [ ] **Step 1: Create Toolbar**

Write `src/components/Toolbar.tsx`: Top bar with:
- "+" button (creates node at viewport center)
- Zoom in/out buttons (Lucide ZoomIn/ZoomOut icons)
- Zoom level indicator (percentage)
- Search area (placeholder, wired in Task 10)
- User avatar/menu with logout

Styled: semi-transparent warm background, no harsh borders, shadow below.

- [ ] **Step 2: Create node creation form**

Write `src/components/NodeCreationForm.tsx`: Inline form that appears at `creatingAt` position:
- Text input for title (auto-focused)
- Type selector (domain/topic/document buttons)
- Enter to confirm, Escape to cancel
- Generates UUID, creates node in store, marks dirty
- Uses `findAutoPlacePosition()` from `canvas/auto-place.ts` when a parent exists (toolbar "+" button)
- Pushes undo action

- [ ] **Step 3: Create delete confirmation**

Write `src/components/DeleteConfirmation.tsx`: Minimal dialog that appears when deleting a node. Shows node title, confirm/cancel buttons.

- [ ] **Step 4: Create toast component**

Write `src/components/Toast.tsx`: Minimal toast notification for sync status. Auto-dismiss after 3s.

- [ ] **Step 5: Commit**

```bash
git add src/components/Toolbar.tsx src/components/NodeCreationForm.tsx src/components/DeleteConfirmation.tsx src/components/Toast.tsx
git commit -m "feat: toolbar, node creation form, delete confirmation, and toast"
```

---

## Task 10: Search Bar

**Files:**
- Create: `src/components/SearchBar.tsx`

- [ ] **Step 1: Implement search with dropdown results**

Write `src/components/SearchBar.tsx`:
- Cmd+K focuses the input
- Debounced search (300ms) calls `searchNodes()` from sync module
- Dropdown shows results with: Lucide icon per type (Circle for domain, FolderOpen for topic, FileText for document), title, parent path
- Click result → `zoomToFitNode()` to navigate
- Escape closes

- [ ] **Step 2: Commit**

```bash
git add src/components/SearchBar.tsx
git commit -m "feat: Cmd+K search with fuzzy results and zoom-to-navigate"
```

---

## Task 11: Keyboard Shortcuts

**Files:**
- Create: `src/hooks/useKeyboardShortcuts.ts`

- [ ] **Step 1: Implement keyboard shortcuts**

Write `src/hooks/useKeyboardShortcuts.ts`: Listens for:
- `Cmd+K` → focus search
- `Delete`/`Backspace` → delete selected node
- `Cmd+Z` → undo
- `Cmd+Shift+Z` → redo
- `+`/`-` → zoom in/out by fixed step
- `0` → zoom to fit all
- `Escape` → deselect / cancel editing / close search
- Arrow keys → pan viewport

Guard: don't fire when typing in an input/textarea/Tiptap editor.

- [ ] **Step 2: Commit**

```bash
git add src/hooks/useKeyboardShortcuts.ts
git commit -m "feat: keyboard shortcuts for canvas navigation and node operations"
```

---

## Task 12: Editor Overlay (Tiptap)

**Files:**
- Create: `src/components/EditorOverlay.tsx`

- [ ] **Step 1: Implement Tiptap editor overlay**

Write `src/components/EditorOverlay.tsx`:
- Absolutely positioned div matching the editing node's screen bounds
- Uses `requestAnimationFrame` to reposition when viewport changes
- Tiptap editor with StarterKit + Placeholder extension
- Content loaded from node's `content` field (markdown)
- Auto-save: debounce 1.5s → update node in store → mark dirty
- Dismiss on: zoom out past L2, click outside, Escape
- Styled: warm white card with subtle shadow, matching the canvas node appearance

- [ ] **Step 2: Commit**

```bash
git add src/components/EditorOverlay.tsx
git commit -m "feat: Tiptap editor overlay for document editing at L3 zoom"
```

---

## Task 13: Minimap

**Files:**
- Create: `src/components/Minimap.tsx`

- [ ] **Step 1: Implement minimap**

Write `src/components/Minimap.tsx`:
- 160x120px canvas in bottom-right corner
- Renders all nodes as colored dots (larger for domains, smaller for documents)
- Semi-transparent rectangle showing current viewport
- Click to jump (animate viewport to clicked position)
- Subtle border, rounded corners, semi-transparent background

- [ ] **Step 2: Commit**

```bash
git add src/components/Minimap.tsx
git commit -m "feat: minimap with viewport indicator and click-to-navigate"
```

---

## Task 14: CanvasApp (Assembly)

**Files:**
- Create: `src/components/CanvasApp.tsx`
- Create: `src/app/canvas/page.tsx`
- Modify: `src/app/globals.css`

- [ ] **Step 1: Assemble all components**

Write `src/components/CanvasApp.tsx`: The top-level client component that wires everything together:
- Mounts `CanvasRenderer` (full screen)
- Mounts `Toolbar` (fixed top)
- Mounts `Minimap` (fixed bottom-right)
- Mounts `EditorOverlay` (conditional, when `editingNodeId` is set)
- Mounts `NodeCreationForm` (conditional, when `creatingAt` is set)
- Mounts `DeleteConfirmation` (conditional)
- Mounts `Toast` (conditional)
- Calls `loadInitialData()` on mount
- Activates `useAutoSave()`, `useKeyboardShortcuts()`

- [ ] **Step 2: Create canvas page**

Write `src/app/canvas/page.tsx`:

```typescript
import { CanvasApp } from '@/components/CanvasApp';

export default function CanvasPage() {
  return <CanvasApp />;
}
```

- [ ] **Step 3: Update globals.css**

Add canvas-specific styles to prevent scrolling, set cursor styles.

- [ ] **Step 4: Full integration test**

```bash
npm run dev
# Test: login, see canvas, create nodes, zoom in/out through all levels, edit content, search, minimap navigation, undo/redo
```

- [ ] **Step 5: Commit**

```bash
git add src/components/CanvasApp.tsx src/app/canvas/page.tsx src/app/globals.css
git commit -m "feat: assemble CanvasApp with all components, canvas page"
```

---

## Task 15: Seed Data + Final Polish

**Files:**
- Modify: `src/store/sync.ts` (add seed data function)

- [ ] **Step 1: Create seed data for first-time users**

Add a function to `sync.ts` that checks if a user has zero nodes and, if so, creates starter domains: "Learning", "Projects", "Health", "Ideas" — positioned in a square layout at the center.

- [ ] **Step 2: Visual polish pass**

- Verify dot grid renders correctly at all zoom levels
- Verify node transitions are smooth
- Verify editor overlay tracks correctly during zoom/pan
- Verify minimap accurately reflects canvas state
- Test with 50+ nodes for performance

- [ ] **Step 3: Build check**

```bash
npm run build
```

Expected: Clean build, no TypeScript errors, no lint warnings.

- [ ] **Step 4: Commit**

```bash
git add src/store/sync.ts
git commit -m "feat: seed data for new users and visual polish"
```

---

## Task 16: GitHub + STATUS.md

- [ ] **Step 1: Create GitHub repo and push**

```bash
cd "/Users/shaoq/Desktop/VScode Workspace/chronicle"
gh repo create chronicle --public --source=. --push
```

- [ ] **Step 2: Write STATUS.md**

Create `STATUS.md` with:
- Current status (Phase 1 complete)
- Architecture summary
- Supabase setup instructions
- Known issues
- Next phases outline

- [ ] **Step 3: Final commit and push**

```bash
git add STATUS.md
git commit -m "docs: STATUS.md with project status and setup instructions"
git push
```
