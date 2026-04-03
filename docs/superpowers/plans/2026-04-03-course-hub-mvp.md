# CourseHub MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an AI-powered course management tool where students upload syllabi and exams, AI parses them into structured outlines and interactive quizzes, and a dashboard tracks mastery across all courses.

**Architecture:** Next.js 16 App Router fullstack. Supabase handles auth (Google OAuth), database (PostgreSQL with RLS), and file storage. Claude API (Sonnet for syllabus parsing, Haiku for quiz generation) with structured output via tool use + Zod validation. Client state via Zustand. UI with Tailwind v4 + Lucide icons.

**Tech Stack:** Next.js 16, Supabase, Claude API, Tailwind CSS v4, Zustand, Zod, react-arborist, react-dropzone, Lucide React

---

## File Structure

```
course-hub/
├── src/
│   ├── app/
│   │   ├── page.tsx                          # Root redirect → /dashboard
│   │   ├── layout.tsx                        # Root layout (fonts, metadata)
│   │   ├── globals.css                       # Tailwind imports + custom vars
│   │   ├── login/page.tsx                    # Login page (Google OAuth)
│   │   ├── dashboard/
│   │   │   ├── layout.tsx                    # Auth guard + Sidebar wrapper
│   │   │   └── page.tsx                      # Course grid + new course button
│   │   ├── course/
│   │   │   └── [id]/
│   │   │       ├── page.tsx                  # Course detail (outline tab default)
│   │   │       ├── practice/page.tsx         # Practice mode
│   │   │       └── progress/page.tsx         # Progress heatmap
│   │   ├── new-course/page.tsx               # Upload syllabus → preview → create
│   │   └── api/
│   │       ├── courses/route.ts              # GET (list), POST (create)
│   │       ├── courses/[id]/route.ts         # GET, PATCH, DELETE
│   │       ├── courses/[id]/outline/route.ts # GET, PUT (bulk update)
│   │       ├── upload/route.ts               # POST (file upload → storage)
│   │       ├── parse/route.ts                # POST (AI parse file)
│   │       ├── questions/route.ts            # GET (by course), POST (generate)
│   │       └── attempts/route.ts             # POST (record answer)
│   ├── components/
│   │   ├── Sidebar.tsx                       # Left nav: course list + links
│   │   ├── CourseCard.tsx                     # Dashboard card
│   │   ├── FileDropzone.tsx                  # Drag-and-drop upload
│   │   ├── OutlineTree.tsx                   # react-arborist tree editor
│   │   ├── OutlinePreview.tsx                # Read-only outline for new-course flow
│   │   ├── QuestionCard.tsx                  # Single question (MC/fill/short)
│   │   ├── ProgressGrid.tsx                  # Knowledge point mastery heatmap
│   │   └── CourseTabs.tsx                    # Tab nav for course detail
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts                     # Browser Supabase client
│   │   │   └── server.ts                     # Server Supabase client (cookies)
│   │   ├── ai.ts                             # Claude API helpers
│   │   ├── schemas.ts                        # Zod schemas for all entities
│   │   └── mastery.ts                        # Mastery calculation logic
│   ├── store/
│   │   └── course-store.ts                   # Zustand store
│   └── types.ts                              # TypeScript types (inferred from Zod)
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
├── .env.local.example                        # Required env vars
├── next.config.ts
├── tailwind.config.ts
├── package.json
└── tsconfig.json
```

---

### Task 1: Project Scaffold

**Files:**
- Create: `course-hub/package.json`
- Create: `course-hub/next.config.ts`
- Create: `course-hub/tsconfig.json`
- Create: `course-hub/tailwind.config.ts`
- Create: `course-hub/src/app/globals.css`
- Create: `course-hub/src/app/layout.tsx`
- Create: `course-hub/src/app/page.tsx`
- Create: `course-hub/.env.local.example`
- Create: `course-hub/.gitignore`

- [ ] **Step 1: Create Next.js project**

```bash
cd "/Users/shaoq/Desktop/VScode Workspace"
npx create-next-app@latest course-hub --typescript --tailwind --eslint --app --src-dir --no-import-alias --use-npm
```

- [ ] **Step 2: Install dependencies**

```bash
cd course-hub
npm install @supabase/supabase-js @supabase/ssr @anthropic-ai/sdk zustand zod react-dropzone react-arborist lucide-react
```

- [ ] **Step 3: Create .env.local.example**

```bash
cat > .env.local.example << 'EOF'
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
ANTHROPIC_API_KEY=your-anthropic-api-key
EOF
```

- [ ] **Step 4: Set up globals.css with warm color palette**

Replace `src/app/globals.css` with:
```css
@import "tailwindcss";

:root {
  --bg-primary: #f8f6f1;
  --bg-surface: #fffefc;
  --text-primary: #1a1814;
  --text-secondary: #6b6560;
  --accent: #c4a97d;
  --accent-hover: #b89a6e;
  --success: #4a7c59;
  --warning: #c49a3c;
  --danger: #a85444;
  --border: #e8e4de;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.7;
}
```

- [ ] **Step 5: Update root layout**

Replace `src/app/layout.tsx` with:
```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CourseHub",
  description: "AI-powered course management for students",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 6: Set root page to redirect**

Replace `src/app/page.tsx` with:
```tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");
}
```

- [ ] **Step 7: Verify dev server starts**

```bash
cd course-hub && npm run dev
```
Expected: Server starts on localhost:3000, redirects to /dashboard (404 is fine — page not built yet).

- [ ] **Step 8: Commit**

```bash
git add course-hub/
git commit -m "feat(course-hub): scaffold Next.js 16 project with deps"
```

---

### Task 2: Types & Zod Schemas

**Files:**
- Create: `course-hub/src/types.ts`
- Create: `course-hub/src/lib/schemas.ts`

- [ ] **Step 1: Define TypeScript types**

Create `src/types.ts`:
```typescript
export type CourseStatus = "active" | "archived";
export type NodeType = "week" | "chapter" | "topic" | "knowledge_point";
export type UploadType = "syllabus" | "exam" | "practice" | "notes" | "other";
export type UploadStatus = "pending" | "parsing" | "done" | "failed";
export type QuestionType = "multiple_choice" | "fill_blank" | "short_answer" | "true_false";
export type MasteryLevel = "mastered" | "reviewing" | "weak" | "untested";

export interface Course {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  professor: string | null;
  semester: string | null;
  status: CourseStatus;
  created_at: string;
  updated_at: string;
}

export interface OutlineNode {
  id: string;
  course_id: string;
  parent_id: string | null;
  title: string;
  type: NodeType;
  content: string | null;
  order: number;
}

export interface Upload {
  id: string;
  course_id: string;
  file_url: string;
  file_name: string;
  file_type: string;
  upload_type: UploadType;
  parsed_content: unknown | null;
  status: UploadStatus;
  created_at: string;
}

export interface Question {
  id: string;
  course_id: string;
  source_upload_id: string | null;
  knowledge_point_id: string | null;
  type: QuestionType;
  stem: string;
  options: { label: string; text: string }[] | null;
  answer: string;
  explanation: string | null;
  difficulty: number;
  created_at: string;
}

export interface Attempt {
  id: string;
  user_id: string;
  question_id: string;
  user_answer: string;
  is_correct: boolean;
  answered_at: string;
}

// AI output types
export interface ParsedSyllabus {
  title: string;
  description: string;
  professor: string | null;
  semester: string | null;
  nodes: ParsedOutlineNode[];
}

export interface ParsedOutlineNode {
  title: string;
  type: NodeType;
  content: string | null;
  children: ParsedOutlineNode[];
}

export interface ParsedQuestion {
  type: QuestionType;
  stem: string;
  options: { label: string; text: string }[] | null;
  answer: string;
  explanation: string | null;
  difficulty: number;
}
```

- [ ] **Step 2: Define Zod schemas for validation**

Create `src/lib/schemas.ts`:
```typescript
import { z } from "zod";

export const courseCreateSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(2000).nullable().default(null),
  professor: z.string().max(100).nullable().default(null),
  semester: z.string().max(50).nullable().default(null),
});

export const courseUpdateSchema = courseCreateSchema.partial().extend({
  status: z.enum(["active", "archived"]).optional(),
});

