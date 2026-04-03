# Learning Arena MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an async knowledge battle platform where users import Canvas syllabi, AI extracts topics and generates quiz questions, and users challenge each other on shared topics with ELO scoring.

**Architecture:** Next.js 16 App Router with Supabase (Auth + PostgreSQL + Realtime). AI features via Claude API (topic extraction + question generation). Canvas LMS REST API for syllabus import. Direct Supabase queries (no ORM), following chronicle project patterns.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS 4, Supabase (@supabase/ssr), Anthropic SDK, Zustand (battle state), Vitest (testing)

**Spec:** `docs/superpowers/specs/2026-04-01-learning-arena-design.md`

---

## File Structure

```
learning-arena/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    # Root layout (fonts, providers)
│   │   ├── page.tsx                      # Landing page
│   │   ├── login/page.tsx                # Google OAuth login
│   │   ├── dashboard/page.tsx            # Main dashboard
│   │   ├── courses/page.tsx              # Course management + Canvas import
│   │   ├── arena/page.tsx                # Battle listing + challenge
│   │   ├── battle/[id]/page.tsx          # Answer questions UI
│   │   ├── battle/[id]/result/page.tsx   # Battle results + ELO change
│   │   ├── leaderboard/page.tsx          # Global + per-topic rankings
│   │   ├── profile/[id]/page.tsx         # User profile + history
│   │   ├── settings/page.tsx             # Canvas token + preferences
│   │   └── api/
│   │       ├── canvas/import/route.ts    # POST: fetch Canvas courses + syllabi
│   │       ├── topics/extract/route.ts   # POST: Claude extracts topics from syllabus
│   │       ├── battle/create/route.ts    # POST: create battle + generate questions
│   │       ├── battle/answer/route.ts    # POST: submit answer
│   │       └── battle/settle/route.ts    # POST: calculate ELO + declare winner
│   ├── components/
│   │   ├── AuthGuard.tsx                 # Redirect if not logged in
│   │   ├── NavBar.tsx                    # Top navigation
│   │   ├── TopicBadge.tsx                # Colored topic tag
│   │   ├── UserCard.tsx                  # Avatar + name + ELO
│   │   ├── BattleCard.tsx                # Battle summary card
│   │   ├── QuestionCard.tsx              # Single question with 4 options
│   │   └── EloChange.tsx                 # +/- ELO display with animation
│   ├── lib/
│   │   ├── supabase-browser.ts           # Browser client factory
│   │   ├── supabase-server.ts            # Server client factory
│   │   ├── supabase-middleware.ts         # Auth middleware helper
│   │   ├── types.ts                      # DB types (profiles, courses, topics, battles, questions, answers)
│   │   ├── canvas.ts                     # Canvas API client (fetch courses, syllabus)
│   │   ├── ai.ts                         # Claude API (extract topics, generate questions)
│   │   ├── elo.ts                        # ELO calculation (pure function)
│   │   └── matching.ts                   # Find opponents by topic overlap
│   └── store/
│       └── battle.ts                     # Zustand store for battle answering state
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql        # All 6 tables + RLS policies
├── tests/
│   ├── lib/
│   │   ├── elo.test.ts                   # ELO calculation tests
│   │   ├── canvas.test.ts                # Canvas API parsing tests
│   │   └── ai.test.ts                    # AI prompt/response parsing tests
│   └── api/
│       ├── battle-create.test.ts         # Battle creation flow
│       └── battle-settle.test.ts         # ELO settlement logic
├── middleware.ts                          # Next.js middleware (auth redirect)
├── .env.local.example                    # Environment variable template
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── tailwind.config.ts (if needed)
└── vitest.config.ts
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `learning-arena/package.json`
- Create: `learning-arena/tsconfig.json`
- Create: `learning-arena/next.config.ts`
- Create: `learning-arena/postcss.config.mjs`
- Create: `learning-arena/.env.local.example`
- Create: `learning-arena/vitest.config.ts`
- Create: `learning-arena/src/app/layout.tsx`
- Create: `learning-arena/src/app/page.tsx`

- [ ] **Step 1: Create project with create-next-app**

```bash
cd "/Users/shaoq/Desktop/VScode Workspace"
npx create-next-app@latest learning-arena --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm
```

- [ ] **Step 2: Install dependencies**

```bash
cd learning-arena
npm install @supabase/ssr @supabase/supabase-js @anthropic-ai/sdk zustand
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

- [ ] **Step 3: Create vitest config**

Create `learning-arena/vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: [],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

- [ ] **Step 4: Add test script to package.json**

Add to `scripts` in `package.json`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 5: Create .env.local.example**

Create `learning-arena/.env.local.example`:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ANTHROPIC_API_KEY=your-anthropic-key
```

- [ ] **Step 6: Verify dev server starts**

```bash
cd learning-arena && npm run dev
```

Expected: Server starts on http://localhost:3000 with default Next.js page.

- [ ] **Step 7: Commit**

```bash
git add learning-arena/
git commit -m "feat(arena): scaffold Next.js 16 + Supabase + Vitest project"
```

---

### Task 2: Supabase Schema + RLS

**Files:**
- Create: `learning-arena/supabase/migrations/001_initial_schema.sql`
- Create: `learning-arena/src/lib/types.ts`

- [ ] **Step 1: Write the migration SQL**

Create `learning-arena/supabase/migrations/001_initial_schema.sql`:

```sql
-- Enable pgcrypto for token encryption
create extension if not exists pgcrypto;

-- 1. profiles
create table profiles (
  id uuid primary key references auth.users on delete cascade,
  display_name text not null default '',
  avatar_url text,
  canvas_token text,  -- encrypted via application layer
  canvas_url text,
  elo_rating int not null default 1000,
  total_wins int not null default 0,
  total_losses int not null default 0,
  created_at timestamptz not null default now()
);

alter table profiles enable row level security;

create policy "Users can read any profile" on profiles
  for select using (true);

create policy "Users can update own profile" on profiles
  for update using (auth.uid() = id);

create policy "Users can insert own profile" on profiles
  for insert with check (auth.uid() = id);

-- 2. courses
create table courses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  canvas_course_id text,
  name text not null,
  syllabus_raw text,
  imported_at timestamptz not null default now()
);

alter table courses enable row level security;

create policy "Users can read own courses" on courses
  for select using (auth.uid() = user_id);

create policy "Users can insert own courses" on courses
  for insert with check (auth.uid() = user_id);

create policy "Users can delete own courses" on courses
  for delete using (auth.uid() = user_id);

-- 3. topics
create table topics (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references courses(id) on delete cascade,
  name text not null,
  normalized_tag text not null,
  difficulty_estimate int not null default 3 check (difficulty_estimate between 1 and 5),
  source text not null default 'canvas' check (source in ('canvas', 'photo', 'manual')),
  created_at timestamptz not null default now()
);

alter table topics enable row level security;

-- Users can read own topics
create policy "Users can read own topics" on topics
  for select using (
    exists (select 1 from courses where courses.id = topics.course_id and courses.user_id = auth.uid())
  );

-- Anyone can read normalized_tag for matching (but not full topic data)
create policy "Anyone can read topic tags for matching" on topics
  for select using (true);

create policy "Users can insert own topics" on topics
  for insert with check (
    exists (select 1 from courses where courses.id = topics.course_id and courses.user_id = auth.uid())
  );

-- 4. battles
create table battles (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references topics(id),
  challenger_id uuid not null references profiles(id),
  opponent_id uuid not null references profiles(id),
  status text not null default 'pending' check (status in ('pending', 'active', 'done')),
  mode text not null default 'async' check (mode in ('realtime', 'async')),
  winner_id uuid references profiles(id),
  elo_change int,
  created_at timestamptz not null default now(),
  finished_at timestamptz
);

alter table battles enable row level security;

create policy "Participants can read their battles" on battles
  for select using (auth.uid() in (challenger_id, opponent_id));

create policy "Any user can create a battle" on battles
  for insert with check (auth.uid() = challenger_id);

create policy "Participants can update battle" on battles
  for update using (auth.uid() in (challenger_id, opponent_id));

-- Anyone can read battles for leaderboard
create policy "Anyone can read battles for leaderboard" on battles
  for select using (status = 'done');

-- 5. questions
create table questions (
  id uuid primary key default gen_random_uuid(),
  battle_id uuid not null references battles(id) on delete cascade,
  topic_id uuid not null references topics(id),
  question_text text not null,
  options jsonb not null,  -- {"a": "...", "b": "...", "c": "...", "d": "..."}
  correct_answer text not null check (correct_answer in ('a', 'b', 'c', 'd')),
  difficulty int not null default 2 check (difficulty between 1 and 3),
  order_index int not null
);

alter table questions enable row level security;

create policy "Battle participants can read questions" on questions
  for select using (
    exists (
      select 1 from battles
      where battles.id = questions.battle_id
      and auth.uid() in (battles.challenger_id, battles.opponent_id)
    )
  );

create policy "Service role can insert questions" on questions
  for insert with check (true);  -- API routes use service role

-- 6. answers
create table answers (
  id uuid primary key default gen_random_uuid(),
  battle_id uuid not null references battles(id) on delete cascade,
  question_id uuid not null references questions(id) on delete cascade,
  user_id uuid not null references profiles(id),
  selected_answer text not null check (selected_answer in ('a', 'b', 'c', 'd')),
  is_correct boolean not null,
  time_taken_ms int not null default 0,
  answered_at timestamptz not null default now(),
  unique(question_id, user_id)  -- one answer per user per question
);

alter table answers enable row level security;

create policy "Users can read own answers" on answers
  for select using (auth.uid() = user_id);

create policy "Battle participants can read all answers after done" on answers
  for select using (
    exists (
      select 1 from battles
      where battles.id = answers.battle_id
      and battles.status = 'done'
      and auth.uid() in (battles.challenger_id, battles.opponent_id)
    )
  );

create policy "Users can insert own answers" on answers
  for insert with check (auth.uid() = user_id);

-- Indexes for common queries
create index idx_topics_normalized_tag on topics(normalized_tag);
create index idx_battles_status on battles(status);
create index idx_battles_challenger on battles(challenger_id);
create index idx_battles_opponent on battles(opponent_id);
create index idx_profiles_elo on profiles(elo_rating desc);

-- Function: auto-create profile on signup
create or replace function handle_new_user()
returns trigger as $$
begin
  insert into profiles (id, display_name, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', new.raw_user_meta_data->>'name', 'Arena User'),
    coalesce(new.raw_user_meta_data->>'avatar_url', new.raw_user_meta_data->>'picture')
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();
```

