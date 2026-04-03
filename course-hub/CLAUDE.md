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