export const outlineNodeSchema = z.object({
  id: z.string().uuid(),
  parent_id: z.string().uuid().nullable(),
  title: z.string().min(1),
  type: z.enum(["week", "chapter", "topic", "knowledge_point"]),
  content: z.string().nullable().default(null),
  order: z.number().int().min(0),
});

export const parsedOutlineNodeSchema: z.ZodType<{
  title: string;
  type: "week" | "chapter" | "topic" | "knowledge_point";
  content: string | null;
  children: unknown[];
}> = z.object({
  title: z.string(),
  type: z.enum(["week", "chapter", "topic", "knowledge_point"]),
  content: z.string().nullable().default(null),
  children: z.lazy(() => parsedOutlineNodeSchema.array()).default([]),
});

export const parsedSyllabusSchema = z.object({
  title: z.string(),
  description: z.string(),
  professor: z.string().nullable().default(null),
  semester: z.string().nullable().default(null),
  nodes: parsedOutlineNodeSchema.array(),
});

export const parsedQuestionSchema = z.object({
  type: z.enum(["multiple_choice", "fill_blank", "short_answer", "true_false"]),
  stem: z.string().min(1),
  options: z.array(z.object({ label: z.string(), text: z.string() })).nullable().default(null),
  answer: z.string().min(1),
  explanation: z.string().nullable().default(null),
  difficulty: z.number().int().min(1).max(5).default(3),
});

export const attemptCreateSchema = z.object({
  question_id: z.string().uuid(),
  user_answer: z.string().min(1),
});
```

- [ ] **Step 3: Commit**

```bash
git add src/types.ts src/lib/schemas.ts
git commit -m "feat(course-hub): add TypeScript types and Zod schemas"
```

---

### Task 3: Database Schema & Supabase Setup

**Files:**
- Create: `course-hub/supabase/migrations/001_initial_schema.sql`

- [ ] **Step 1: Create Supabase project**

Go to https://supabase.com/dashboard and create a new project named "course-hub". Copy the URL, anon key, and service role key into `.env.local`.

- [ ] **Step 2: Write migration SQL**

Create `supabase/migrations/001_initial_schema.sql`:
```sql
-- Courses
create table public.courses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null,
  description text,
  professor text,
  semester text,
  status text not null default 'active' check (status in ('active', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_courses_user_id on public.courses(user_id);
create index idx_courses_status on public.courses(status);

alter table public.courses enable row level security;
create policy "Users can CRUD own courses" on public.courses
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Outline Nodes (adjacency list tree)
create table public.outline_nodes (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  parent_id uuid references public.outline_nodes(id) on delete cascade,
  title text not null,
  type text not null check (type in ('week', 'chapter', 'topic', 'knowledge_point')),
  content text,
  "order" int not null default 0
);

create index idx_outline_course on public.outline_nodes(course_id);
create index idx_outline_parent on public.outline_nodes(parent_id);

alter table public.outline_nodes enable row level security;
create policy "Users can CRUD own outline nodes" on public.outline_nodes
  for all using (
    exists (select 1 from public.courses where courses.id = outline_nodes.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = outline_nodes.course_id and courses.user_id = auth.uid())
  );

-- Uploads
create table public.uploads (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  file_url text not null,
  file_name text not null,
  file_type text not null,
  upload_type text not null default 'other' check (upload_type in ('syllabus', 'exam', 'practice', 'notes', 'other')),
  parsed_content jsonb,
  status text not null default 'pending' check (status in ('pending', 'parsing', 'done', 'failed')),
  created_at timestamptz not null default now()
);

create index idx_uploads_course on public.uploads(course_id);

alter table public.uploads enable row level security;
create policy "Users can CRUD own uploads" on public.uploads
  for all using (
    exists (select 1 from public.courses where courses.id = uploads.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = uploads.course_id and courses.user_id = auth.uid())
  );

-- Questions
create table public.questions (
  id uuid primary key default gen_random_uuid(),
  course_id uuid not null references public.courses(id) on delete cascade,
  source_upload_id uuid references public.uploads(id) on delete set null,
  knowledge_point_id uuid references public.outline_nodes(id) on delete set null,
  type text not null check (type in ('multiple_choice', 'fill_blank', 'short_answer', 'true_false')),
  stem text not null,
  options jsonb,
  answer text not null,
  explanation text,
  difficulty int not null default 3 check (difficulty between 1 and 5),
  created_at timestamptz not null default now()
);

create index idx_questions_course on public.questions(course_id);
create index idx_questions_kp on public.questions(knowledge_point_id);

alter table public.questions enable row level security;
create policy "Users can CRUD own questions" on public.questions
  for all using (
    exists (select 1 from public.courses where courses.id = questions.course_id and courses.user_id = auth.uid())
  )
  with check (
    exists (select 1 from public.courses where courses.id = questions.course_id and courses.user_id = auth.uid())
  );

-- Attempts
create table public.attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id uuid not null references public.questions(id) on delete cascade,
  user_answer text not null,
  is_correct boolean not null,
  answered_at timestamptz not null default now()
);

create index idx_attempts_user on public.attempts(user_id);
create index idx_attempts_question on public.attempts(question_id);

alter table public.attempts enable row level security;
create policy "Users can CRUD own attempts" on public.attempts
  for all using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Storage bucket for uploads
insert into storage.buckets (id, name, public)
values ('course-files', 'course-files', false);

create policy "Users can upload course files" on storage.objects
  for insert with check (bucket_id = 'course-files' and auth.uid() is not null);

create policy "Users can read own course files" on storage.objects
  for select using (bucket_id = 'course-files' and auth.uid() is not null);

create policy "Users can delete own course files" on storage.objects
  for delete using (bucket_id = 'course-files' and auth.uid() is not null);

-- Updated_at trigger
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger courses_updated_at
  before update on public.courses
  for each row execute function public.set_updated_at();
```

- [ ] **Step 3: Apply migration via Supabase dashboard**

Go to Supabase SQL Editor → paste the migration → Run. Verify all tables appear in Table Editor.

- [ ] **Step 4: Enable Google OAuth in Supabase**

Go to Supabase → Authentication → Providers → Enable Google. Add OAuth client ID and secret from Google Cloud Console.

- [ ] **Step 5: Commit**

```bash
git add supabase/
git commit -m "feat(course-hub): database schema with RLS policies"
```

---

### Task 4: Supabase Client Helpers

**Files:**
- Create: `course-hub/src/lib/supabase/client.ts`
- Create: `course-hub/src/lib/supabase/server.ts`
- Create: `course-hub/src/lib/supabase/middleware.ts`
- Create: `course-hub/src/middleware.ts`

- [ ] **Step 1: Create browser client**

Create `src/lib/supabase/client.ts`:
```typescript
import { createBrowserClient } from "@supabase/ssr";

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}
```

- [ ] **Step 2: Create server client**

Create `src/lib/supabase/server.ts`:
```typescript
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

export async function createClient() {
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
          for (const { name, value, options } of cookiesToSet) {
            cookieStore.set(name, value, options);
          }
        },
      },
    }
  );
}
```

- [ ] **Step 3: Create middleware helper**

Create `src/lib/supabase/middleware.ts`:
```typescript
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          for (const { name, value } of cookiesToSet) {
            request.cookies.set(name, value);
          }
          supabaseResponse = NextResponse.next({ request });
          for (const { name, value, options } of cookiesToSet) {
            supabaseResponse.cookies.set(name, value, options);
          }
        },
      },
    }
  );

  const { data: { user } } = await supabase.auth.getUser();

  // Redirect unauthenticated users to login (except login page and API routes)
  if (!user && !request.nextUrl.pathname.startsWith("/login") && !request.nextUrl.pathname.startsWith("/api") && !request.nextUrl.pathname.startsWith("/auth")) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