- [ ] **Step 2: Write TypeScript types**

Create `learning-arena/src/lib/types.ts`:

```typescript
export interface Profile {
  id: string;
  display_name: string;
  avatar_url: string | null;
  canvas_token: string | null;
  canvas_url: string | null;
  elo_rating: number;
  total_wins: number;
  total_losses: number;
  created_at: string;
}

export interface Course {
  id: string;
  user_id: string;
  canvas_course_id: string | null;
  name: string;
  syllabus_raw: string | null;
  imported_at: string;
}

export interface Topic {
  id: string;
  course_id: string;
  name: string;
  normalized_tag: string;
  difficulty_estimate: number;
  source: 'canvas' | 'photo' | 'manual';
  created_at: string;
}

export interface Battle {
  id: string;
  topic_id: string;
  challenger_id: string;
  opponent_id: string;
  status: 'pending' | 'active' | 'done';
  mode: 'realtime' | 'async';
  winner_id: string | null;
  elo_change: number | null;
  created_at: string;
  finished_at: string | null;
}

export interface Question {
  id: string;
  battle_id: string;
  topic_id: string;
  question_text: string;
  options: { a: string; b: string; c: string; d: string };
  correct_answer: 'a' | 'b' | 'c' | 'd';
  difficulty: 1 | 2 | 3;
  order_index: number;
}

export interface Answer {
  id: string;
  battle_id: string;
  question_id: string;
  user_id: string;
  selected_answer: 'a' | 'b' | 'c' | 'd';
  is_correct: boolean;
  time_taken_ms: number;
  answered_at: string;
}

// Joined types for UI
export interface BattleWithDetails extends Battle {
  topic: Topic;
  challenger: Profile;
  opponent: Profile;
  questions?: Question[];
}

export interface LeaderboardEntry {
  id: string;
  display_name: string;
  avatar_url: string | null;
  elo_rating: number;
  total_wins: number;
  total_losses: number;
}
```

- [ ] **Step 3: Apply migration to Supabase**

Go to Supabase Dashboard → SQL Editor → paste and run `001_initial_schema.sql`.

Or if Supabase CLI is set up:
```bash
supabase db push
```

- [ ] **Step 4: Commit**

```bash
git add learning-arena/supabase/ learning-arena/src/lib/types.ts
git commit -m "feat(arena): add 6-table schema with RLS + TypeScript types"
```

---

### Task 3: Supabase Client + Auth

**Files:**
- Create: `learning-arena/src/lib/supabase-browser.ts`
- Create: `learning-arena/src/lib/supabase-server.ts`
- Create: `learning-arena/src/lib/supabase-middleware.ts`
- Create: `learning-arena/middleware.ts`
- Create: `learning-arena/src/app/login/page.tsx`
- Modify: `learning-arena/src/app/layout.tsx`

- [ ] **Step 1: Create browser Supabase client**

Create `learning-arena/src/lib/supabase-browser.ts`:

```typescript
import { createBrowserClient } from '@supabase/ssr';

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

- [ ] **Step 2: Create server Supabase client**

Create `learning-arena/src/lib/supabase-server.ts`:

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
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        },
      },
    }
  );
}

export async function createServiceSupabase() {
  const { createClient } = await import('@supabase/supabase-js');
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}
```

- [ ] **Step 3: Create middleware for auth**

Create `learning-arena/src/lib/supabase-middleware.ts`:

```typescript
import { createServerClient } from '@supabase/ssr';
import { type NextRequest, NextResponse } from 'next/server';

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const { data: { user } } = await supabase.auth.getUser();

  const protectedPaths = ['/dashboard', '/courses', '/arena', '/battle', '/settings', '/profile'];
  const isProtected = protectedPaths.some(p => request.nextUrl.pathname.startsWith(p));

  if (isProtected && !user) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (request.nextUrl.pathname === '/login' && user) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return response;
}
```

Create `learning-arena/middleware.ts`:

```typescript
import { updateSession } from '@/lib/supabase-middleware';
import { type NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api/).*)'],
};
```

- [ ] **Step 4: Create login page**

Create `learning-arena/src/app/login/page.tsx`:

```tsx
'use client';

import { createClient } from '@/lib/supabase-browser';

export default function LoginPage() {
  const supabase = createClient();

  async function handleGoogleLogin() {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <div className="text-center space-y-8">
        <div>
          <h1 className="text-4xl font-bold text-white">Learning Arena</h1>
          <p className="text-gray-400 mt-2">知识竞技场 — 用学习来对战</p>
        </div>
        <button
          onClick={handleGoogleLogin}
          className="px-6 py-3 bg-white text-gray-900 font-medium rounded-lg hover:bg-gray-100 transition-colors"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Create auth callback route**

Create `learning-arena/src/app/auth/callback/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { createServerSupabase } from '@/lib/supabase-server';

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');

  if (code) {
    const supabase = await createServerSupabase();
    await supabase.auth.exchangeCodeForSession(code);
  }

  return NextResponse.redirect(`${origin}/dashboard`);
}
```

- [ ] **Step 6: Update root layout**

Replace `learning-arena/src/app/layout.tsx`:

```tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Learning Arena',
  description: '知识竞技场 — 用学习来对战',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-white`}>
        {children}
      </body>
    </html>
  );
}
```

- [ ] **Step 7: Verify login flow**

1. Set up Google OAuth in Supabase Dashboard → Authentication → Providers → Google
2. Add `http://localhost:3000/auth/callback` to authorized redirect URLs
3. Copy Supabase URL + anon key to `learning-arena/.env.local`
4. Run `npm run dev`, navigate to `/login`, click Google sign-in
5. Verify redirect to `/dashboard` after auth

Expected: Successful login, profile auto-created via trigger.

- [ ] **Step 8: Commit**

```bash
git add learning-arena/src/lib/supabase-*.ts learning-arena/middleware.ts learning-arena/src/app/login/ learning-arena/src/app/auth/ learning-arena/src/app/layout.tsx
git commit -m "feat(arena): add Supabase auth with Google OAuth + middleware"
```

---

### Task 4: ELO Calculation (Pure Logic + Tests)

**Files:**
- Create: `learning-arena/src/lib/elo.ts`
- Create: `learning-arena/tests/lib/elo.test.ts`

- [ ] **Step 1: Write failing ELO tests**

Create `learning-arena/tests/lib/elo.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { calculateElo } from '@/lib/elo';

describe('calculateElo', () => {
  it('returns equal change for equal-rated players', () => {
    const result = calculateElo(1000, 1000, 'win');
    expect(result.newRating).toBe(1016);
    expect(result.change).toBe(16);
  });

  it('gives more points for beating a stronger opponent', () => {
    const result = calculateElo(1000, 1400, 'win');
    expect(result.change).toBeGreaterThan(16);
  });

  it('gives fewer points for beating a weaker opponent', () => {
    const result = calculateElo(1400, 1000, 'win');
    expect(result.change).toBeLessThan(16);
  });

  it('subtracts points on loss', () => {
    const result = calculateElo(1000, 1000, 'loss');
    expect(result.change).toBeLessThan(0);
    expect(result.newRating).toBe(984);
  });

  it('uses higher K-factor for new players', () => {
    const newPlayer = calculateElo(1000, 1000, 'win', { isNewPlayer: true });
    const veteran = calculateElo(1000, 1000, 'win', { isNewPlayer: false });
    expect(newPlayer.change).toBeGreaterThan(veteran.change);
  });

  it('never drops below 0', () => {
    const result = calculateElo(10, 2000, 'loss');
    expect(result.newRating).toBeGreaterThanOrEqual(0);
  });

  it('handles draw', () => {
    const result = calculateElo(1000, 1000, 'draw');
    expect(result.change).toBe(0);
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd learning-arena && npx vitest run tests/lib/elo.test.ts
```

Expected: FAIL — module `@/lib/elo` not found.

- [ ] **Step 3: Implement ELO calculation**

Create `learning-arena/src/lib/elo.ts`:

```typescript
type Outcome = 'win' | 'loss' | 'draw';

interface EloOptions {
  isNewPlayer?: boolean;
}

interface EloResult {
  newRating: number;
  change: number;
}

export function calculateElo(
  playerRating: number,
  opponentRating: number,
  outcome: Outcome,
  options: EloOptions = {}
): EloResult {
  const K = options.isNewPlayer ? 64 : 32;

  const expectedScore = 1 / (1 + Math.pow(10, (opponentRating - playerRating) / 400));

  const actualScore = outcome === 'win' ? 1 : outcome === 'loss' ? 0 : 0.5;

  const change = Math.round(K * (actualScore - expectedScore));
  const newRating = Math.max(0, playerRating + change);

  return { newRating, change };
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd learning-arena && npx vitest run tests/lib/elo.test.ts
```

Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add learning-arena/src/lib/elo.ts learning-arena/tests/lib/elo.test.ts
git commit -m "feat(arena): add ELO calculation with tests"
```

---

### Task 5: Canvas API Client

**Files:**
- Create: `learning-arena/src/lib/canvas.ts`
- Create: `learning-arena/tests/lib/canvas.test.ts`
- Create: `learning-arena/src/app/api/canvas/import/route.ts`

- [ ] **Step 1: Write Canvas client tests**

Create `learning-arena/tests/lib/canvas.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { parseCanvasCourses, extractSyllabusText } from '@/lib/canvas';

