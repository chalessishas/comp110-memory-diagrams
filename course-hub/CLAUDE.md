# CourseHub — AI Course Management Tool

## Architecture
- **Framework:** Next.js 16 (App Router)
- **Database:** Supabase (PostgreSQL + RLS, project: `zubvbcexqaiauyptsyby`)
- **Auth:** Supabase Auth (Email/Password + Google OAuth)
- **AI:** Qwen3.5-Plus via DashScope (OpenAI-compatible, `@ai-sdk/openai` + `createOpenAI`)
- **State:** Server Components (primary), client hooks for interactive panels
- **Styling:** Tailwind CSS v4 + globals.css custom properties, minimal black/gray palette, frosted glass cards
- **Icons:** Lucide React (no emoji)

## Key Files
- `src/lib/ai.ts` — Qwen AI wrapper: parseSyllabus, parseExamQuestions, generateStudyTasks, generateQuestionsFromOutline
- `src/lib/schemas.ts` — Zod schemas for all entities + AI structured output
- `src/lib/mastery.ts` — Mastery calculation (last 10 attempts, 3-tier: mastered/reviewing/weak)
- `src/lib/course-notes.ts` — CourseNote data layer (row ↔ domain model conversion)
- `src/lib/study-tracker.ts` — localStorage-based study timer (by mode: solving/reviewing/studying/idle)
- `supabase/migrations/001_initial_schema.sql` — courses, outline_nodes, uploads, questions, attempts + RLS
- `supabase/migrations/002_study_tasks.sql` — study_tasks table + RLS

## Data Model
- Course → OutlineNodes (adjacency list tree, parent_id self-ref)
- Course → Uploads → Questions (AI-generated from exam/practice files)
- Course → StudyTasks (auto-generated from outline)
- Course → Questions (also auto-generated from outline, no exam needed)
- Course → CourseNotes (voice notes, linked to knowledge points)
- User → Attempts → mastery aggregation per knowledge point

## Auto-Pipeline
On course creation, `POST /api/courses/[id]/generate` fires (non-blocking):
1. Filters outline nodes of type `knowledge_point`
2. Runs `generateStudyTasks` + `generateQuestionsFromOutline` in parallel via Qwen
3. Inserts results into `study_tasks` and `questions` tables

## Pages & Routes
| Route | What |
|-------|------|
| `/login` | Email/password + Google OAuth, guest preview support |
| `/dashboard` | Course grid (active + archived), new course button |
| `/new-course` | Upload/paste syllabus → AI parse → preview tasks + questions → create |
| `/course/[id]` | Outline tab (tree + study tasks + learning blueprint) |
| `/course/[id]/practice` | Quiz cards (MC/fill/short/TF), upload exam for more |
| `/course/[id]/progress` | Mastery heatmap + wrong answer notebook |
| `/course/[id]/notes` | Voice notes (speech-to-text) + AI organize |

## API Routes
| Route | Method | What |
|-------|--------|------|
| `/api/courses` | GET/POST | List/create courses |
| `/api/courses/[id]` | GET/PATCH/DELETE | Single course CRUD |
| `/api/courses/[id]/outline` | GET/PUT | Outline tree CRUD |
| `/api/courses/[id]/generate` | POST | Auto-generate tasks + questions from outline |
| `/api/courses/[id]/notes` | GET/POST | Course notes CRUD |
| `/api/courses/[id]/notes/organize` | POST | AI organize notes |
| `/api/upload` | POST | File upload to Supabase Storage |
| `/api/parse` | POST | AI parse file (syllabus or exam) |
| `/api/questions` | GET/POST | Questions CRUD + AI exam extraction |
| `/api/attempts` | POST | Record answer + auto-grade |
| `/api/study-tasks/[id]` | PATCH | Toggle task status (todo/done) |
| `/api/preview/learning` | POST | Guest preview of AI-generated content |

## Components (48 files total)
**Core:** Sidebar, CourseCard, CourseTabs, FileDropzone, OutlineTree, OutlinePreview
**Practice:** QuestionCard, ProgressGrid, WrongAnswerNotebook
**Study:** StudyTaskList, LearningBlueprint, StudyTrackerPanel
**Notes:** VoiceNotesPanel (browser SpeechRecognition → AI organize)
**Auth:** ArchiveButton (archive/restore/delete)

## Conventions
- All API routes validate with Zod before DB operations
- RLS on every table — user_id ownership, child tables via FK joins
- Minimal palette: #101010 accent, #efefeb background, frosted glass surfaces
- No emoji in UI — Lucide icons only
- File uploads → Supabase Storage (`course-files` bucket, private)