```

- [ ] **Step 4: Create Next.js middleware**

Create `src/middleware.ts`:
```typescript
import { type NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

export async function middleware(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/supabase/ src/middleware.ts
git commit -m "feat(course-hub): Supabase client helpers + auth middleware"
```

---

### Task 5: Login Page + Auth Callback

**Files:**
- Create: `course-hub/src/app/login/page.tsx`
- Create: `course-hub/src/app/auth/callback/route.ts`

- [ ] **Step 1: Create login page**

Create `src/app/login/page.tsx`:
```tsx
"use client";

import { createClient } from "@/lib/supabase/client";
import { LogIn } from "lucide-react";

export default function LoginPage() {
  const supabase = createClient();

  async function signInWithGoogle() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "var(--bg-primary)" }}>
      <div className="p-8 rounded-2xl shadow-sm max-w-sm w-full" style={{ backgroundColor: "var(--bg-surface)" }}>
        <h1 className="text-2xl font-semibold mb-2" style={{ color: "var(--text-primary)" }}>CourseHub</h1>
        <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
          Upload your syllabus. AI does the rest.
        </p>
        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-colors cursor-pointer"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = "var(--accent-hover)")}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = "var(--accent)")}
        >
          <LogIn size={18} />
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create auth callback route**

Create `src/app/auth/callback/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");

  if (code) {
    const supabase = await createClient();
    await supabase.auth.exchangeCodeForSession(code);
  }

  return NextResponse.redirect(`${origin}/dashboard`);
}
```

- [ ] **Step 3: Verify login flow**

Run dev server, visit `/login`, click Google sign-in. After OAuth, should redirect to `/dashboard`.

- [ ] **Step 4: Commit**

```bash
git add src/app/login/ src/app/auth/
git commit -m "feat(course-hub): login page with Google OAuth"
```

---

### Task 6: App Shell (Sidebar + Dashboard Layout)

**Files:**
- Create: `course-hub/src/components/Sidebar.tsx`
- Create: `course-hub/src/app/dashboard/layout.tsx`
- Create: `course-hub/src/app/dashboard/page.tsx`

- [ ] **Step 1: Create Sidebar component**

Create `src/components/Sidebar.tsx`:
```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Plus, Settings, LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { useRouter } from "next/navigation";
import type { Course } from "@/types";

export function Sidebar({ courses }: { courses: Course[] }) {
  const pathname = usePathname();
  const router = useRouter();
  const supabase = createClient();

  const activeCourses = courses.filter((c) => c.status === "active");

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  return (
    <aside
      className="w-64 h-screen flex flex-col border-r p-4 shrink-0"
      style={{ backgroundColor: "var(--bg-surface)", borderColor: "var(--border)" }}
    >
      <Link href="/dashboard" className="text-lg font-semibold mb-6 block" style={{ color: "var(--text-primary)" }}>
        CourseHub
      </Link>

      <nav className="flex-1 space-y-1">
        <Link
          href="/dashboard"
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
            pathname === "/dashboard" ? "font-medium" : ""
          }`}
          style={{
            backgroundColor: pathname === "/dashboard" ? "var(--bg-primary)" : "transparent",
            color: "var(--text-primary)",
          }}
        >
          <LayoutDashboard size={16} />
          Dashboard
        </Link>

        <Link
          href="/new-course"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors"
          style={{ color: "var(--accent)" }}
        >
          <Plus size={16} />
          New Course
        </Link>

        {activeCourses.length > 0 && (
          <div className="mt-4">
            <p className="px-3 text-xs font-medium uppercase tracking-wider mb-2" style={{ color: "var(--text-secondary)" }}>
              Courses
            </p>
            {activeCourses.map((course) => (
              <Link
                key={course.id}
                href={`/course/${course.id}`}
                className={`block px-3 py-2 rounded-lg text-sm truncate transition-colors ${
                  pathname.startsWith(`/course/${course.id}`) ? "font-medium" : ""
                }`}
                style={{
                  backgroundColor: pathname.startsWith(`/course/${course.id}`) ? "var(--bg-primary)" : "transparent",
                  color: "var(--text-primary)",
                }}
              >
                {course.title}
              </Link>
            ))}
          </div>
        )}
      </nav>

      <div className="space-y-1 border-t pt-4" style={{ borderColor: "var(--border)" }}>
        <Link
          href="/settings"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm"
          style={{ color: "var(--text-secondary)" }}
        >
          <Settings size={16} />
          Settings
        </Link>
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm w-full cursor-pointer"
          style={{ color: "var(--text-secondary)" }}
        >
          <LogOut size={16} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: Create dashboard layout with auth guard**

Create `src/app/dashboard/layout.tsx`:
```tsx
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) redirect("/login");

  const { data: courses } = await supabase
    .from("courses")
    .select("*")
    .order("created_at", { ascending: false });

  return (
    <div className="flex min-h-screen">
      <Sidebar courses={courses ?? []} />
      <main className="flex-1 p-8 overflow-auto">{children}</main>
    </div>
  );
}
```

- [ ] **Step 3: Create dashboard page (empty state + course grid)**

Create `src/app/dashboard/page.tsx`:
```tsx
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import Link from "next/link";
import { Plus, Archive } from "lucide-react";
import { CourseCard } from "@/components/CourseCard";

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: courses } = await supabase
    .from("courses")
    .select("*")
    .order("created_at", { ascending: false });

  const activeCourses = (courses ?? []).filter((c) => c.status === "active");
  const archivedCourses = (courses ?? []).filter((c) => c.status === "archived");

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-semibold">My Courses</h1>
        <Link
          href="/new-course"
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          <Plus size={16} />
          New Course
        </Link>
      </div>

      {activeCourses.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-lg mb-2" style={{ color: "var(--text-secondary)" }}>No courses yet</p>
          <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
            Upload a syllabus to get started
          </p>
          <Link
            href="/new-course"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium"
            style={{ backgroundColor: "var(--accent)", color: "white" }}
          >
            <Plus size={18} />
            Add Your First Course
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {activeCourses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}

      {archivedCourses.length > 0 && (
        <details className="mt-12">
          <summary className="flex items-center gap-2 cursor-pointer text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
            <Archive size={16} />
            Archived ({archivedCourses.length})
          </summary>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4 opacity-60">
            {archivedCourses.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create CourseCard component**

Create `src/components/CourseCard.tsx`:
```tsx
import Link from "next/link";
import { BookOpen } from "lucide-react";
import type { Course } from "@/types";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/course/${course.id}`}
      className="block p-5 rounded-xl shadow-sm transition-shadow hover:shadow-md"
      style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: "var(--bg-primary)" }}>
          <BookOpen size={20} style={{ color: "var(--accent)" }} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium truncate">{course.title}</h3>
          {course.professor && (
            <p className="text-sm mt-1 truncate" style={{ color: "var(--text-secondary)" }}>
              {course.professor}
            </p>
          )}
          {course.semester && (
            <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
              {course.semester}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
}
```

- [ ] **Step 5: Verify dashboard renders**

Run dev server, log in, visit `/dashboard`. Should show empty state with "Add Your First Course" button.

- [ ] **Step 6: Commit**

```bash
git add src/components/Sidebar.tsx src/components/CourseCard.tsx src/app/dashboard/
git commit -m "feat(course-hub): dashboard with sidebar, course grid, archive section"
```

---

### Task 7: Course CRUD API

**Files:**
- Create: `course-hub/src/app/api/courses/route.ts`
- Create: `course-hub/src/app/api/courses/[id]/route.ts`

- [ ] **Step 1: Create courses list + create API**

Create `src/app/api/courses/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { courseCreateSchema } from "@/lib/schemas";
import { NextResponse } from "next/server";

export async function GET() {
  const supabase = await createClient();
  const { data, error } = await supabase
    .from("courses")
    .select("*")
    .order("created_at", { ascending: false });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const parsed = courseCreateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const { data, error } = await supabase
    .from("courses")
    .insert({ ...parsed.data, user_id: user.id })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data, { status: 201 });
}
```

- [ ] **Step 2: Create single course API (get, update, delete)**

Create `src/app/api/courses/[id]/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { courseUpdateSchema } from "@/lib/schemas";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data, error } = await supabase.from("courses").select("*").eq("id", id).single();

  if (error) return NextResponse.json({ error: error.message }, { status: 404 });
  return NextResponse.json(data);
}

export async function PATCH(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const body = await request.json();
  const parsed = courseUpdateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const { data, error } = await supabase
    .from("courses")
    .update(parsed.data)
    .eq("id", id)
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function DELETE(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { error } = await supabase.from("courses").delete().eq("id", id);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ success: true });
}
```

- [ ] **Step 3: Commit**

```bash
git add src/app/api/courses/
git commit -m "feat(course-hub): course CRUD API routes"
```

---

### Task 8: File Upload (Dropzone + Storage)