describe('parseCanvasCourses', () => {
  it('extracts course id and name from Canvas API response', () => {
    const raw = [
      { id: 123, name: 'STOR 120 - Intro to Stats', syllabus_body: '<p>Week 1: Probability</p>' },
      { id: 456, name: 'CHEM 261 - Organic Chemistry', syllabus_body: null },
    ];
    const courses = parseCanvasCourses(raw);
    expect(courses).toHaveLength(2);
    expect(courses[0]).toEqual({
      canvas_course_id: '123',
      name: 'STOR 120 - Intro to Stats',
      syllabus_raw: '<p>Week 1: Probability</p>',
    });
    expect(courses[1].syllabus_raw).toBeNull();
  });

  it('handles empty array', () => {
    expect(parseCanvasCourses([])).toEqual([]);
  });
});

describe('extractSyllabusText', () => {
  it('strips HTML tags from syllabus body', () => {
    const html = '<h2>Course Outline</h2><p>Week 1: <strong>Probability</strong></p><ul><li>Bayes theorem</li></ul>';
    const text = extractSyllabusText(html);
    expect(text).toContain('Course Outline');
    expect(text).toContain('Probability');
    expect(text).toContain('Bayes theorem');
    expect(text).not.toContain('<');
  });

  it('returns empty string for null', () => {
    expect(extractSyllabusText(null)).toBe('');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd learning-arena && npx vitest run tests/lib/canvas.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement Canvas client**

Create `learning-arena/src/lib/canvas.ts`:

```typescript
interface CanvasRawCourse {
  id: number;
  name: string;
  syllabus_body: string | null;
}

interface ParsedCourse {
  canvas_course_id: string;
  name: string;
  syllabus_raw: string | null;
}

export function parseCanvasCourses(raw: CanvasRawCourse[]): ParsedCourse[] {
  return raw.map(c => ({
    canvas_course_id: String(c.id),
    name: c.name,
    syllabus_raw: c.syllabus_body ?? null,
  }));
}

export function extractSyllabusText(html: string | null): string {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}

export async function fetchCanvasCourses(
  canvasUrl: string,
  token: string
): Promise<CanvasRawCourse[]> {
  const baseUrl = canvasUrl.replace(/\/+$/, '');
  const res = await fetch(
    `${baseUrl}/api/v1/courses?include[]=syllabus_body&enrollment_state=active&per_page=50`,
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );

  if (!res.ok) {
    throw new Error(`Canvas API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd learning-arena && npx vitest run tests/lib/canvas.test.ts
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Create Canvas import API route**

Create `learning-arena/src/app/api/canvas/import/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { createServerSupabase } from '@/lib/supabase-server';
import { fetchCanvasCourses, parseCanvasCourses } from '@/lib/canvas';

export async function POST(request: Request) {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { canvas_url, canvas_token } = await request.json();

  if (!canvas_url || !canvas_token) {
    return NextResponse.json({ error: 'Missing canvas_url or canvas_token' }, { status: 400 });
  }

  // Save token to profile
  await supabase
    .from('profiles')
    .update({ canvas_url, canvas_token })
    .eq('id', user.id);

  // Fetch courses from Canvas
  const rawCourses = await fetchCanvasCourses(canvas_url, canvas_token);
  const courses = parseCanvasCourses(rawCourses);

  // Insert courses
  const { data: inserted, error } = await supabase
    .from('courses')
    .upsert(
      courses.map(c => ({
        user_id: user.id,
        canvas_course_id: c.canvas_course_id,
        name: c.name,
        syllabus_raw: c.syllabus_raw,
      })),
      { onConflict: 'user_id,canvas_course_id', ignoreDuplicates: false }
    )
    .select();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ courses: inserted, count: inserted?.length ?? 0 });
}
```

- [ ] **Step 6: Add unique constraint for upsert**

Add to `001_initial_schema.sql` (or run separately):

```sql
alter table courses add constraint courses_user_course_unique unique (user_id, canvas_course_id);
```

- [ ] **Step 7: Commit**

```bash
git add learning-arena/src/lib/canvas.ts learning-arena/tests/lib/canvas.test.ts learning-arena/src/app/api/canvas/
git commit -m "feat(arena): add Canvas API client + import endpoint"
```

---

### Task 6: AI Engine (Topic Extraction + Question Generation)

**Files:**
- Create: `learning-arena/src/lib/ai.ts`
- Create: `learning-arena/tests/lib/ai.test.ts`
- Create: `learning-arena/src/app/api/topics/extract/route.ts`

- [ ] **Step 1: Write AI parsing tests**

Create `learning-arena/tests/lib/ai.test.ts`:

```typescript
import { describe, it, expect } from 'vitest';
import { parseTopicsResponse, parseQuestionsResponse, buildTopicExtractionPrompt, buildQuestionPrompt } from '@/lib/ai';

describe('parseTopicsResponse', () => {
  it('parses JSON array of topics from Claude response', () => {
    const raw = JSON.stringify([
      { name: 'Eigenvalues', normalized_tag: 'linear-algebra/eigenvalues', difficulty_estimate: 3 },
      { name: 'Matrix Diagonalization', normalized_tag: 'linear-algebra/diagonalization', difficulty_estimate: 4 },
    ]);
    const topics = parseTopicsResponse(raw);
    expect(topics).toHaveLength(2);
    expect(topics[0].name).toBe('Eigenvalues');
    expect(topics[0].normalized_tag).toBe('linear-algebra/eigenvalues');
  });

  it('handles JSON wrapped in markdown code block', () => {
    const raw = '```json\n[{"name":"Probability","normalized_tag":"statistics/probability","difficulty_estimate":2}]\n```';
    const topics = parseTopicsResponse(raw);
    expect(topics).toHaveLength(1);
  });

  it('returns empty array for unparseable response', () => {
    expect(parseTopicsResponse('I cannot parse this')).toEqual([]);
  });
});

describe('parseQuestionsResponse', () => {
  it('parses quiz questions from Claude response', () => {
    const raw = JSON.stringify([
      {
        question_text: 'What is an eigenvalue?',
        options: { a: 'A scalar λ', b: 'A matrix', c: 'A vector', d: 'A function' },
        correct_answer: 'a',
        difficulty: 2,
      },
    ]);
    const questions = parseQuestionsResponse(raw);
    expect(questions).toHaveLength(1);
    expect(questions[0].correct_answer).toBe('a');
    expect(questions[0].options.a).toBe('A scalar λ');
  });
});

describe('buildTopicExtractionPrompt', () => {
  it('includes course name and syllabus text', () => {
    const prompt = buildTopicExtractionPrompt('STOR 120', 'Week 1: Probability. Week 2: Bayes theorem.');
    expect(prompt).toContain('STOR 120');
    expect(prompt).toContain('Probability');
  });
});

describe('buildQuestionPrompt', () => {
  it('includes topic name and difficulty', () => {
    const prompt = buildQuestionPrompt('Eigenvalues and Eigenvectors', 2, 5);
    expect(prompt).toContain('Eigenvalues');
    expect(prompt).toContain('5');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd learning-arena && npx vitest run tests/lib/ai.test.ts
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement AI module**

Create `learning-arena/src/lib/ai.ts`:

```typescript
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

interface ExtractedTopic {
  name: string;
  normalized_tag: string;
  difficulty_estimate: number;
}

interface GeneratedQuestion {
  question_text: string;
  options: { a: string; b: string; c: string; d: string };
  correct_answer: 'a' | 'b' | 'c' | 'd';
  difficulty: 1 | 2 | 3;
}

function extractJson(text: string): string {
  const codeBlockMatch = text.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
  if (codeBlockMatch) return codeBlockMatch[1].trim();
  const arrayMatch = text.match(/\[[\s\S]*\]/);
  if (arrayMatch) return arrayMatch[0];
  return text;
}

export function parseTopicsResponse(raw: string): ExtractedTopic[] {
  try {
    const json = extractJson(raw);
    const parsed = JSON.parse(json);
    if (!Array.isArray(parsed)) return [];
    return parsed.map(t => ({
      name: String(t.name),
      normalized_tag: String(t.normalized_tag),
      difficulty_estimate: Number(t.difficulty_estimate) || 3,
    }));
  } catch {
    return [];
  }
}

export function parseQuestionsResponse(raw: string): GeneratedQuestion[] {
  try {
    const json = extractJson(raw);
    const parsed = JSON.parse(json);
    if (!Array.isArray(parsed)) return [];
    return parsed.map(q => ({
      question_text: String(q.question_text),
      options: {
        a: String(q.options.a),
        b: String(q.options.b),
        c: String(q.options.c),
        d: String(q.options.d),
      },
      correct_answer: q.correct_answer as 'a' | 'b' | 'c' | 'd',
      difficulty: (Number(q.difficulty) || 2) as 1 | 2 | 3,
    }));
  } catch {
    return [];
  }
}

export function buildTopicExtractionPrompt(courseName: string, syllabusText: string): string {
  return `You are analyzing a course syllabus to extract specific knowledge topics for a quiz platform.

Course: ${courseName}
Syllabus:
${syllabusText}

Extract all distinct knowledge topics from this syllabus. For each topic, provide:
- name: Human-readable topic name (e.g., "Eigenvalues and Eigenvectors")
- normalized_tag: Hierarchical tag in kebab-case (e.g., "linear-algebra/eigenvalues")
- difficulty_estimate: 1-5 scale (1=intro, 5=advanced)

Return ONLY a JSON array. No explanation. Example:
[{"name": "Bayes Theorem", "normalized_tag": "statistics/bayes-theorem", "difficulty_estimate": 2}]`;
}

export function buildQuestionPrompt(topicName: string, difficulty: number, count: number): string {
  const diffLabel = difficulty <= 1 ? 'easy (recall/definition)' : difficulty <= 2 ? 'medium (application/analysis)' : 'hard (synthesis/evaluation)';
  return `Generate ${count} multiple-choice quiz questions about "${topicName}" at ${diffLabel} level.

Requirements:
- Test understanding, not memorization
- Each question has exactly 4 options (a, b, c, d)
- Distractors should be plausible (common misconceptions)
- Questions should be clear and unambiguous

Return ONLY a JSON array. No explanation. Example:
[{"question_text": "Which property defines eigenvalues?", "options": {"a": "Av = λv", "b": "A + v = λ", "c": "det(A) = 0", "d": "A^T = A"}, "correct_answer": "a", "difficulty": 2}]`;
}

export async function extractTopics(courseName: string, syllabusText: string): Promise<ExtractedTopic[]> {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 2000,
    messages: [{ role: 'user', content: buildTopicExtractionPrompt(courseName, syllabusText) }],
  });

  const text = message.content[0].type === 'text' ? message.content[0].text : '';
  return parseTopicsResponse(text);
}

export async function generateQuestions(
  topicName: string,
  difficulty: number,
  count: number = 5
): Promise<GeneratedQuestion[]> {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 3000,
    messages: [{ role: 'user', content: buildQuestionPrompt(topicName, difficulty, count) }],
  });

  const text = message.content[0].type === 'text' ? message.content[0].text : '';
  return parseQuestionsResponse(text);
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd learning-arena && npx vitest run tests/lib/ai.test.ts
```

Expected: All 6 tests PASS (only testing parsing, not API calls).

- [ ] **Step 5: Create topic extraction API route**

Create `learning-arena/src/app/api/topics/extract/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { createServerSupabase } from '@/lib/supabase-server';
import { extractTopics } from '@/lib/ai';
import { extractSyllabusText } from '@/lib/canvas';

export async function POST(request: Request) {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { course_id } = await request.json();

  // Fetch course
  const { data: course } = await supabase
    .from('courses')
    .select('*')
    .eq('id', course_id)
    .eq('user_id', user.id)
    .single();

  if (!course) {
    return NextResponse.json({ error: 'Course not found' }, { status: 404 });
  }

  const syllabusText = extractSyllabusText(course.syllabus_raw);
  if (!syllabusText) {
    return NextResponse.json({ error: 'No syllabus content to extract from' }, { status: 400 });
  }

  // Extract topics via Claude
  const extracted = await extractTopics(course.name, syllabusText);

  if (extracted.length === 0) {
    return NextResponse.json({ error: 'Could not extract topics' }, { status: 422 });
  }

  // Insert topics
  const { data: topics, error } = await supabase
    .from('topics')
    .insert(
      extracted.map(t => ({
        course_id,
        name: t.name,
        normalized_tag: t.normalized_tag,
        difficulty_estimate: t.difficulty_estimate,
        source: 'canvas' as const,
      }))
    )
    .select();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ topics, count: topics?.length ?? 0 });
}
```

- [ ] **Step 6: Commit**

```bash
git add learning-arena/src/lib/ai.ts learning-arena/tests/lib/ai.test.ts learning-arena/src/app/api/topics/
git commit -m "feat(arena): add AI topic extraction + question generation engine"
```

---

### Task 7: Battle Creation + Question Generation API

**Files:**
- Create: `learning-arena/src/lib/matching.ts`
- Create: `learning-arena/src/app/api/battle/create/route.ts`

- [ ] **Step 1: Implement matching utility**

Create `learning-arena/src/lib/matching.ts`:

```typescript
import type { Profile, Topic } from './types';

