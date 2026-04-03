# CourseHub — AI Course Management Tool

## Architecture
- **Framework:** Next.js 16 (App Router)
- **Database:** Supabase (PostgreSQL + RLS)
- **Auth:** Supabase Auth (Google OAuth)
- **AI:** Qwen3.5-Plus via DashScope (OpenAI-compatible, $0.26/$1.56 per M tokens)
- **State:** Zustand (client), Server Components (server)
- **Styling:** Tailwind CSS v4, Lucide icons, warm color palette

## Key Files
- `src/lib/ai.ts` — Qwen AI wrapper (parseSyllabus, parseExamQuestions, generateStudyTasks, generateQuestionsFromOutline)
- `src/lib/schemas.ts` — Zod schemas for all entities
- `src/lib/mastery.ts` — Mastery calculation (last 10 attempts, 3-tier)
- `supabase/migrations/001_initial_schema.sql` — All tables + RLS
- `supabase/migrations/002_study_tasks.sql` — study_tasks table + RLS
- `src/app/api/courses/[id]/generate/route.ts` — Auto-pipeline: outline → study tasks + quiz questions

## Data Model
- Course → OutlineNodes (adjacency list tree)
- Course → Uploads → Questions (AI-generated from exam/practice files)
- Course → StudyTasks (auto-generated from outline via Pipeline 3)
- Course → Questions (also auto-generated from outline via Pipeline 4, no exam needed)
- User → Attempts → mastery aggregation per knowledge point

## Auto-Pipeline
On course creation, after outline is saved, `POST /api/courses/[id]/generate` fires (non-blocking):
1. Filters outline nodes of type `knowledge_point`
2. Runs `generateStudyTasks` + `generateQuestionsFromOutline` in parallel
3. Inserts results into `study_tasks` and `questions` tables

## Conventions
- All API routes validate with Zod before DB operations
- RLS on every table — user_id ownership, child tables via FK joins
- No emoji in UI — Lucide icons only
- Warm palette: off-white #f8f6f1, accent gold #c4a97d