**Files:**
- Create: `course-hub/src/components/FileDropzone.tsx`
- Create: `course-hub/src/app/api/upload/route.ts`

- [ ] **Step 1: Create upload API route**

Create `src/app/api/upload/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const formData = await request.formData();
  const file = formData.get("file") as File;
  const courseId = formData.get("courseId") as string | null;

  if (!file) return NextResponse.json({ error: "No file provided" }, { status: 400 });

  // Upload to Supabase Storage
  const timestamp = Date.now();
  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
  const path = `${user.id}/${timestamp}_${safeName}`;

  const { error: uploadError } = await supabase.storage
    .from("course-files")
    .upload(path, file);

  if (uploadError) return NextResponse.json({ error: uploadError.message }, { status: 500 });

  const { data: { publicUrl } } = supabase.storage.from("course-files").getPublicUrl(path);

  // Detect file type
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  const fileType = ["pdf"].includes(ext) ? "pdf"
    : ["ppt", "pptx"].includes(ext) ? "ppt"
    : ["png", "jpg", "jpeg", "webp"].includes(ext) ? "image"
    : ["txt", "md", "docx"].includes(ext) ? "text"
    : "other";

  // If courseId provided, create upload record
  if (courseId) {
    const { data: upload, error: dbError } = await supabase
      .from("uploads")
      .insert({
        course_id: courseId,
        file_url: publicUrl,
        file_name: file.name,
        file_type: fileType,
        status: "pending",
      })
      .select()
      .single();

    if (dbError) return NextResponse.json({ error: dbError.message }, { status: 500 });
    return NextResponse.json({ upload, storagePath: path });
  }

  return NextResponse.json({ storagePath: path, fileUrl: publicUrl, fileName: file.name, fileType });
}
```

- [ ] **Step 2: Create FileDropzone component**

Create `src/components/FileDropzone.tsx`:
```tsx
"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, Loader2 } from "lucide-react";

interface FileDropzoneProps {
  onFileUploaded: (result: { storagePath: string; fileUrl: string; fileName: string; fileType: string }) => void;
  courseId?: string;
  accept?: Record<string, string[]>;
}

export function FileDropzone({ onFileUploaded, courseId, accept }: FileDropzoneProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    if (courseId) formData.append("courseId", courseId);

    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      setError(data.error || "Upload failed");
      setUploading(false);
      return;
    }

    setUploading(false);
    onFileUploaded(data);
  }, [courseId, onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 30 * 1024 * 1024, // 30MB
    accept,
  });

  return (
    <div
      {...getRootProps()}
      className="border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors"
      style={{
        borderColor: isDragActive ? "var(--accent)" : "var(--border)",
        backgroundColor: isDragActive ? "rgba(196, 169, 125, 0.05)" : "transparent",
      }}
    >
      <input {...getInputProps()} />
      {uploading ? (
        <div className="flex flex-col items-center gap-2">
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent)" }} />
          <p style={{ color: "var(--text-secondary)" }}>Uploading...</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2">
          {isDragActive ? (
            <File size={32} style={{ color: "var(--accent)" }} />
          ) : (
            <Upload size={32} style={{ color: "var(--text-secondary)" }} />
          )}
          <p style={{ color: "var(--text-secondary)" }}>
            {isDragActive ? "Drop file here" : "Drag & drop any file, or click to browse"}
          </p>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            PDF, PPT, images, text — AI will figure out the rest
          </p>
        </div>
      )}
      {error && <p className="text-sm mt-2" style={{ color: "var(--danger)" }}>{error}</p>}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add src/app/api/upload/ src/components/FileDropzone.tsx
git commit -m "feat(course-hub): file upload with dropzone + Supabase Storage"
```

---

### Task 9: AI Module (Claude API Wrapper)

**Files:**
- Create: `course-hub/src/lib/ai.ts`

- [ ] **Step 1: Create Claude API wrapper with structured output**

Create `src/lib/ai.ts`:
```typescript
import Anthropic from "@anthropic-ai/sdk";
import { parsedSyllabusSchema, parsedQuestionSchema } from "./schemas";
import type { ParsedSyllabus, ParsedQuestion } from "@/types";

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! });

export async function parseSyllabus(fileBase64: string, mimeType: string): Promise<ParsedSyllabus> {
  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-5-20250514",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: { type: "base64", media_type: mimeType as "application/pdf", data: fileBase64 },
          },
          {
            type: "text",
            text: `Analyze this course syllabus and extract its structure. Return a JSON object with:
- title: the course name
- description: a one-sentence course description
- professor: instructor name (null if not found)
- semester: semester info like "Fall 2026" (null if not found)
- nodes: hierarchical array of course content, where each node has:
  - title: section title
  - type: one of "week", "chapter", "topic", "knowledge_point"
  - content: brief description of what this section covers (null if obvious from title)
  - children: nested sub-sections

Organize by the document's natural structure (weeks, chapters, units). Break each section into specific knowledge points where possible. Return ONLY valid JSON, no markdown.`,
          },
        ],
      },
    ],
  });

  const text = response.content.find((b) => b.type === "text")?.text ?? "";
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error("AI did not return valid JSON");

  const parsed = parsedSyllabusSchema.parse(JSON.parse(jsonMatch[0]));
  return parsed as ParsedSyllabus;
}

export async function parseExamQuestions(
  fileBase64: string,
  mimeType: string,
  knowledgePoints: { id: string; title: string }[]
): Promise<(ParsedQuestion & { matched_kp_title: string | null })[]> {
  const kpList = knowledgePoints.map((kp) => kp.title).join(", ");

  const response = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 8192,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: { type: "base64", media_type: mimeType as "application/pdf", data: fileBase64 },
          },
          {
            type: "text",
            text: `Extract all questions from this exam/practice document. For each question, return a JSON array where each item has:
- type: "multiple_choice", "fill_blank", "short_answer", or "true_false"
- stem: the question text
- options: array of {label, text} for multiple choice (null otherwise)
- answer: the correct answer
- explanation: brief explanation of why this answer is correct
- difficulty: 1-5 (1=easy, 5=hard)
- matched_kp_title: which of these knowledge points this question tests: [${kpList}]. Use null if no match.

Return ONLY a JSON array, no markdown.`,
          },
        ],
      },
    ],
  });

  const text = response.content.find((b) => b.type === "text")?.text ?? "";
  const jsonMatch = text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error("AI did not return valid JSON array");

  const questions = JSON.parse(jsonMatch[0]);
  return questions.map((q: unknown) => ({
    ...parsedQuestionSchema.parse(q),
    matched_kp_title: (q as Record<string, unknown>).matched_kp_title ?? null,
  }));
}
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/ai.ts
git commit -m "feat(course-hub): Claude API wrapper for syllabus + exam parsing"
```

---

### Task 10: Parse API Route

**Files:**
- Create: `course-hub/src/app/api/parse/route.ts`

- [ ] **Step 1: Create parse API route**

Create `src/app/api/parse/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { parseSyllabus, parseExamQuestions } from "@/lib/ai";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { storagePath, parseType, courseId } = await request.json();
  if (!storagePath) return NextResponse.json({ error: "storagePath required" }, { status: 400 });

  // Download file from Supabase Storage
  const { data: fileData, error: downloadError } = await supabase.storage
    .from("course-files")
    .download(storagePath);

  if (downloadError || !fileData) {
    return NextResponse.json({ error: "Failed to download file" }, { status: 500 });
  }

  const buffer = Buffer.from(await fileData.arrayBuffer());
  const base64 = buffer.toString("base64");
  const ext = storagePath.split(".").pop()?.toLowerCase() ?? "";
  const mimeType = ext === "pdf" ? "application/pdf"
    : ["png"].includes(ext) ? "image/png"
    : ["jpg", "jpeg"].includes(ext) ? "image/jpeg"
    : "application/pdf"; // fallback

  if (parseType === "syllabus" || !parseType) {
    const result = await parseSyllabus(base64, mimeType);
    return NextResponse.json({ type: "syllabus", data: result });
  }

  if (parseType === "exam") {
    let knowledgePoints: { id: string; title: string }[] = [];

    if (courseId) {
      const { data: nodes } = await supabase
        .from("outline_nodes")
        .select("id, title")
        .eq("course_id", courseId)
        .eq("type", "knowledge_point");
      knowledgePoints = nodes ?? [];
    }

    const questions = await parseExamQuestions(base64, mimeType, knowledgePoints);
    return NextResponse.json({ type: "exam", data: questions });
  }

  return NextResponse.json({ error: "Invalid parseType" }, { status: 400 });
}
```

- [ ] **Step 2: Commit**

```bash
git add src/app/api/parse/
git commit -m "feat(course-hub): AI parse API route for syllabus + exam"
```

---

### Task 11: New Course Flow (Upload → Parse → Preview → Create)

**Files:**
- Create: `course-hub/src/app/new-course/page.tsx`
- Create: `course-hub/src/components/OutlinePreview.tsx`

- [ ] **Step 1: Create OutlinePreview component**

Create `src/components/OutlinePreview.tsx`:
```tsx
"use client";