interface MatchCandidate {
  profile: Profile;
  score: number;
  shared_topics: string[];
}

export function scoreMatch(
  challengerElo: number,
  challengerTags: string[],
  candidate: { elo_rating: number; tags: string[] }
): { score: number; shared_topics: string[] } {
  // ELO proximity (30%): closer ELO = higher score
  const eloDiff = Math.abs(challengerElo - candidate.elo_rating);
  const eloScore = Math.max(0, 1 - eloDiff / 500);

  // Topic overlap (70%): more shared topics = higher score
  const shared = challengerTags.filter(t => candidate.tags.includes(t));
  const topicScore = shared.length / Math.max(challengerTags.length, 1);

  return {
    score: eloScore * 0.3 + topicScore * 0.7,
    shared_topics: shared,
  };
}
```

- [ ] **Step 2: Create battle creation API route**

Create `learning-arena/src/app/api/battle/create/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { createServerSupabase, createServiceSupabase } from '@/lib/supabase-server';
import { generateQuestions } from '@/lib/ai';

export async function POST(request: Request) {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { topic_id, opponent_id } = await request.json();

  if (!topic_id || !opponent_id) {
    return NextResponse.json({ error: 'Missing topic_id or opponent_id' }, { status: 400 });
  }

  // Verify topic exists
  const { data: topic } = await supabase
    .from('topics')
    .select('*')
    .eq('id', topic_id)
    .single();

  if (!topic) {
    return NextResponse.json({ error: 'Topic not found' }, { status: 404 });
  }

  // Create battle
  const { data: battle, error: battleError } = await supabase
    .from('battles')
    .insert({
      topic_id,
      challenger_id: user.id,
      opponent_id,
      status: 'active',
      mode: 'async',
    })
    .select()
    .single();

  if (battleError) {
    return NextResponse.json({ error: battleError.message }, { status: 500 });
  }

  // Generate 5 questions via Claude (use service role to bypass RLS for insert)
  const generated = await generateQuestions(topic.name, topic.difficulty_estimate, 5);

  if (generated.length === 0) {
    return NextResponse.json({ error: 'Failed to generate questions' }, { status: 422 });
  }

  const serviceSupabase = await createServiceSupabase();
  const { error: qError } = await serviceSupabase
    .from('questions')
    .insert(
      generated.map((q, i) => ({
        battle_id: battle.id,
        topic_id,
        question_text: q.question_text,
        options: q.options,
        correct_answer: q.correct_answer,
        difficulty: q.difficulty,
        order_index: i + 1,
      }))
    );

  if (qError) {
    return NextResponse.json({ error: qError.message }, { status: 500 });
  }

  return NextResponse.json({ battle });
}
```

- [ ] **Step 3: Commit**

```bash
git add learning-arena/src/lib/matching.ts learning-arena/src/app/api/battle/create/
git commit -m "feat(arena): add battle creation + AI question generation endpoint"
```

---

### Task 8: Battle Answer + Settlement APIs

**Files:**
- Create: `learning-arena/src/app/api/battle/answer/route.ts`
- Create: `learning-arena/src/app/api/battle/settle/route.ts`

- [ ] **Step 1: Create answer submission API**

Create `learning-arena/src/app/api/battle/answer/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { createServerSupabase } from '@/lib/supabase-server';

export async function POST(request: Request) {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { battle_id, question_id, selected_answer, time_taken_ms } = await request.json();

  // Verify user is a participant
  const { data: battle } = await supabase
    .from('battles')
    .select('*')
    .eq('id', battle_id)
    .in('status', ['active'])
    .single();

  if (!battle || (battle.challenger_id !== user.id && battle.opponent_id !== user.id)) {
    return NextResponse.json({ error: 'Battle not found or not active' }, { status: 404 });
  }

  // Get correct answer
  const { data: question } = await supabase
    .from('questions')
    .select('correct_answer')
    .eq('id', question_id)
    .single();

  if (!question) {
    return NextResponse.json({ error: 'Question not found' }, { status: 404 });
  }

  const is_correct = selected_answer === question.correct_answer;

  const { data: answer, error } = await supabase
    .from('answers')
    .insert({
      battle_id,
      question_id,
      user_id: user.id,
      selected_answer,
      is_correct,
      time_taken_ms: time_taken_ms || 0,
    })
    .select()
    .single();

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ answer, is_correct });
}
```

- [ ] **Step 2: Create battle settlement API**

Create `learning-arena/src/app/api/battle/settle/route.ts`:

```typescript
import { NextResponse } from 'next/server';
import { createServerSupabase } from '@/lib/supabase-server';
import { calculateElo } from '@/lib/elo';

export async function POST(request: Request) {
  const supabase = await createServerSupabase();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { battle_id } = await request.json();

  // Fetch battle with questions count
  const { data: battle } = await supabase
    .from('battles')
    .select('*')
    .eq('id', battle_id)
    .eq('status', 'active')
    .single();

  if (!battle) {
    return NextResponse.json({ error: 'Battle not found or already settled' }, { status: 404 });
  }

  // Count answers for each player
  const { data: answers } = await supabase
    .from('answers')
    .select('user_id, is_correct')
    .eq('battle_id', battle_id);

  if (!answers) {
    return NextResponse.json({ error: 'No answers found' }, { status: 400 });
  }

  const challengerCorrect = answers.filter(a => a.user_id === battle.challenger_id && a.is_correct).length;
  const opponentCorrect = answers.filter(a => a.user_id === battle.opponent_id && a.is_correct).length;

  // Both must have answered all 5 questions
  const challengerTotal = answers.filter(a => a.user_id === battle.challenger_id).length;
  const opponentTotal = answers.filter(a => a.user_id === battle.opponent_id).length;

  if (challengerTotal < 5 || opponentTotal < 5) {
    return NextResponse.json({ error: 'Both players must answer all questions' }, { status: 400 });
  }

  // Determine winner
  let outcome: 'win' | 'loss' | 'draw';
  let winner_id: string | null = null;
  if (challengerCorrect > opponentCorrect) {
    outcome = 'win';
    winner_id = battle.challenger_id;
  } else if (opponentCorrect > challengerCorrect) {
    outcome = 'loss';
    winner_id = battle.opponent_id;
  } else {
    outcome = 'draw';
  }

  // Fetch ELO ratings
  const { data: challenger } = await supabase.from('profiles').select('elo_rating, total_wins, total_losses').eq('id', battle.challenger_id).single();
  const { data: opponent } = await supabase.from('profiles').select('elo_rating, total_wins, total_losses').eq('id', battle.opponent_id).single();

  if (!challenger || !opponent) {
    return NextResponse.json({ error: 'Player profiles not found' }, { status: 500 });
  }

  const isNewChallenger = (challenger.total_wins + challenger.total_losses) < 10;
  const isNewOpponent = (opponent.total_wins + opponent.total_losses) < 10;

  const challengerElo = calculateElo(challenger.elo_rating, opponent.elo_rating, outcome, { isNewPlayer: isNewChallenger });
  const opponentOutcome = outcome === 'win' ? 'loss' : outcome === 'loss' ? 'win' : 'draw';
  const opponentElo = calculateElo(opponent.elo_rating, challenger.elo_rating, opponentOutcome, { isNewPlayer: isNewOpponent });

  // Update battle
  await supabase
    .from('battles')
    .update({
      status: 'done',
      winner_id,
      elo_change: challengerElo.change,
      finished_at: new Date().toISOString(),
    })
    .eq('id', battle_id);

  // Update profiles
  await supabase.from('profiles').update({
    elo_rating: challengerElo.newRating,
    total_wins: challenger.total_wins + (outcome === 'win' ? 1 : 0),
    total_losses: challenger.total_losses + (outcome === 'loss' ? 1 : 0),
  }).eq('id', battle.challenger_id);

  await supabase.from('profiles').update({
    elo_rating: opponentElo.newRating,
    total_wins: opponent.total_wins + (opponentOutcome === 'win' ? 1 : 0),
    total_losses: opponent.total_losses + (opponentOutcome === 'loss' ? 1 : 0),
  }).eq('id', battle.opponent_id);

  return NextResponse.json({
    winner_id,
    challenger: { score: challengerCorrect, elo_change: challengerElo.change, new_elo: challengerElo.newRating },
    opponent: { score: opponentCorrect, elo_change: opponentElo.change, new_elo: opponentElo.newRating },
  });
}
```

- [ ] **Step 3: Commit**

```bash
git add learning-arena/src/app/api/battle/
git commit -m "feat(arena): add battle answer submission + ELO settlement endpoints"
```

---

### Task 9: NavBar + AuthGuard Components

**Files:**
- Create: `learning-arena/src/components/AuthGuard.tsx`
- Create: `learning-arena/src/components/NavBar.tsx`

- [ ] **Step 1: Create AuthGuard**

Create `learning-arena/src/components/AuthGuard.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@/lib/supabase-browser';
import type { Profile } from '@/lib/types';

export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    async function load() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
        return;
      }
      const { data } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();
      setProfile(data);
      setLoading(false);
    }
    load();
  }, []);

  return { profile, loading };
}
```

- [ ] **Step 2: Create NavBar**

Create `learning-arena/src/components/NavBar.tsx`:

```tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { createClient } from '@/lib/supabase-browser';

const links = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/courses', label: 'Courses' },
  { href: '/arena', label: 'Arena' },
  { href: '/leaderboard', label: 'Leaderboard' },
];