import { ChevronRight, ChevronDown } from "lucide-react";
import { useState } from "react";
import type { ParsedOutlineNode } from "@/types";

function TreeNode({ node, depth = 0 }: { node: ParsedOutlineNode; depth?: number }) {
  const [expanded, setExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  const typeColors: Record<string, string> = {
    week: "var(--accent)",
    chapter: "var(--accent)",
    topic: "var(--text-primary)",
    knowledge_point: "var(--text-secondary)",
  };

  return (
    <div style={{ marginLeft: depth * 20 }}>
      <div
        className="flex items-center gap-1 py-1 cursor-pointer select-none"
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren ? (
          expanded ? <ChevronDown size={14} style={{ color: "var(--text-secondary)" }} />
            : <ChevronRight size={14} style={{ color: "var(--text-secondary)" }} />
        ) : (
          <span className="w-3.5" />
        )}
        <span
          className="text-sm"
          style={{ color: typeColors[node.type] || "var(--text-primary)", fontWeight: depth < 2 ? 500 : 400 }}
        >
          {node.title}
        </span>
      </div>
      {expanded && hasChildren && node.children.map((child, i) => (
        <TreeNode key={i} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export function OutlinePreview({ nodes }: { nodes: ParsedOutlineNode[] }) {
  return (
    <div className="p-4 rounded-xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
      {nodes.map((node, i) => (
        <TreeNode key={i} node={node} />
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create new-course page**

Create `src/app/new-course/page.tsx`:
```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileDropzone } from "@/components/FileDropzone";
import { OutlinePreview } from "@/components/OutlinePreview";
import { Loader2, Check, ArrowLeft } from "lucide-react";
import Link from "next/link";
import type { ParsedSyllabus } from "@/types";

type Step = "upload" | "parsing" | "preview";

export default function NewCoursePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("upload");
  const [storagePath, setStoragePath] = useState<string | null>(null);
  const [parsed, setParsed] = useState<ParsedSyllabus | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileUploaded(result: { storagePath: string }) {
    setStoragePath(result.storagePath);
    setStep("parsing");
    setError(null);

    const res = await fetch("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ storagePath: result.storagePath, parseType: "syllabus" }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || "Failed to parse file");
      setStep("upload");
      return;
    }

    setParsed(data.data);
    setStep("preview");
  }

  async function handleCreate() {
    if (!parsed || !storagePath) return;
    setCreating(true);

    // Create course
    const courseRes = await fetch("/api/courses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: parsed.title,
        description: parsed.description,
        professor: parsed.professor,
        semester: parsed.semester,
      }),
    });

    const course = await courseRes.json();
    if (!courseRes.ok) {
      setError(course.error || "Failed to create course");
      setCreating(false);
      return;
    }

    // Save outline nodes
    const res = await fetch(`/api/courses/${course.id}/outline`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nodes: parsed.nodes }),
    });

    if (!res.ok) {
      setError("Course created but failed to save outline");
      setCreating(false);
      return;
    }

    // Save upload record
    await fetch("/api/upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: course.id, storagePath }),
    });

    router.push(`/course/${course.id}`);
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Link href="/dashboard" className="flex items-center gap-1 text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <h1 className="text-2xl font-semibold mb-2">New Course</h1>
      <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
        Upload your syllabus and AI will create the course structure for you.
      </p>

      {step === "upload" && (
        <FileDropzone onFileUploaded={handleFileUploaded} />
      )}

      {step === "parsing" && (
        <div className="flex flex-col items-center py-16 gap-3">
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent)" }} />
          <p style={{ color: "var(--text-secondary)" }}>AI is reading your syllabus...</p>
        </div>
      )}

      {step === "preview" && parsed && (
        <div>
          <div className="mb-6 p-4 rounded-xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
            <h2 className="text-lg font-medium">{parsed.title}</h2>
            <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{parsed.description}</p>
            {parsed.professor && <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>Instructor: {parsed.professor}</p>}
            {parsed.semester && <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{parsed.semester}</p>}
          </div>

          <h3 className="font-medium mb-3">Course Outline</h3>
          <OutlinePreview nodes={parsed.nodes} />

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => { setStep("upload"); setParsed(null); }}
              className="px-4 py-2 rounded-lg text-sm border cursor-pointer"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Upload Different File
            </button>
            <button
              onClick={handleCreate}
              disabled={creating}
              className="flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-50"
              style={{ backgroundColor: "var(--accent)", color: "white" }}
            >
              {creating ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
              Create Course
            </button>
          </div>
        </div>
      )}

      {error && <p className="text-sm mt-4" style={{ color: "var(--danger)" }}>{error}</p>}
    </div>
  );
}
```

- [ ] **Step 3: Create outline bulk save API**

Create `src/app/api/courses/[id]/outline/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import type { ParsedOutlineNode } from "@/types";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .order("order");

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

// Flatten tree → flat rows for DB insert
function flattenNodes(
  nodes: ParsedOutlineNode[],
  courseId: string,
  parentId: string | null = null
): { id: string; course_id: string; parent_id: string | null; title: string; type: string; content: string | null; order: number }[] {
  const rows: ReturnType<typeof flattenNodes> = [];
  nodes.forEach((node, index) => {
    const id = randomUUID();
    rows.push({
      id,
      course_id: courseId,
      parent_id: parentId,
      title: node.title,
      type: node.type,
      content: node.content ?? null,
      order: index,
    });
    if (node.children?.length) {
      rows.push(...flattenNodes(node.children, courseId, id));
    }
  });
  return rows;
}

export async function PUT(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { nodes } = await request.json();

  // Delete existing outline
  await supabase.from("outline_nodes").delete().eq("course_id", id);

  // Insert new outline
  const rows = flattenNodes(nodes, id);
  if (rows.length > 0) {
    const { error } = await supabase.from("outline_nodes").insert(rows);
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ count: rows.length });
}
```

- [ ] **Step 4: Verify end-to-end flow**

Run dev server. Log in → click "New Course" → upload a PDF syllabus → wait for AI parsing → preview outline → click "Create Course" → should redirect to course detail page.

- [ ] **Step 5: Commit**

```bash
git add src/app/new-course/ src/components/OutlinePreview.tsx src/app/api/courses/\[id\]/outline/
git commit -m "feat(course-hub): new course flow — upload syllabus → AI parse → preview → create"
```

---

### Task 12: Course Detail Page with Tabs + Outline Tree

**Files:**
- Create: `course-hub/src/components/CourseTabs.tsx`
- Create: `course-hub/src/components/OutlineTree.tsx`
- Create: `course-hub/src/app/course/[id]/page.tsx`

- [ ] **Step 1: Create CourseTabs component**

Create `src/components/CourseTabs.tsx`:
```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { List, BookOpen, BarChart3 } from "lucide-react";

export function CourseTabs({ courseId }: { courseId: string }) {
  const pathname = usePathname();
  const base = `/course/${courseId}`;

  const tabs = [
    { href: base, label: "Outline", icon: List, exact: true },
    { href: `${base}/practice`, label: "Practice", icon: BookOpen },
    { href: `${base}/progress`, label: "Progress", icon: BarChart3 },
  ];

  return (
    <div className="flex gap-1 border-b mb-6" style={{ borderColor: "var(--border)" }}>
      {tabs.map((tab) => {
        const isActive = tab.exact ? pathname === tab.href : pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className="flex items-center gap-1.5 px-4 py-2.5 text-sm transition-colors -mb-px"
            style={{
              color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
              borderBottom: isActive ? "2px solid var(--accent)" : "2px solid transparent",
              fontWeight: isActive ? 500 : 400,
            }}
          >
            <tab.icon size={16} />
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Create OutlineTree component with react-arborist**

Create `src/components/OutlineTree.tsx`:
```tsx
"use client";

import { Tree, type NodeRendererProps } from "react-arborist";
import { ChevronRight, ChevronDown, GripVertical } from "lucide-react";
import type { OutlineNode } from "@/types";

interface TreeNode {
  id: string;
  name: string;
  type: string;
  content: string | null;
  children?: TreeNode[];
}

// Convert flat DB rows → nested tree for react-arborist
export function buildTree(nodes: OutlineNode[]): TreeNode[] {
  const map = new Map<string, TreeNode>();
  const roots: TreeNode[] = [];

  for (const node of nodes) {
    map.set(node.id, { id: node.id, name: node.title, type: node.type, content: node.content, children: [] });
  }

  for (const node of nodes) {
    const treeNode = map.get(node.id)!;
    if (node.parent_id && map.has(node.parent_id)) {
      map.get(node.parent_id)!.children!.push(treeNode);
    } else {
      roots.push(treeNode);
    }
  }

  return roots;
}

function Node({ node, style, dragHandle }: NodeRendererProps<TreeNode>) {
  const typeLabel: Record<string, string> = {
    week: "W",
    chapter: "Ch",
    topic: "T",
    knowledge_point: "KP",
  };

  return (
    <div
      style={style}
      ref={dragHandle}
      className="flex items-center gap-1 py-1 px-2 rounded group cursor-pointer"
      onClick={() => node.toggle()}
    >
      <GripVertical size={12} className="opacity-0 group-hover:opacity-40 shrink-0" style={{ color: "var(--text-secondary)" }} />

      {node.isInternal ? (
        node.isOpen
          ? <ChevronDown size={14} style={{ color: "var(--text-secondary)" }} />
          : <ChevronRight size={14} style={{ color: "var(--text-secondary)" }} />
      ) : (
        <span className="w-3.5 shrink-0" />
      )}

      <span
        className="text-xs px-1.5 py-0.5 rounded shrink-0"
        style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-secondary)" }}
      >
        {typeLabel[node.data.type] || "?"}
      </span>

      <span
        className="text-sm truncate"
        style={{ fontWeight: node.level < 2 ? 500 : 400 }}
      >
        {node.data.name}
      </span>
    </div>
  );
}

export function OutlineTree({ nodes }: { nodes: OutlineNode[] }) {
  const treeData = buildTree(nodes);

  if (treeData.length === 0) {
    return (
      <p className="text-sm py-8 text-center" style={{ color: "var(--text-secondary)" }}>
        No outline yet. Upload a syllabus to generate one.
      </p>
    );
  }

  return (
    <Tree
      data={treeData}
      width="100%"
      height={600}
      indent={24}
      rowHeight={34}
      openByDefault={true}
    >
      {Node}
    </Tree>
  );
}
```

- [ ] **Step 3: Create course detail page**

Create `src/app/course/[id]/page.tsx`:
```tsx
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { OutlineTree } from "@/components/OutlineTree";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";

export default async function CourseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("*").eq("id", id).single();
  if (!course) redirect("/dashboard");

  const { data: outlineNodes } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .order("order");

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold">{course.title}</h1>
          {course.professor && (
            <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{course.professor}</p>
          )}
          {course.semester && (
            <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>{course.semester}</p>
          )}
        </div>
        <div className="flex gap-2">
          <form action={`/api/courses/${id}`} method="POST">
            <button
              type="submit"
              className="p-2 rounded-lg transition-colors cursor-pointer"
              style={{ color: "var(--text-secondary)" }}
              title={course.status === "active" ? "Archive" : "Restore"}
            >
              {course.status === "active" ? <Archive size={18} /> : <ArchiveRestore size={18} />}
            </button>
          </form>
        </div>
      </div>

      <CourseTabs courseId={id} />
      <OutlineTree nodes={outlineNodes ?? []} />
    </div>
  );
}
```

- [ ] **Step 4: Verify course detail page**

Navigate to a created course. Should show course header, tabs, and outline tree with drag handles and expand/collapse.

- [ ] **Step 5: Commit**

```bash
git add src/components/CourseTabs.tsx src/components/OutlineTree.tsx src/app/course/
git commit -m "feat(course-hub): course detail page with tabs + react-arborist outline tree"
```

---

### Task 13: Questions API + Exam Upload

**Files:**
- Create: `course-hub/src/app/api/questions/route.ts`
- Create: `course-hub/src/app/api/attempts/route.ts`

- [ ] **Step 1: Create questions API**

Create `src/app/api/questions/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { parseExamQuestions } from "@/lib/ai";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const courseId = searchParams.get("courseId");
  if (!courseId) return NextResponse.json({ error: "courseId required" }, { status: 400 });

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("questions")
    .select("*")
    .eq("course_id", courseId)
    .order("created_at", { ascending: false });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { courseId, storagePath } = await request.json();
  if (!courseId || !storagePath) {
    return NextResponse.json({ error: "courseId and storagePath required" }, { status: 400 });
  }

  // Download file
  const { data: fileData } = await supabase.storage.from("course-files").download(storagePath);
  if (!fileData) return NextResponse.json({ error: "File not found" }, { status: 404 });

  const buffer = Buffer.from(await fileData.arrayBuffer());
  const base64 = buffer.toString("base64");
  const ext = storagePath.split(".").pop()?.toLowerCase() ?? "";
  const mimeType = ext === "pdf" ? "application/pdf" : `image/${ext}`;

  // Get knowledge points for matching
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", courseId)
    .eq("type", "knowledge_point");

  const parsed = await parseExamQuestions(base64, mimeType, kps ?? []);

  // Match KP titles to IDs
  const kpMap = new Map((kps ?? []).map((kp) => [kp.title.toLowerCase(), kp.id]));

  const rows = parsed.map((q) => ({
    course_id: courseId,
    type: q.type,
    stem: q.stem,
    options: q.options,
    answer: q.answer,
    explanation: q.explanation,
    difficulty: q.difficulty,
    knowledge_point_id: q.matched_kp_title ? kpMap.get(q.matched_kp_title.toLowerCase()) ?? null : null,
  }));

  const { data: inserted, error } = await supabase.from("questions").insert(rows).select();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json(inserted, { status: 201 });
}
```

- [ ] **Step 2: Create attempts API**

Create `src/app/api/attempts/route.ts`:
```typescript
import { createClient } from "@/lib/supabase/server";
import { attemptCreateSchema } from "@/lib/schemas";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const parsed = attemptCreateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  // Get correct answer
  const { data: question } = await supabase
    .from("questions")
    .select("answer")
    .eq("id", parsed.data.question_id)
    .single();

  if (!question) return NextResponse.json({ error: "Question not found" }, { status: 404 });

  const isCorrect = parsed.data.user_answer.trim().toLowerCase() === question.answer.trim().toLowerCase();

  const { data, error } = await supabase
    .from("attempts")
    .insert({
      user_id: user.id,
      question_id: parsed.data.question_id,
      user_answer: parsed.data.user_answer,
      is_correct: isCorrect,
    })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data, { status: 201 });
}
```

- [ ] **Step 3: Commit**

```bash
git add src/app/api/questions/ src/app/api/attempts/
git commit -m "feat(course-hub): questions + attempts API routes"
```

---

### Task 14: Practice Mode

**Files:**
- Create: `course-hub/src/components/QuestionCard.tsx`
- Create: `course-hub/src/app/course/[id]/practice/page.tsx`

- [ ] **Step 1: Create QuestionCard component**

Create `src/components/QuestionCard.tsx`:
```tsx
"use client";

import { useState } from "react";
import { Check, X } from "lucide-react";
import type { Question } from "@/types";

interface QuestionCardProps {
  question: Question;
  onAnswer: (questionId: string, answer: string, isCorrect: boolean) => void;
}

export function QuestionCard({ question, onAnswer }: QuestionCardProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [textAnswer, setTextAnswer] = useState("");

  const isCorrect = submitted && (selected || textAnswer).trim().toLowerCase() === question.answer.trim().toLowerCase();

  async function handleSubmit() {
    const answer = question.type === "multiple_choice" || question.type === "true_false"
      ? selected ?? ""
      : textAnswer;

    if (!answer) return;

    const correct = answer.trim().toLowerCase() === question.answer.trim().toLowerCase();
    setSubmitted(true);

    await fetch("/api/attempts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: question.id, user_answer: answer }),
    });

    onAnswer(question.id, answer, correct);
  }

  return (
    <div className="p-6 rounded-xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
      <p className="text-sm font-medium mb-4">{question.stem}</p>

      {(question.type === "multiple_choice" || question.type === "true_false") && question.options && (
        <div className="space-y-2 mb-4">
          {question.options.map((opt) => (
            <button
              key={opt.label}
              onClick={() => !submitted && setSelected(opt.label)}
              disabled={submitted}
              className="w-full text-left px-4 py-3 rounded-lg text-sm transition-colors cursor-pointer disabled:cursor-default"
              style={{
                border: "1px solid",
                borderColor: submitted
                  ? opt.label.toLowerCase() === question.answer.trim().toLowerCase()
                    ? "var(--success)"
                    : selected === opt.label
                      ? "var(--danger)"
                      : "var(--border)"
                  : selected === opt.label
                    ? "var(--accent)"
                    : "var(--border)",
                backgroundColor: submitted
                  ? opt.label.toLowerCase() === question.answer.trim().toLowerCase()
                    ? "rgba(74, 124, 89, 0.1)"
                    : "transparent"
                  : selected === opt.label
                    ? "rgba(196, 169, 125, 0.1)"
                    : "transparent",
              }}
            >
              <span className="font-medium mr-2">{opt.label}.</span>
              {opt.text}
            </button>
          ))}
        </div>
      )}

      {(question.type === "fill_blank" || question.type === "short_answer") && (
        <textarea
          value={textAnswer}
          onChange={(e) => !submitted && setTextAnswer(e.target.value)}
          disabled={submitted}
          placeholder="Type your answer..."
          className="w-full px-4 py-3 rounded-lg text-sm mb-4 resize-none"
          style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-primary)" }}
          rows={question.type === "short_answer" ? 4 : 1}
        />
      )}

      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={!selected && !textAnswer}
          className="px-6 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-40"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          Submit
        </button>
      ) : (
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-2">
            {isCorrect ? (
              <><Check size={16} style={{ color: "var(--success)" }} /><span className="text-sm font-medium" style={{ color: "var(--success)" }}>Correct</span></>
            ) : (
              <><X size={16} style={{ color: "var(--danger)" }} /><span className="text-sm font-medium" style={{ color: "var(--danger)" }}>Incorrect — answer: {question.answer}</span></>
            )}
          </div>
          {question.explanation && (
            <p className="text-sm p-3 rounded-lg" style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-secondary)" }}>
              {question.explanation}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Create practice page**

Create `src/app/course/[id]/practice/page.tsx`:
```tsx
"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { FileDropzone } from "@/components/FileDropzone";
import { ChevronLeft, ChevronRight, Loader2, Upload } from "lucide-react";
import type { Question } from "@/types";

export default function PracticePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetch(`/api/questions?courseId=${id}`)
      .then((r) => r.json())
      .then((data) => { setQuestions(data); setLoading(false); });
  }, [id]);

  async function handleExamUpload(result: { storagePath: string }) {
    setGenerating(true);
    const res = await fetch("/api/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: id, storagePath: result.storagePath }),
    });
    const newQuestions = await res.json();
    if (res.ok) {
      setQuestions((prev) => [...newQuestions, ...prev]);
      setCurrentIndex(0);
    }
    setGenerating(false);
    setShowUpload(false);
  }

  function handleAnswer() {
    // Auto-advance after 2 seconds
    setTimeout(() => {
      if (currentIndex < questions.length - 1) setCurrentIndex((i) => i + 1);
    }, 2000);
  }

  if (loading) return <div><CourseTabs courseId={id} /><Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--accent)" }} /></div>;

  return (
    <div>
      <CourseTabs courseId={id} />

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium">Practice</h2>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm cursor-pointer"
          style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        >
          <Upload size={14} />
          Upload Exam
        </button>
      </div>

      {showUpload && (
        <div className="mb-6">
          {generating ? (
            <div className="flex items-center gap-2 py-8 justify-center">
              <Loader2 size={20} className="animate-spin" style={{ color: "var(--accent)" }} />
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>AI is converting questions...</p>
            </div>
          ) : (
            <FileDropzone onFileUploaded={handleExamUpload} courseId={id} />
          )}
        </div>
      )}

      {questions.length === 0 ? (
        <div className="text-center py-16">
          <p className="mb-2" style={{ color: "var(--text-secondary)" }}>No practice questions yet</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Upload a past exam or practice sheet to generate interactive questions</p>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              Question {currentIndex + 1} of {questions.length}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
                disabled={currentIndex === 0}
                className="p-1.5 rounded-lg cursor-pointer disabled:opacity-30"
                style={{ border: "1px solid var(--border)" }}
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
                disabled={currentIndex === questions.length - 1}
                className="p-1.5 rounded-lg cursor-pointer disabled:opacity-30"
                style={{ border: "1px solid var(--border)" }}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
          <QuestionCard
            key={questions[currentIndex].id}
            question={questions[currentIndex]}
            onAnswer={handleAnswer}
          />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add src/components/QuestionCard.tsx src/app/course/\[id\]/practice/
git commit -m "feat(course-hub): practice mode with interactive question cards"
```

---

### Task 15: Progress Tracking + Mastery Heatmap

**Files:**
- Create: `course-hub/src/lib/mastery.ts`
- Create: `course-hub/src/components/ProgressGrid.tsx`
- Create: `course-hub/src/app/course/[id]/progress/page.tsx`

- [ ] **Step 1: Create mastery calculation logic**

Create `src/lib/mastery.ts`:
```typescript
import type { MasteryLevel } from "@/types";

interface AttemptRecord {
  is_correct: boolean;
  answered_at: string;
}

export function calculateMastery(attempts: AttemptRecord[]): { level: MasteryLevel; rate: number; total: number } {
  if (attempts.length === 0) return { level: "untested", rate: 0, total: 0 };

  // Take last 10 attempts, sorted by most recent
  const recent = [...attempts]
    .sort((a, b) => new Date(b.answered_at).getTime() - new Date(a.answered_at).getTime())
    .slice(0, 10);

  const correct = recent.filter((a) => a.is_correct).length;
  const rate = correct / recent.length;

  const level: MasteryLevel = rate > 0.8 ? "mastered" : rate >= 0.4 ? "reviewing" : "weak";

  return { level, rate, total: attempts.length };
}

export const masteryColors: Record<MasteryLevel, string> = {
  mastered: "var(--success)",
  reviewing: "var(--warning)",
  weak: "var(--danger)",
  untested: "var(--border)",
};

export const masteryLabels: Record<MasteryLevel, string> = {
  mastered: "Mastered",
  reviewing: "Needs Review",
  weak: "Weak",
  untested: "Untested",
};
```

- [ ] **Step 2: Create ProgressGrid component**

Create `src/components/ProgressGrid.tsx`:
```tsx
"use client";

import { calculateMastery, masteryColors, masteryLabels } from "@/lib/mastery";
import type { OutlineNode, MasteryLevel } from "@/types";

interface KPMastery {
  node: OutlineNode;
  level: MasteryLevel;
  rate: number;
  total: number;
}

export function ProgressGrid({ data }: { data: KPMastery[] }) {
  if (data.length === 0) {
    return (
      <p className="text-sm py-8 text-center" style={{ color: "var(--text-secondary)" }}>
        No knowledge points to track yet.
      </p>
    );
  }

  const grouped = {
    mastered: data.filter((d) => d.level === "mastered"),
    reviewing: data.filter((d) => d.level === "reviewing"),
    weak: data.filter((d) => d.level === "weak"),
    untested: data.filter((d) => d.level === "untested"),
  };

  return (
    <div>
      {/* Legend */}
      <div className="flex gap-4 mb-6">
        {(["mastered", "reviewing", "weak", "untested"] as MasteryLevel[]).map((level) => (
          <div key={level} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: masteryColors[level] }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
              {masteryLabels[level]} ({grouped[level].length})
            </span>
          </div>
        ))}
      </div>

      {/* Heatmap grid */}
      <div className="flex flex-wrap gap-1.5">
        {data.map((item) => (
          <div
            key={item.node.id}
            className="relative group"
          >
            <div
              className="w-10 h-10 rounded-lg transition-transform hover:scale-110"
              style={{ backgroundColor: masteryColors[item.level] }}
            />
            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10"
              style={{ backgroundColor: "var(--text-primary)", color: "var(--bg-surface)" }}
            >
              {item.node.title}
              {item.total > 0 && ` — ${Math.round(item.rate * 100)}% (${item.total} attempts)`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export { calculateMastery };
```

- [ ] **Step 3: Create progress page**

Create `src/app/course/[id]/progress/page.tsx`:
```tsx
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";
import { CourseTabs } from "@/components/CourseTabs";
import { ProgressGrid } from "@/components/ProgressGrid";
import { calculateMastery } from "@/lib/mastery";
import type { MasteryLevel } from "@/types";

export default async function ProgressPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // Get knowledge points
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .eq("type", "knowledge_point")
    .order("order");

  // Get questions with their KP mapping
  const { data: questions } = await supabase
    .from("questions")
    .select("id, knowledge_point_id")
    .eq("course_id", id);

  // Get all attempts for this user
  const questionIds = (questions ?? []).map((q) => q.id);
  const { data: attempts } = questionIds.length > 0
    ? await supabase
        .from("attempts")
        .select("question_id, is_correct, answered_at")
        .eq("user_id", user.id)
        .in("question_id", questionIds)
    : { data: [] };

  // Build KP → attempts mapping
  const kpQuestions = new Map<string, string[]>();
  for (const q of questions ?? []) {
    if (q.knowledge_point_id) {
      const list = kpQuestions.get(q.knowledge_point_id) ?? [];
      list.push(q.id);
      kpQuestions.set(q.knowledge_point_id, list);
    }
  }

  const data = (kps ?? []).map((kp) => {
    const qIds = kpQuestions.get(kp.id) ?? [];
    const kpAttempts = (attempts ?? []).filter((a) => qIds.includes(a.question_id));
    const mastery = calculateMastery(kpAttempts);
    return { node: kp, ...mastery };
  });

  return (
    <div>
      <CourseTabs courseId={id} />
      <h2 className="text-lg font-medium mb-4">Knowledge Point Mastery</h2>
      <ProgressGrid data={data} />
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add src/lib/mastery.ts src/components/ProgressGrid.tsx src/app/course/\[id\]/progress/
git commit -m "feat(course-hub): progress tracking with mastery heatmap"
```

---

### Task 16: Archive/Restore + Final Polish

**Files:**
- Modify: `course-hub/src/app/course/[id]/page.tsx`
- Create: `course-hub/src/app/course/[id]/layout.tsx`

- [ ] **Step 1: Add course detail layout (shared for all tabs)**

Create `src/app/course/[id]/layout.tsx`:
```tsx
import { createClient } from "@/lib/supabase/server";
import { redirect } from "next/navigation";

export default async function CourseLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const { data: course } = await supabase.from("courses").select("id").eq("id", id).single();
  if (!course) redirect("/dashboard");

  return <>{children}</>;
}
```

- [ ] **Step 2: Add archive/restore client action to course detail page**

Update `src/app/course/[id]/page.tsx` — replace the archive button section with a client component:

Add at the top of the file, a new client component `ArchiveButton`:
```tsx
"use client";

import { useRouter } from "next/navigation";
import { Archive, ArchiveRestore, Trash2 } from "lucide-react";

function ArchiveButton({ courseId, status }: { courseId: string; status: string }) {
  const router = useRouter();

  async function toggleArchive() {
    const newStatus = status === "active" ? "archived" : "active";
    await fetch(`/api/courses/${courseId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    });
    router.refresh();
  }

  async function deleteCourse() {
    if (!confirm("Delete this course and all its data?")) return;
    await fetch(`/api/courses/${courseId}`, { method: "DELETE" });
    router.push("/dashboard");
  }

  return (
    <div className="flex gap-1">
      <button onClick={toggleArchive} className="p-2 rounded-lg cursor-pointer" style={{ color: "var(--text-secondary)" }}
        title={status === "active" ? "Archive" : "Restore"}>
        {status === "active" ? <Archive size={18} /> : <ArchiveRestore size={18} />}
      </button>
      <button onClick={deleteCourse} className="p-2 rounded-lg cursor-pointer" style={{ color: "var(--danger)" }} title="Delete">
        <Trash2 size={18} />
      </button>
    </div>
  );
}
```

Then use `<ArchiveButton courseId={id} status={course.status} />` in the JSX where the archive button was.

- [ ] **Step 3: Verify complete flow**

Test end-to-end:
1. Log in with Google
2. Create a new course by uploading a syllabus PDF
3. View the generated outline tree
4. Navigate to Practice tab → upload an exam → answer questions
5. Navigate to Progress tab → see mastery heatmap
6. Archive the course from course detail page
7. Dashboard shows it in archived section
8. Restore it back

- [ ] **Step 4: Commit**

```bash
git add src/app/course/
git commit -m "feat(course-hub): archive/restore, course layout, final polish"
```

---

### Task 17: CLAUDE.md + STATUS.md + Final Commit

**Files:**
- Create: `course-hub/CLAUDE.md`
- Create: `course-hub/STATUS.md`

- [ ] **Step 1: Create CLAUDE.md**

Create `course-hub/CLAUDE.md`:
```markdown
# CourseHub — AI Course Management Tool

## Architecture
- **Framework:** Next.js 16 (App Router)
- **Database:** Supabase (PostgreSQL + RLS)
- **Auth:** Supabase Auth (Google OAuth)
- **AI:** Claude API (Sonnet for syllabus, Haiku for quizzes)
- **State:** Zustand (client), Server Components (server)
- **Styling:** Tailwind CSS v4, Lucide icons, warm color palette

## Key Files
- `src/lib/ai.ts` — Claude API wrapper (parseSyllabus, parseExamQuestions)
- `src/lib/schemas.ts` — Zod schemas for all entities
- `src/lib/mastery.ts` — Mastery calculation (last 10 attempts, 3-tier)
- `supabase/migrations/001_initial_schema.sql` — All tables + RLS

## Data Model
- Course → OutlineNodes (adjacency list tree)
- Course → Uploads → Questions (AI-generated)
- User → Attempts → mastery aggregation per knowledge point

## Conventions
- All API routes validate with Zod before DB operations
- RLS on every table — user_id ownership, child tables via FK joins
- No emoji in UI — Lucide icons only
- Warm palette: off-white #f8f6f1, accent gold #c4a97d
```

- [ ] **Step 2: Create STATUS.md**

Create `course-hub/STATUS.md`:
```markdown
# CourseHub Status

## [YYYY-MM-DD] MVP Complete
- Google OAuth login
- Multi-course dashboard with archive/restore
- Upload syllabus → AI generates course outline
- Outline tree view (react-arborist)
- Upload exams → AI generates interactive questions
- Practice mode (MC, fill-blank, short-answer)
- Knowledge point mastery heatmap
- 5 tables with RLS, Supabase Storage for files
```

- [ ] **Step 3: Commit and push**

```bash
git add course-hub/
git commit -m "feat(course-hub): MVP complete — CLAUDE.md + STATUS.md"
git push
```

---

## Summary

| Task | What it builds | Est. Steps |
|------|---------------|------------|
| 1 | Project scaffold + deps | 8 |
| 2 | Types + Zod schemas | 3 |
| 3 | Database migration + RLS | 5 |
| 4 | Supabase client helpers + middleware | 5 |
| 5 | Login page + OAuth callback | 4 |
| 6 | Sidebar + Dashboard layout + CourseCard | 6 |
| 7 | Course CRUD API | 3 |
| 8 | File upload (dropzone + storage) | 3 |
| 9 | Claude API wrapper (syllabus + exam) | 2 |
| 10 | Parse API route | 2 |
| 11 | New course flow (upload → parse → preview → create) | 5 |
| 12 | Course detail + tabs + outline tree | 5 |
| 13 | Questions + attempts API | 3 |
| 14 | Practice mode UI | 3 |
| 15 | Progress tracking + mastery heatmap | 4 |
| 16 | Archive/restore + polish | 4 |
| 17 | CLAUDE.md + STATUS.md | 3 |
| **Total** | | **68 steps** |