export function NavBar({ displayName }: { displayName?: string }) {
  const pathname = usePathname();
  const supabase = createClient();

  async function handleLogout() {
    await supabase.auth.signOut();
    window.location.href = '/login';
  }

  return (
    <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="font-bold text-lg">Arena</Link>
          <div className="flex gap-4">
            {links.map(l => (
              <Link
                key={l.href}
                href={l.href}
                className={`text-sm ${pathname.startsWith(l.href) ? 'text-white' : 'text-gray-500 hover:text-gray-300'}`}
              >
                {l.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-4">
          {displayName && <span className="text-sm text-gray-400">{displayName}</span>}
          <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-white">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add learning-arena/src/components/
git commit -m "feat(arena): add NavBar + useProfile hook"
```

---

### Task 10: Dashboard Page

**Files:**
- Create: `learning-arena/src/app/dashboard/page.tsx`

- [ ] **Step 1: Create dashboard page**

Create `learning-arena/src/app/dashboard/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { createClient } from '@/lib/supabase-browser';
import Link from 'next/link';
import type { Course, Battle, Topic } from '@/lib/types';

export default function DashboardPage() {
  const { profile, loading } = useProfile();
  const [courses, setCourses] = useState<Course[]>([]);
  const [battles, setBattles] = useState<(Battle & { topic: Topic })[]>([]);
  const supabase = createClient();

  useEffect(() => {
    if (!profile) return;

    async function load() {
      const { data: c } = await supabase
        .from('courses')
        .select('*')
        .eq('user_id', profile!.id)
        .order('imported_at', { ascending: false })
        .limit(5);
      setCourses(c || []);

      const { data: b } = await supabase
        .from('battles')
        .select('*, topic:topics(*)')
        .or(`challenger_id.eq.${profile!.id},opponent_id.eq.${profile!.id}`)
        .order('created_at', { ascending: false })
        .limit(5);
      setBattles((b as any) || []);
    }
    load();
  }, [profile]);

  if (loading) return <div className="min-h-screen bg-gray-950" />;

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* ELO Card */}
        <div className="bg-gray-900 rounded-xl p-6 mb-8 border border-gray-800">
          <div className="text-gray-400 text-sm">Your Rating</div>
          <div className="text-4xl font-bold mt-1">{profile?.elo_rating}</div>
          <div className="text-gray-500 text-sm mt-1">
            {profile?.total_wins}W / {profile?.total_losses}L
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Courses */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">My Courses</h2>
              <Link href="/courses" className="text-sm text-blue-400 hover:text-blue-300">Manage</Link>
            </div>
            {courses.length === 0 ? (
              <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 text-gray-500 text-sm">
                No courses yet. <Link href="/courses" className="text-blue-400">Import from Canvas</Link>
              </div>
            ) : (
              <div className="space-y-2">
                {courses.map(c => (
                  <div key={c.id} className="bg-gray-900 rounded-lg p-3 border border-gray-800 text-sm">
                    {c.name}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Battles */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Recent Battles</h2>
              <Link href="/arena" className="text-sm text-blue-400 hover:text-blue-300">Arena</Link>
            </div>
            {battles.length === 0 ? (
              <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 text-gray-500 text-sm">
                No battles yet. <Link href="/arena" className="text-blue-400">Find an opponent</Link>
              </div>
            ) : (
              <div className="space-y-2">
                {battles.map(b => (
                  <Link key={b.id} href={b.status === 'done' ? `/battle/${b.id}/result` : `/battle/${b.id}`}>
                    <div className="bg-gray-900 rounded-lg p-3 border border-gray-800 text-sm flex justify-between">
                      <span>{b.topic?.name || 'Unknown'}</span>
                      <span className={b.status === 'done' ? 'text-green-400' : 'text-yellow-400'}>
                        {b.status}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add learning-arena/src/app/dashboard/
git commit -m "feat(arena): add dashboard page with ELO card, courses, recent battles"
```

---

### Task 11: Courses Page (Canvas Import + Topic Extraction)

**Files:**
- Create: `learning-arena/src/app/courses/page.tsx`

- [ ] **Step 1: Create courses page**

Create `learning-arena/src/app/courses/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { createClient } from '@/lib/supabase-browser';
import type { Course, Topic } from '@/lib/types';

export default function CoursesPage() {
  const { profile, loading } = useProfile();
  const supabase = createClient();
  const [courses, setCourses] = useState<(Course & { topics?: Topic[] })[]>([]);
  const [canvasUrl, setCanvasUrl] = useState('');
  const [canvasToken, setCanvasToken] = useState('');
  const [importing, setImporting] = useState(false);
  const [extracting, setExtracting] = useState<string | null>(null);

  useEffect(() => {
    if (!profile) return;
    loadCourses();
    setCanvasUrl(profile.canvas_url || '');
  }, [profile]);

  async function loadCourses() {
    const { data } = await supabase
      .from('courses')
      .select('*, topics(*)')
      .eq('user_id', profile!.id)
      .order('imported_at', { ascending: false });
    setCourses((data as any) || []);
  }

  async function handleImport() {
    if (!canvasUrl || !canvasToken) return;
    setImporting(true);
    const res = await fetch('/api/canvas/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ canvas_url: canvasUrl, canvas_token: canvasToken }),
    });
    const data = await res.json();
    if (res.ok) {
      await loadCourses();
    } else {
      alert(data.error || 'Import failed');
    }
    setImporting(false);
  }

  async function handleExtractTopics(courseId: string) {
    setExtracting(courseId);
    const res = await fetch('/api/topics/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ course_id: courseId }),
    });
    if (res.ok) {
      await loadCourses();
    } else {
      const data = await res.json();
      alert(data.error || 'Extraction failed');
    }
    setExtracting(null);
  }

  if (loading) return <div className="min-h-screen bg-gray-950" />;

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Courses</h1>

        {/* Canvas Import Section */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-8">
          <h2 className="font-semibold mb-4">Import from Canvas</h2>
          <div className="space-y-3">
            <input
              type="url"
              placeholder="Canvas URL (e.g., https://uncch.instructure.com)"
              value={canvasUrl}
              onChange={e => setCanvasUrl(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm"
            />
            <input
              type="password"
              placeholder="Canvas API Token"
              value={canvasToken}
              onChange={e => setCanvasToken(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm"
            />
            <button
              onClick={handleImport}
              disabled={importing || !canvasUrl || !canvasToken}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-500 disabled:opacity-50"
            >
              {importing ? 'Importing...' : 'Import Courses'}
            </button>
          </div>
        </div>

        {/* Course List */}
        <div className="space-y-4">
          {courses.map(course => (
            <div key={course.id} className="bg-gray-900 rounded-xl p-5 border border-gray-800">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">{course.name}</h3>
                {(!course.topics || course.topics.length === 0) && (
                  <button
                    onClick={() => handleExtractTopics(course.id)}
                    disabled={extracting === course.id}
                    className="text-sm px-3 py-1 bg-purple-600 rounded-lg hover:bg-purple-500 disabled:opacity-50"
                  >
                    {extracting === course.id ? 'Extracting...' : 'Extract Topics'}
                  </button>
                )}
              </div>
              {course.topics && course.topics.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {course.topics.map(t => (
                    <span
                      key={t.id}
                      className="text-xs px-2 py-1 bg-gray-800 text-gray-300 rounded-full"
                    >
                      {t.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add learning-arena/src/app/courses/
git commit -m "feat(arena): add courses page with Canvas import + topic extraction"
```

---

### Task 12: Arena Page (Find Opponents + Create Battle)

**Files:**
- Create: `learning-arena/src/app/arena/page.tsx`

- [ ] **Step 1: Create arena page**

Create `learning-arena/src/app/arena/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { createClient } from '@/lib/supabase-browser';
import { useRouter } from 'next/navigation';
import type { Topic, Profile, Battle } from '@/lib/types';

interface Opponent {
  id: string;
  display_name: string;
  avatar_url: string | null;
  elo_rating: number;
  shared_topics: Topic[];
}

export default function ArenaPage() {
  const { profile, loading } = useProfile();
  const supabase = createClient();
  const router = useRouter();
  const [myTopics, setMyTopics] = useState<Topic[]>([]);
  const [opponents, setOpponents] = useState<Opponent[]>([]);
  const [pendingBattles, setPendingBattles] = useState<(Battle & { topic: Topic; challenger: Profile; opponent: Profile })[]>([]);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!profile) return;
    loadData();
  }, [profile]);

  async function loadData() {
    // Load my topics
    const { data: courses } = await supabase
      .from('courses')
      .select('id')
      .eq('user_id', profile!.id);

    if (courses && courses.length > 0) {
      const { data: topics } = await supabase
        .from('topics')
        .select('*')
        .in('course_id', courses.map(c => c.id));
      setMyTopics(topics || []);

      // Find opponents: users who have overlapping normalized_tags
      if (topics && topics.length > 0) {
        const myTags = topics.map(t => t.normalized_tag);
        const { data: matchingTopics } = await supabase
          .from('topics')
          .select('*, course:courses(user_id)')
          .in('normalized_tag', myTags);

        // Group by user_id, exclude self
        const userMap = new Map<string, Topic[]>();
        for (const t of matchingTopics || []) {
          const userId = (t.course as any)?.user_id;
          if (userId && userId !== profile!.id) {
            if (!userMap.has(userId)) userMap.set(userId, []);
            userMap.get(userId)!.push(t);
          }
        }

        // Fetch profiles for matched users
        const userIds = Array.from(userMap.keys());
        if (userIds.length > 0) {
          const { data: profiles } = await supabase
            .from('profiles')
            .select('*')
            .in('id', userIds);

          setOpponents(
            (profiles || []).map(p => ({
              ...p,
              shared_topics: userMap.get(p.id) || [],
            }))
          );
        }
      }
    }

    // Load pending battles for me
    const { data: battles } = await supabase
      .from('battles')
      .select('*, topic:topics(*), challenger:profiles!battles_challenger_id_fkey(*), opponent:profiles!battles_opponent_id_fkey(*)')
      .or(`challenger_id.eq.${profile!.id},opponent_id.eq.${profile!.id}`)
      .in('status', ['pending', 'active'])
      .order('created_at', { ascending: false });
    setPendingBattles((battles as any) || []);
  }

  async function handleChallenge(opponentId: string, topicId: string) {
    setCreating(true);
    const res = await fetch('/api/battle/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic_id: topicId, opponent_id: opponentId }),
    });
    const data = await res.json();
    if (res.ok) {
      router.push(`/battle/${data.battle.id}`);
    } else {
      alert(data.error || 'Failed to create battle');
    }
    setCreating(false);
  }

  if (loading) return <div className="min-h-screen bg-gray-950" />;

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Arena</h1>

        {/* Active Battles */}
        {pendingBattles.length > 0 && (
          <div className="mb-8">
            <h2 className="font-semibold mb-3 text-yellow-400">Active Battles</h2>
            <div className="space-y-2">
              {pendingBattles.map(b => {
                const isChallenger = b.challenger_id === profile?.id;
                const other = isChallenger ? b.opponent : b.challenger;
                return (
                  <button
                    key={b.id}
                    onClick={() => router.push(`/battle/${b.id}`)}
                    className="w-full bg-gray-900 rounded-lg p-4 border border-yellow-800/50 text-left hover:border-yellow-600/50 transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="text-sm text-gray-400">vs </span>
                        <span className="font-medium">{other?.display_name}</span>
                        <span className="text-gray-500 text-sm ml-2">({other?.elo_rating})</span>
                      </div>
                      <span className="text-xs px-2 py-1 bg-yellow-900/50 text-yellow-400 rounded">
                        {b.topic?.name}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Opponents */}
        <h2 className="font-semibold mb-3">Available Opponents</h2>
        {opponents.length === 0 ? (
          <div className="bg-gray-900 rounded-lg p-6 border border-gray-800 text-gray-500 text-center">
            {myTopics.length === 0
              ? 'Import courses and extract topics first to find opponents.'
              : 'No matching opponents found yet. Share the app to get more users!'}
          </div>
        ) : (
          <div className="space-y-3">
            {opponents.map(opp => (
              <div key={opp.id} className="bg-gray-900 rounded-xl p-5 border border-gray-800">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <span className="font-medium">{opp.display_name}</span>
                    <span className="text-gray-500 text-sm ml-2">ELO {opp.elo_rating}</span>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {opp.shared_topics.map(t => (
                    <button
                      key={t.id}
                      onClick={() => handleChallenge(opp.id, t.id)}
                      disabled={creating}
                      className="text-xs px-3 py-1.5 bg-red-900/30 text-red-400 border border-red-800/50 rounded-full hover:bg-red-800/40 transition-colors disabled:opacity-50"
                    >
                      Challenge: {t.name}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add learning-arena/src/app/arena/
git commit -m "feat(arena): add arena page with opponent discovery + challenge buttons"
```

---

### Task 13: Battle Page (Answer Questions)

**Files:**
- Create: `learning-arena/src/app/battle/[id]/page.tsx`
- Create: `learning-arena/src/store/battle.ts`
- Create: `learning-arena/src/components/QuestionCard.tsx`

- [ ] **Step 1: Create Zustand battle store**

Create `learning-arena/src/store/battle.ts`:

```typescript
import { create } from 'zustand';
import type { Question } from '@/lib/types';

interface BattleState {
  questions: Question[];
  currentIndex: number;
  answers: Record<string, { selected: string; timeMs: number }>;
  startTime: number;
  setQuestions: (q: Question[]) => void;
  submitAnswer: (questionId: string, selected: string, timeMs: number) => void;
  nextQuestion: () => void;
  isComplete: () => boolean;
}

export const useBattleStore = create<BattleState>((set, get) => ({
  questions: [],
  currentIndex: 0,
  answers: {},
  startTime: Date.now(),

  setQuestions: (questions) => set({ questions, currentIndex: 0, answers: {}, startTime: Date.now() }),

  submitAnswer: (questionId, selected, timeMs) =>
    set(state => ({
      answers: { ...state.answers, [questionId]: { selected, timeMs } },
    })),

  nextQuestion: () =>
    set(state => ({
      currentIndex: Math.min(state.currentIndex + 1, state.questions.length - 1),
      startTime: Date.now(),
    })),

  isComplete: () => {
    const { questions, answers } = get();
    return questions.length > 0 && Object.keys(answers).length >= questions.length;
  },
}));
```

- [ ] **Step 2: Create QuestionCard component**

Create `learning-arena/src/components/QuestionCard.tsx`:

```tsx
'use client';

interface QuestionCardProps {
  questionNumber: number;
  totalQuestions: number;
  questionText: string;
  options: { a: string; b: string; c: string; d: string };
  selectedAnswer: string | null;
  onSelect: (answer: string) => void;
  disabled: boolean;
}

export function QuestionCard({
  questionNumber,
  totalQuestions,
  questionText,
  options,
  selectedAnswer,
  onSelect,
  disabled,
}: QuestionCardProps) {
  const optionKeys = ['a', 'b', 'c', 'd'] as const;

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      <div className="text-sm text-gray-500 mb-2">
        Question {questionNumber} of {totalQuestions}
      </div>
      <h2 className="text-lg font-medium mb-6">{questionText}</h2>
      <div className="space-y-3">
        {optionKeys.map(key => (
          <button
            key={key}
            onClick={() => onSelect(key)}
            disabled={disabled}
            className={`w-full text-left p-4 rounded-lg border transition-colors ${
              selectedAnswer === key
                ? 'border-blue-500 bg-blue-900/30 text-blue-200'
                : 'border-gray-700 bg-gray-800 hover:border-gray-600'
            } disabled:opacity-60`}
          >
            <span className="font-mono text-sm text-gray-500 mr-3">{key.toUpperCase()}</span>
            {options[key]}
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create battle page**

Create `learning-arena/src/app/battle/[id]/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { QuestionCard } from '@/components/QuestionCard';
import { useBattleStore } from '@/store/battle';
import { createClient } from '@/lib/supabase-browser';

export default function BattlePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { profile, loading } = useProfile();
  const supabase = createClient();
  const store = useBattleStore();
  const [submitting, setSubmitting] = useState(false);
  const [battleStatus, setBattleStatus] = useState<string>('');

  useEffect(() => {
    if (!profile || !id) return;
    loadBattle();
  }, [profile, id]);

  async function loadBattle() {
    const { data: battle } = await supabase
      .from('battles')
      .select('*')
      .eq('id', id)
      .single();

    if (!battle) return;
    setBattleStatus(battle.status);

    if (battle.status === 'done') {
      router.push(`/battle/${id}/result`);
      return;
    }

    const { data: questions } = await supabase
      .from('questions')
      .select('*')
      .eq('battle_id', id)
      .order('order_index');

    if (questions) {
      store.setQuestions(questions);
    }

    // Load existing answers for this user
    const { data: existingAnswers } = await supabase
      .from('answers')
      .select('question_id, selected_answer, time_taken_ms')
      .eq('battle_id', id)
      .eq('user_id', profile!.id);

    if (existingAnswers) {
      for (const a of existingAnswers) {
        store.submitAnswer(a.question_id, a.selected_answer, a.time_taken_ms);
      }
    }
  }

  async function handleSelect(questionId: string, answer: string) {
    const timeMs = Date.now() - store.startTime;
    store.submitAnswer(questionId, answer, timeMs);

    // Submit to API
    await fetch('/api/battle/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        battle_id: id,
        question_id: questionId,
        selected_answer: answer,
        time_taken_ms: timeMs,
      }),
    });

    // Auto-advance after 500ms
    setTimeout(() => {
      if (store.currentIndex < store.questions.length - 1) {
        store.nextQuestion();
      }
    }, 500);
  }

  async function handleFinish() {
    setSubmitting(true);
    // Try to settle if both players done
    const res = await fetch('/api/battle/settle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ battle_id: id }),
    });

    if (res.ok) {
      router.push(`/battle/${id}/result`);
    } else {
      // Opponent hasn't finished yet
      router.push('/arena');
    }
    setSubmitting(false);
  }

  if (loading || store.questions.length === 0) {
    return <div className="min-h-screen bg-gray-950" />;
  }

  const currentQ = store.questions[store.currentIndex];
  const currentAnswer = store.answers[currentQ.id];
  const allAnswered = store.isComplete();

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Progress bar */}
        <div className="flex gap-1 mb-6">
          {store.questions.map((q, i) => (
            <div
              key={q.id}
              className={`h-1.5 flex-1 rounded-full ${
                store.answers[q.id]
                  ? 'bg-blue-500'
                  : i === store.currentIndex
                  ? 'bg-gray-600'
                  : 'bg-gray-800'
              }`}
            />
          ))}
        </div>

        <QuestionCard
          questionNumber={store.currentIndex + 1}
          totalQuestions={store.questions.length}
          questionText={currentQ.question_text}
          options={currentQ.options as { a: string; b: string; c: string; d: string }}
          selectedAnswer={currentAnswer?.selected ?? null}
          onSelect={(answer) => handleSelect(currentQ.id, answer)}
          disabled={!!currentAnswer}
        />

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button
            onClick={() => useBattleStore.setState(s => ({ currentIndex: Math.max(0, s.currentIndex - 1), startTime: Date.now() }))}
            disabled={store.currentIndex === 0}
            className="text-sm text-gray-500 hover:text-white disabled:opacity-30"
          >
            Previous
          </button>

          {allAnswered ? (
            <button
              onClick={handleFinish}
              disabled={submitting}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Finish Battle'}
            </button>
          ) : (
            <button
              onClick={() => store.nextQuestion()}
              disabled={store.currentIndex >= store.questions.length - 1}
              className="text-sm text-gray-500 hover:text-white disabled:opacity-30"
            >
              Next
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add learning-arena/src/app/battle/ learning-arena/src/store/ learning-arena/src/components/QuestionCard.tsx
git commit -m "feat(arena): add battle answering page with Zustand state + QuestionCard"
```

---

### Task 14: Battle Result Page

**Files:**
- Create: `learning-arena/src/app/battle/[id]/result/page.tsx`
- Create: `learning-arena/src/components/EloChange.tsx`

- [ ] **Step 1: Create EloChange component**

Create `learning-arena/src/components/EloChange.tsx`:

```tsx
export function EloChange({ change }: { change: number }) {
  if (change === 0) return <span className="text-gray-500">±0</span>;
  return (
    <span className={change > 0 ? 'text-green-400' : 'text-red-400'}>
      {change > 0 ? '+' : ''}{change}
    </span>
  );
}
```

- [ ] **Step 2: Create result page**

Create `learning-arena/src/app/battle/[id]/result/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { EloChange } from '@/components/EloChange';
import { createClient } from '@/lib/supabase-browser';
import Link from 'next/link';
import type { Battle, Profile, Question, Answer, Topic } from '@/lib/types';

export default function BattleResultPage() {
  const { id } = useParams<{ id: string }>();
  const { profile, loading } = useProfile();
  const supabase = createClient();
  const [battle, setBattle] = useState<Battle | null>(null);
  const [topic, setTopic] = useState<Topic | null>(null);
  const [challenger, setChallenger] = useState<Profile | null>(null);
  const [opponent, setOpponent] = useState<Profile | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Answer[]>([]);

  useEffect(() => {
    if (!profile || !id) return;
    loadResult();
  }, [profile, id]);

  async function loadResult() {
    const { data: b } = await supabase.from('battles').select('*').eq('id', id).single();
    if (!b) return;
    setBattle(b);

    const [topicRes, challRes, oppRes, questRes, ansRes] = await Promise.all([
      supabase.from('topics').select('*').eq('id', b.topic_id).single(),
      supabase.from('profiles').select('*').eq('id', b.challenger_id).single(),
      supabase.from('profiles').select('*').eq('id', b.opponent_id).single(),
      supabase.from('questions').select('*').eq('battle_id', id).order('order_index'),
      supabase.from('answers').select('*').eq('battle_id', id),
    ]);

    setTopic(topicRes.data);
    setChallenger(challRes.data);
    setOpponent(oppRes.data);
    setQuestions(questRes.data || []);
    setAnswers(ansRes.data || []);
  }

  if (loading || !battle || !challenger || !opponent) {
    return <div className="min-h-screen bg-gray-950" />;
  }

  const isChallenger = profile?.id === battle.challenger_id;
  const myScore = answers.filter(a => a.user_id === profile?.id && a.is_correct).length;
  const theirScore = answers.filter(a => a.user_id !== profile?.id && a.is_correct).length;
  const isWinner = battle.winner_id === profile?.id;
  const isDraw = !battle.winner_id;
  const eloChange = isChallenger ? (battle.elo_change ?? 0) : -(battle.elo_change ?? 0);

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-2xl mx-auto px-4 py-8">
        {/* Result Header */}
        <div className="text-center mb-8">
          <div className={`text-3xl font-bold ${isDraw ? 'text-yellow-400' : isWinner ? 'text-green-400' : 'text-red-400'}`}>
            {isDraw ? 'DRAW' : isWinner ? 'VICTORY' : 'DEFEAT'}
          </div>
          <div className="text-gray-500 mt-1">{topic?.name}</div>
        </div>

        {/* Score Comparison */}
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
          <div className="grid grid-cols-3 text-center">
            <div>
              <div className="text-sm text-gray-500">You</div>
              <div className="text-3xl font-bold mt-1">{myScore}</div>
              <div className="text-sm mt-1"><EloChange change={eloChange} /></div>
            </div>
            <div className="flex items-center justify-center text-gray-600 text-2xl">vs</div>
            <div>
              <div className="text-sm text-gray-500">
                {isChallenger ? opponent.display_name : challenger.display_name}
              </div>
              <div className="text-3xl font-bold mt-1">{theirScore}</div>
              <div className="text-sm mt-1"><EloChange change={-eloChange} /></div>
            </div>
          </div>
        </div>

        {/* Question Review */}
        <h3 className="font-semibold mb-3">Question Review</h3>
        <div className="space-y-3">
          {questions.map((q, i) => {
            const myAnswer = answers.find(a => a.question_id === q.id && a.user_id === profile?.id);
            return (
              <div key={q.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div className="text-sm text-gray-500 mb-1">Q{i + 1}</div>
                <div className="text-sm mb-2">{q.question_text}</div>
                <div className="flex gap-2 text-xs">
                  <span className={myAnswer?.is_correct ? 'text-green-400' : 'text-red-400'}>
                    Your answer: {myAnswer?.selected_answer?.toUpperCase() || '—'}
                  </span>
                  <span className="text-gray-600">|</span>
                  <span className="text-gray-400">
                    Correct: {q.correct_answer.toUpperCase()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 flex gap-3">
          <Link href="/arena" className="flex-1 text-center py-3 bg-blue-600 rounded-lg hover:bg-blue-500">
            Back to Arena
          </Link>
          <Link href="/leaderboard" className="flex-1 text-center py-3 bg-gray-800 rounded-lg hover:bg-gray-700">
            Leaderboard
          </Link>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add learning-arena/src/app/battle/[id]/result/ learning-arena/src/components/EloChange.tsx
git commit -m "feat(arena): add battle result page with score comparison + question review"
```

---

### Task 15: Leaderboard Page

**Files:**
- Create: `learning-arena/src/app/leaderboard/page.tsx`

- [ ] **Step 1: Create leaderboard page**

Create `learning-arena/src/app/leaderboard/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { createClient } from '@/lib/supabase-browser';
import type { LeaderboardEntry } from '@/lib/types';

export default function LeaderboardPage() {
  const { profile, loading } = useProfile();
  const supabase = createClient();
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    if (!profile) return;
    loadLeaderboard();
  }, [profile]);

  async function loadLeaderboard() {
    const { data } = await supabase
      .from('profiles')
      .select('id, display_name, avatar_url, elo_rating, total_wins, total_losses')
      .order('elo_rating', { ascending: false })
      .limit(50);
    setEntries(data || []);
  }

  if (loading) return <div className="min-h-screen bg-gray-950" />;

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Leaderboard</h1>
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-gray-800">
                <th className="text-left py-3 px-4">#</th>
                <th className="text-left py-3 px-4">Player</th>
                <th className="text-right py-3 px-4">ELO</th>
                <th className="text-right py-3 px-4">W/L</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e, i) => (
                <tr
                  key={e.id}
                  className={`border-b border-gray-800/50 ${e.id === profile?.id ? 'bg-blue-900/20' : ''}`}
                >
                  <td className="py-3 px-4 text-sm text-gray-500">{i + 1}</td>
                  <td className="py-3 px-4">
                    <span className="font-medium">{e.display_name}</span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono">{e.elo_rating}</td>
                  <td className="py-3 px-4 text-right text-sm text-gray-400">
                    {e.total_wins}/{e.total_losses}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add learning-arena/src/app/leaderboard/
git commit -m "feat(arena): add leaderboard page with ELO rankings"
```

---

### Task 16: Landing Page

**Files:**
- Modify: `learning-arena/src/app/page.tsx`

- [ ] **Step 1: Create landing page**

Replace `learning-arena/src/app/page.tsx`:

```tsx
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <nav className="max-w-5xl mx-auto px-4 w-full flex items-center justify-between h-14">
        <span className="font-bold text-lg">Learning Arena</span>
        <Link href="/login" className="text-sm px-4 py-2 bg-white text-gray-900 rounded-lg hover:bg-gray-100">
          Get Started
        </Link>
      </nav>

      <main className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-xl px-4">
          <h1 className="text-5xl font-bold mb-4">
            Learn by <span className="text-red-400">Fighting</span>
          </h1>
          <p className="text-gray-400 text-lg mb-8">
            Import your courses, let AI extract what you're learning, and challenge other students to knowledge battles. Your ELO tells the truth.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/login"
              className="px-6 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-500 transition-colors"
            >
              Enter the Arena
            </Link>
          </div>
          <div className="mt-16 grid grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-2xl mb-2">📚</div>
              <div className="text-sm font-medium">Import from Canvas</div>
              <div className="text-xs text-gray-500 mt-1">Auto-sync your course syllabi</div>
            </div>
            <div>
              <div className="text-2xl mb-2">🤖</div>
              <div className="text-sm font-medium">AI-Generated Quizzes</div>
              <div className="text-xs text-gray-500 mt-1">Tailored to your exact topics</div>
            </div>
            <div>
              <div className="text-2xl mb-2">⚔️</div>
              <div className="text-sm font-medium">Battle & Rank Up</div>
              <div className="text-xs text-gray-500 mt-1">ELO rating proves your knowledge</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add learning-arena/src/app/page.tsx
git commit -m "feat(arena): add landing page with hero + feature highlights"
```

---

### Task 17: Settings Page + Profile Page

**Files:**
- Create: `learning-arena/src/app/settings/page.tsx`
- Create: `learning-arena/src/app/profile/[id]/page.tsx`

- [ ] **Step 1: Create settings page**

Create `learning-arena/src/app/settings/page.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { createClient } from '@/lib/supabase-browser';

export default function SettingsPage() {
  const { profile, loading } = useProfile();
  const supabase = createClient();
  const [displayName, setDisplayName] = useState('');
  const [canvasUrl, setCanvasUrl] = useState('');
  const [canvasToken, setCanvasToken] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useState(() => {
    if (profile) {
      setDisplayName(profile.display_name);
      setCanvasUrl(profile.canvas_url || '');
    }
  });

  async function handleSave() {
    if (!profile) return;
    setSaving(true);
    const updates: Record<string, string> = { display_name: displayName };
    if (canvasUrl) updates.canvas_url = canvasUrl;
    if (canvasToken) updates.canvas_token = canvasToken;

    await supabase.from('profiles').update(updates).eq('id', profile.id);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  if (loading) return <div className="min-h-screen bg-gray-950" />;

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={profile?.display_name} />
      <main className="max-w-lg mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Settings</h1>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-400 block mb-1">Display Name</label>
            <input
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Canvas URL</label>
            <input
              value={canvasUrl}
              onChange={e => setCanvasUrl(e.target.value)}
              placeholder="https://uncch.instructure.com"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm text-gray-400 block mb-1">Canvas API Token</label>
            <input
              type="password"
              value={canvasToken}
              onChange={e => setCanvasToken(e.target.value)}
              placeholder="Leave blank to keep existing"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm"
            />
            <p className="text-xs text-gray-600 mt-1">
              Get your token from Canvas → Account → Settings → New Access Token
            </p>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-500 disabled:opacity-50"
          >
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Settings'}
          </button>
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 2: Create profile page**

Create `learning-arena/src/app/profile/[id]/page.tsx`:

```tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useProfile } from '@/components/AuthGuard';
import { NavBar } from '@/components/NavBar';
import { EloChange } from '@/components/EloChange';
import { createClient } from '@/lib/supabase-browser';
import type { Profile, Battle, Topic } from '@/lib/types';

export default function ProfilePage() {
  const { id } = useParams<{ id: string }>();
  const { profile: myProfile, loading } = useProfile();
  const supabase = createClient();
  const [targetProfile, setTargetProfile] = useState<Profile | null>(null);
  const [battles, setBattles] = useState<(Battle & { topic: Topic })[]>([]);

  useEffect(() => {
    if (!myProfile || !id) return;
    loadProfile();
  }, [myProfile, id]);

  async function loadProfile() {
    const { data: p } = await supabase.from('profiles').select('*').eq('id', id).single();
    setTargetProfile(p);

    const { data: b } = await supabase
      .from('battles')
      .select('*, topic:topics(*)')
      .or(`challenger_id.eq.${id},opponent_id.eq.${id}`)
      .eq('status', 'done')
      .order('finished_at', { ascending: false })
      .limit(20);
    setBattles((b as any) || []);
  }

  if (loading || !targetProfile) return <div className="min-h-screen bg-gray-950" />;

  const winRate = targetProfile.total_wins + targetProfile.total_losses > 0
    ? Math.round((targetProfile.total_wins / (targetProfile.total_wins + targetProfile.total_losses)) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-gray-950">
      <NavBar displayName={myProfile?.display_name} />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
          <h1 className="text-2xl font-bold">{targetProfile.display_name}</h1>
          <div className="grid grid-cols-3 gap-4 mt-4 text-center">
            <div>
              <div className="text-2xl font-bold">{targetProfile.elo_rating}</div>
              <div className="text-xs text-gray-500">ELO</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{targetProfile.total_wins}/{targetProfile.total_losses}</div>
              <div className="text-xs text-gray-500">W/L</div>
            </div>
            <div>
              <div className="text-2xl font-bold">{winRate}%</div>
              <div className="text-xs text-gray-500">Win Rate</div>
            </div>
          </div>
        </div>

        <h2 className="font-semibold mb-3">Battle History</h2>
        <div className="space-y-2">
          {battles.map(b => {
            const isWinner = b.winner_id === id;
            const isDraw = !b.winner_id;
            return (
              <div key={b.id} className="bg-gray-900 rounded-lg p-3 border border-gray-800 flex justify-between text-sm">
                <span>{b.topic?.name}</span>
                <span className={isDraw ? 'text-yellow-400' : isWinner ? 'text-green-400' : 'text-red-400'}>
                  {isDraw ? 'Draw' : isWinner ? 'Win' : 'Loss'}
                </span>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add learning-arena/src/app/settings/ learning-arena/src/app/profile/
git commit -m "feat(arena): add settings page + user profile page"
```

---

### Task 18: Final Integration + Smoke Test

**Files:**
- Modify: various (fix any import issues)

- [ ] **Step 1: Run build to check for errors**

```bash
cd learning-arena && npm run build
```

Fix any TypeScript or import errors that surface.

- [ ] **Step 2: Run all tests**

```bash
cd learning-arena && npx vitest run
```

Expected: All tests pass (ELO, Canvas parsing, AI parsing).

- [ ] **Step 3: Start dev server and verify key pages**

```bash
cd learning-arena && npm run dev
```

Verify these pages load without errors:
1. `/` — Landing page
2. `/login` — Login page
3. `/dashboard` — Redirects to login if not auth'd
4. After login: `/dashboard`, `/courses`, `/arena`, `/leaderboard`, `/settings`

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix(arena): resolve build errors from integration"
```

- [ ] **Step 5: Final commit with project CLAUDE.md**

Create `learning-arena/CLAUDE.md`:

```markdown
# Learning Arena

## Architecture
Next.js 16 App Router + Supabase (Auth, DB, Realtime) + Claude API.

## Key Paths
- `src/app/api/` — Backend API routes
- `src/lib/` — Shared utilities (supabase clients, AI, ELO, Canvas)
- `src/components/` — Reusable React components
- `src/store/` — Zustand stores
- `supabase/migrations/` — Database schema

## Commands
- `npm run dev` — Start dev server
- `npm run build` — Production build
- `npx vitest run` — Run tests

## Environment Variables
See `.env.local.example`
```

```bash
git add learning-arena/CLAUDE.md
git commit -m "docs(arena): add project CLAUDE.md"
```
