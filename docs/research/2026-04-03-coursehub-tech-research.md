# CourseHub Tech Research Report

**Date:** 2026-04-03
**Project:** CourseHub (AI-powered course management for college students)
**Stack:** Next.js 16 + Supabase + Claude API + Tailwind + Zustand

---

## Topic 1: Best Libraries for the Tech Stack

### 1.1 Drag-and-Drop Tree Libraries for Outline Editing

| Library | Weekly Downloads | GitHub Stars | Maintained | Tree Support |
|---------|-----------------|-------------|------------|-------------|
| @dnd-kit | ~12M | 16.9k | Active | Via plugin/example |
| react-beautiful-dnd | ~2.3M | 34k | **Deprecated** (Atlassian stopped) | Lists only |
| react-arborist | ~50k | 3.5k | Active | Native tree |

**@dnd-kit** is the most flexible and actively maintained drag-and-drop library. It supports grids, trees, 2D layouts, and custom interactions. Tree support requires building on top of the `@dnd-kit/sortable` preset -- there's an official `SortableTree` example in the repo and a community package `dnd-kit-sortable-tree` that extracts it into a reusable component. The hook-based API gives full control over sensors, collision detection, and animations.

**react-beautiful-dnd** was the gold standard for list DnD but Atlassian discontinued maintenance. The community fork `@hello-pangea/dnd` keeps it alive but it fundamentally only supports flat lists, not nested trees. Not suitable for course outline editing.

**react-arborist** is purpose-built for tree views with built-in drag-and-drop, inline editing, multi-selection, and virtualization (handles 10k+ nodes). It provides the complete tree UX out of the box: open/close folders, rename nodes inline, drag nodes to new positions. The trade-off is less flexibility for non-tree use cases.

**Recommendation for CourseHub:** Use **react-arborist** for the syllabus outline editor. It provides exactly what we need (tree DnD + inline edit + virtualization) with minimal setup. If we later need DnD elsewhere (e.g., quiz question reordering), add `@dnd-kit` for those specific cases. Avoid react-beautiful-dnd -- it's dead.

**Sources:**
- [dnd-kit Official Docs](https://dndkit.com/)
- [react-arborist GitHub](https://github.com/brimdata/react-arborist)
- [npm trends comparison](https://npmtrends.com/@dnd-kit/core-vs-react-beautiful-dnd-vs-react-dnd-vs-react-drag-and-drop-vs-react-draggable-vs-react-file-drop)
- [dnd-kit-sortable-tree](https://github.com/Shaddix/dnd-kit-sortable-tree)
- [Puck: Top 5 DnD Libraries 2026](https://puckeditor.com/blog/top-5-drag-and-drop-libraries-for-react)

---

### 1.2 File Upload / Dropzone Libraries

| Library | Weekly Downloads | Approach | Full-Stack |
|---------|-----------------|----------|-----------|
| react-dropzone | ~5M | Headless UI only | No |
| FilePond | ~500k | Full widget + plugins | Partial |
| UploadThing | ~300k (growing) | Full-stack service | Yes |

**react-dropzone** is a headless component -- it handles drag-and-drop zone UI and file validation but does NOT upload files. You pair it with your own upload logic (e.g., Supabase Storage presigned URLs). Extremely lightweight (~7kb), fully customizable, no opinions on styling.

**FilePond** is a batteries-included upload widget with chunked/resumable uploads, image preview, file validation plugins, and a polished default UI. Heavier than react-dropzone but handles the full upload lifecycle including progress indicators and retry. Supports React, Vue, Angular.

**UploadThing** is a full-stack upload service (from the T3 stack team). You define "File Routes" on the server specifying allowed types/sizes, and it handles S3 storage, signed URLs, CDN delivery, and webhook callbacks. Pricing starts at $10/month. Type-safe from route definition to client component.

**Recommendation for CourseHub:** Use **react-dropzone** for the UI + **Supabase Storage** for the backend. We already have Supabase in the stack, so adding UploadThing would introduce an unnecessary dependency and monthly cost. react-dropzone gives us full control over the upload UX (drag area, file preview, validation), and we upload directly to Supabase Storage via signed URLs. For large files (>6MB syllabi/exams), use Supabase's TUS resumable upload protocol.

**Sources:**
- [react-dropzone docs](https://react-dropzone.js.org/)
- [UploadThing docs](https://docs.uploadthing.com/)
- [PkgPulse: Best File Upload Libraries 2026](https://www.pkgpulse.com/blog/best-file-upload-libraries-react-2026)
- [Supabase Dropzone Component](https://supabase.com/ui/docs/nextjs/dropzone)

---

### 1.3 PDF/File Processing in Next.js API Routes with Claude Vision

**Architecture:** Next.js Route Handler receives file upload -> store in Supabase Storage -> read file as base64 -> send to Claude API with `type: "document"` source.

**Key technical details:**
- Claude API accepts PDF via base64 encoding with `media_type: "application/pdf"` or via the new **Files API** (upload once, reference by `file_id`)
- Each PDF page costs **1,500-3,000 tokens** (pages are converted to images internally)
- Maximum **100 pages** per API request
- Maximum file size: **32MB** per Messages API request, **500MB** via Files API

**For large documents (>10 pages):**
1. **Files API (recommended):** Upload the PDF once via `POST /v1/files`, get a `file_id`, reuse across multiple API calls. Files persist until deleted. 500GB storage per org.
2. **Page batching:** Split large PDFs into chunks (e.g., 10 pages each), process in parallel, merge results.
3. **Prompt caching:** For repeated analysis of the same document, caching reduces cost by up to 90% and latency by 80%.
4. **Batch API:** For non-real-time processing (e.g., batch syllabus imports), use the Batch API for 50% discount on tokens.

**Cost optimization strategy for CourseHub:**
- Average syllabus: 5-15 pages = 7,500-45,000 tokens = ~$0.02-$0.14 per syllabus (Sonnet)
- Use Files API to upload once, then run multiple extraction passes (outline, key dates, topics)
- Combine prompt caching + Haiku for simple extractions, Sonnet for complex parsing

**Recommendation for CourseHub:** Use the **Files API** for PDF storage + **Claude Sonnet** for syllabus parsing with structured output (tool use). For exam/quiz conversion, use **Haiku** (cheaper, fast enough for flashcard generation). Process pages 1-5 first to show instant results, then continue background processing.

**Sources:**
- [Claude PDF Support Docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support)
- [Claude Files API](https://platform.claude.com/docs/en/build-with-claude/files)
- [Claude Vision Docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- [Claude API Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

---

## Topic 2: Competitive Landscape (2026 State)

### 2.1 Major Players

#### Knowt (knowt.com)
- **Status (2026):** 5M+ users. Emerged as the top free Quizlet alternative.
- **Features:** Upload notes/lectures -> AI generates flashcards, quizzes, study guides. AP exam prep library. Spaced repetition built in.
- **Strengths:** Free tier is generous. Strong at converting messy notes into structured study materials.
- **Weakness:** No course-level organization. No syllabus parsing. Individual document focus, not semester-wide view.
- **Pricing:** Free with premium features.

#### StudyFetch (studyfetch.com)
- **Status (2026):** Leading AI study platform. "Spark.E" AI tutor is the key differentiator.
- **Features:** Upload PDFs/slides/videos/handwritten notes -> flashcards, quizzes, notes, AI tutor. Calendar integration (upload syllabus photo -> extract events). Course-based organization.
- **Strengths:** Interactive AI tutor chat. Course organization. Syllabus-to-calendar feature.
- **Weakness:** Expensive ($9.99/mo). AI tutor is generic, not personalized to mastery level.
- **Differentiator from CourseHub:** StudyFetch focuses on individual material conversion. CourseHub's edge is the knowledge-point heatmap and mastery tracking across an entire course.

#### Quizlet
- **Status (2026):** Acquired Coconote (note-taking app with 1B+ views). Launched unified AI learning experience in Feb 2026.
- **Features:** AI-generated flashcards, quizzes, explanations grounded in user's materials. New: audio/video recording -> notes/quizzes via Coconote integration.
- **Strengths:** Massive user base. Brand recognition. Coconote acquisition fills the "upload anything" gap.
- **Pricing:** $7.99/month for Quizlet Plus.
- **Weakness:** Still primarily flashcard-focused. No syllabus-level organization or mastery tracking.

#### Brainscape
- **Status (2026):** Niche player focused on confidence-based repetition (rate cards 1-5).
- **Features:** AI card creation (Pro only). Expert-certified content library. Confidence-based spaced repetition.
- **Strengths:** Strong for structured exam prep (medical, legal). Algorithm is well-regarded.
- **Weakness:** Premium features locked behind paywall. No document upload/parsing. Manual card creation for free tier.

#### Anki
- **Status (2026):** Still the gold standard for serious spaced repetition users (med students, language learners).
- **Updates:** Now uses FSRS (machine-learning scheduling algorithm). Third-party AI add-ons via AnkiHub for card generation.
- **Strengths:** Free, open-source, most customizable. FSRS algorithm trained on hundreds of millions of reviews.
- **Weakness:** Steep learning curve. Ugly default UI. No built-in AI -- requires add-ons.

### 2.2 New Entrants (2026)

#### YouLearn (YC-backed)
- **Status:** 150k MAU, 2.2M+ learning materials uploaded. iOS + Android apps.
- **Features:** Upload PDFs/videos/slides/recordings -> notes, flashcards, quizzes, podcasts, AI tutor. Supports 40+ languages. Personalized exams with answer breakdowns and progress tracking.
- **Key differentiator:** Voice AI tutor you can "talk to." Lecture recording -> instant chapters + transcripts.
- **Threat level: HIGH.** Most similar to CourseHub's vision. BUT: no syllabus-level course organization, no knowledge-point heatmap.

#### Miyagi Labs (YC-backed)
- AI-powered exam prep for SAT/ACT. AI tutoring + personalized study plans + practice questions + realistic exams.
- Narrow focus on standardized testing -- not a direct competitor for college course management.

#### Microsoft Study and Learn Agent
- Available in Microsoft 365 Copilot for students 13+.
- Flashcards, matching exercises, adaptive quizzes, guided study.
- Integrated into existing Microsoft ecosystem. Low threat for standalone app but signals market validation.

### 2.3 Competitive Gap Analysis

**What everyone does:** Upload material -> generate flashcards/quizzes/summaries. This is table stakes in 2026.

**What nobody does well:**
1. **Semester-level course organization** -- most tools are document-centric, not course-centric
2. **Cross-topic mastery tracking** -- no one shows "you're weak on Chapter 7 topics" as a heatmap
3. **Syllabus-first workflow** -- only StudyFetch does basic syllabus-to-calendar; nobody structures the entire course outline from the syllabus
4. **Multi-course dashboard** -- students take 4-5 courses; no tool gives a unified view with archiving

**CourseHub's positioning:** The "course operating system" -- not another flashcard app, but a tool that takes your syllabus as the organizing principle and tracks mastery across all topics in all your courses.

**Sources:**
- [Knowt](https://knowt.com/)
- [StudyFetch](https://www.studyfetch.com/)
- [Quizlet Coconote acquisition](https://www.prnewswire.com/news-releases/quizlet-supercharges-studying-with-new-product-innovations-and-strategic-acquisition-302679622.html)
- [Best AI Study Tools 2026](https://laxuai.com/blog/best-ai-study-tools-2026)
- [YouLearn](https://www.youlearn.ai/)
- [Y Combinator Education Companies](https://www.ycombinator.com/companies/industry/education)
- [StudyFetch Alternatives 2026](https://www.cramberry.study/blog/studyfetch-alternatives-2026)
- [Brainscape vs Anki](https://learnlog.app/vs/anki-vs-brainscape/)
- [Best Spaced Repetition Apps 2026](https://www.mintdeck.app/blog/best-spaced-repetition-apps-2026)

---

## Topic 3: Claude API Best Practices for Structured Output

### 3.1 Structured Output (GA in 2026)

Claude now supports **structured outputs** as a generally available feature for Claude Sonnet 4.5, Opus 4.5, and Haiku 4.5.

**Two approaches:**

1. **Tool Use (recommended for CourseHub):** Define a tool schema, Claude fills it with guaranteed-valid parameters. Use `strict: true` for schema-enforced output -- every field, type, and constraint is guaranteed.

2. **JSON Mode:** Provide a JSON Schema directly in the request. Claude outputs conforming JSON. Simpler but less flexible than tool use.

**Best practices:**
- Use **Zod** (TypeScript) to define schemas -- the SDK auto-generates JSON Schema and provides typed parsing
- Keep schemas focused -- one tool per extraction task (e.g., `extract_outline`, `extract_quiz_questions`)
- Tool definitions benefit from **prompt caching** -- same tools across requests = automatic token savings after first call
- Complex schemas produce larger grammars that take longer to compile -- prefer flat structures over deeply nested ones

**Example for syllabus parsing:**
```typescript
const syllabusSchema = z.object({
  courseName: z.string(),
  instructor: z.string(),
  semester: z.string(),
  outline: z.array(z.object({
    week: z.number(),
    topic: z.string(),
    subtopics: z.array(z.string()),
    readings: z.array(z.string()).optional(),
    dueDate: z.string().optional(),
  })),
  gradingPolicy: z.object({
    components: z.array(z.object({
      name: z.string(),
      weight: z.number(),
    })),
  }),
});
```

**Recommendation for CourseHub:** Use **tool use with strict mode** for all AI extractions. Define separate tools for each task: `parse_syllabus`, `generate_quiz`, `extract_key_concepts`. Use Zod schemas for type safety from API response to React component.

**Sources:**
- [Claude Structured Outputs Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Claude Structured Outputs Blog Post](https://claude.com/blog/structured-outputs-on-the-claude-developer-platform)
- [Agent Structured Outputs](https://platform.claude.com/docs/en/agent-sdk/structured-outputs)
- [Claude Strict Mode Guide](https://learn-prompting.fr/blog/claude-structured-outputs-strict-mode)

---

### 3.2 Claude Vision with PDFs -- Token Optimization

**How it works:** When you send a PDF, Claude converts each page into an image. This means PDF processing uses vision token costs, not text token costs.

**Token costs per page:**
| Content Type | Tokens/Page | Cost (Sonnet) |
|-------------|------------|---------------|
| Text-heavy (syllabus) | ~1,500 | ~$0.005 |
| Mixed (slides) | ~2,000 | ~$0.006 |
| Graphics-heavy (diagrams) | ~3,000 | ~$0.009 |

**Optimization strategies:**

1. **Use Files API for reuse:** Upload once, reference by `file_id` in multiple requests. Avoids re-sending base64 data. Files persist until deleted (500GB org limit, 500MB per file).

2. **Prompt caching for repeated analysis:** If running multiple extraction passes on the same PDF (outline pass, then quiz pass, then key concepts), enable prompt caching. First pass costs 1.25x, subsequent passes cost 0.1x = 90% savings.

3. **Page batching for large documents:** For a 50-page textbook chapter, process in batches of 10. Run batches in parallel via Promise.all. Merge results with a final Claude call.

4. **Model tiering by task:**
   - **Haiku** ($1/$5 per M tokens): Simple extractions (dates, titles, basic Q&A generation)
   - **Sonnet** ($3/$15 per M tokens): Complex parsing (syllabus structure, multi-step reasoning)
   - **Opus** ($5/$25 per M tokens): Only for the hardest tasks (ambiguous layouts, handwritten notes)

5. **Place documents first in prompt:** Anthropic's docs state that placing long documents above instructions improves quality by up to 30%.

6. **Batch API for non-urgent processing:** 50% discount on tokens for async processing. Perfect for batch syllabus imports or end-of-day quiz generation.

**Recommendation for CourseHub:** Implement a two-tier processing pipeline. **Fast path:** Use Sonnet + Files API for immediate syllabus parsing (user waits). **Background path:** Use Haiku + Batch API for quiz generation, flashcard creation, and concept extraction (runs async, notifies user when done). Cache aggressively -- students will re-open the same syllabus many times.

**Sources:**
- [Claude PDF Support](https://platform.claude.com/docs/en/build-with-claude/pdf-support)
- [Claude Files API](https://platform.claude.com/docs/en/build-with-claude/files)
- [Claude Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Claude Token-Saving Updates](https://claudelab.net/en/articles/api-sdk/claude-api-token-saving-updates-cost-optimization)
- [Claude Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

---

## Topic 4: Supabase Patterns for CourseHub

### 4.1 File Storage in Supabase Storage

**Best practices:**

1. **Bucket organization:** Create separate buckets per file type:
   - `syllabi` -- uploaded syllabus PDFs
   - `exams` -- uploaded past exams/practice materials
   - `avatars` -- user profile images

2. **Private buckets by default:** All Supabase buckets are private. Set up RLS policies per bucket to control who can read/write.

3. **Signed URLs for upload:** Use server-generated signed upload URLs instead of direct client uploads. This avoids Next.js body size limits (default 1MB) and keeps auth server-side.

4. **TUS resumable uploads for large files:** Any file >6MB should use the TUS protocol for reliability. Supabase Storage supports this natively.

5. **Avoid overwriting files:** CDN propagation takes time when files change at the same path. Always upload to a new path (e.g., `{userId}/{timestamp}_{filename}`). This also serves as a version history.

6. **Unique file naming:** Use `${Date.now()}_${crypto.randomUUID()}_${sanitizedFilename}` pattern to avoid collisions.

**Implementation pattern for CourseHub:**
```
Upload flow:
1. Client: react-dropzone captures file
2. Client: calls API route /api/upload/presign
3. Server: validates user auth, generates Supabase signed upload URL
4. Client: uploads directly to Supabase Storage via signed URL
5. Server: on upload complete, stores file metadata in DB
6. Server: triggers async Claude processing via background job
```

**Sources:**
- [Supabase Standard Uploads](https://supabase.com/docs/guides/storage/uploads/standard-uploads)
- [Supabase File Upload Guide](https://nikofischer.com/supabase-storage-file-upload-guide)
- [Signed URL Uploads with Next.js](https://medium.com/@olliedoesdev/signed-url-file-uploads-with-nextjs-and-supabase-74ba91b65fe0)
- [Supabase Dropzone Component](https://supabase.com/ui/docs/nextjs/dropzone)

---

### 4.2 Tree Data Structures in PostgreSQL

For storing course outlines (syllabus -> units -> topics -> subtopics), we need a tree structure. Three main approaches:

#### Adjacency List
```sql
CREATE TABLE outline_nodes (
  id UUID PRIMARY KEY,
  parent_id UUID REFERENCES outline_nodes(id),
  course_id UUID REFERENCES courses(id),
  title TEXT NOT NULL,
  sort_order INT NOT NULL,
  depth INT NOT NULL
);
```
- **Pros:** Simplest model. Easy inserts/updates/deletes. Moves are a single UPDATE (change parent_id).
- **Cons:** Fetching full subtree requires recursive CTE (`WITH RECURSIVE`). Slow for deep trees.
- **Best for:** Trees with <500 nodes, frequent modifications, depth <10 levels.

#### Materialized Path
```sql
CREATE TABLE outline_nodes (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(id),
  path TEXT NOT NULL,  -- e.g., 'root.unit1.topic3.subtopic2'
  title TEXT NOT NULL,
  sort_order INT NOT NULL
);
-- Fetch all children: WHERE path LIKE 'root.unit1.%'
```
- **Pros:** Fast subtree queries (single LIKE or prefix match). No recursion needed.
- **Cons:** Moving a node requires updating all descendant paths. Path string can get long.
- **Best for:** Read-heavy workloads, infrequent moves, moderate tree sizes.

#### ltree (PostgreSQL Extension)
```sql
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE TABLE outline_nodes (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(id),
  path ltree NOT NULL,  -- e.g., 'root.unit1.topic3'
  title TEXT NOT NULL,
  sort_order INT NOT NULL
);
CREATE INDEX idx_path ON outline_nodes USING GIST (path);
-- Subtree: WHERE path <@ 'root.unit1'
-- Ancestors: WHERE path @> 'root.unit1.topic3'
```
- **Pros:** Native PostgreSQL operators (`<@`, `@>`, `~`, `?`). GiST index for fast queries. Pattern matching with `lquery`.
- **Cons:** ltree labels must be alphanumeric (no spaces/special chars -- need to use IDs as labels). GiST index has size limitations for very deep trees. Moving subtrees still requires updating all descendant paths.
- **Available in Supabase:** Yes, ltree is in the [Supabase extensions list](https://supabase.com/docs/guides/database/extensions).

**Recommendation for CourseHub:** Use **adjacency list** for the MVP. A course syllabus outline is typically 3-5 levels deep with <200 nodes -- well within the recursive CTE performance sweet spot. Adjacency list gives us the simplest move/reorder operations (critical for the drag-and-drop editor). Fetch the entire tree in one recursive query, cache in Zustand on the client.

If we later find performance issues with very large outlines, migrate to ltree. But premature optimization here adds complexity we don't need at MVP.

```sql
-- Fetch full tree for a course (adjacency list, one query)
WITH RECURSIVE tree AS (
  SELECT id, parent_id, title, sort_order, 0 AS depth
  FROM outline_nodes
  WHERE course_id = $1 AND parent_id IS NULL
  UNION ALL
  SELECT n.id, n.parent_id, n.title, n.sort_order, t.depth + 1
  FROM outline_nodes n
  JOIN tree t ON n.parent_id = t.id
)
SELECT * FROM tree ORDER BY depth, sort_order;
```

**Sources:**
- [PostgreSQL ltree Docs](https://www.postgresql.org/docs/current/ltree.html)
- [Hierarchical Models in PostgreSQL](https://www.ackee.agency/blog/hierarchical-models-in-postgresql)
- [Modeling Hierarchical Tree Data](https://leonardqmarcq.com/posts/modeling-hierarchical-tree-data)
- [Supabase ltree Discussion](https://github.com/orgs/supabase/discussions/18505)
- [PostgreSQL ltree vs WITH RECURSIVE](https://www.cybertec-postgresql.com/en/postgresql-ltree-vs-with-recursive/)

---

### 4.3 RLS Patterns for Multi-Tenant SaaS

CourseHub's data model: Users -> Courses -> Outline Nodes / Quizzes / Mastery Records. Each user owns their own courses (single-tenant per user initially, with potential for shared courses later).

**Pattern 1: User-Owned Resources (MVP)**
```sql
-- Every table has a user_id column
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own courses"
ON courses FOR ALL
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- For child tables, join to parent
CREATE POLICY "Users can CRUD own outline nodes"
ON outline_nodes FOR ALL
USING (
  EXISTS (
    SELECT 1 FROM courses
    WHERE courses.id = outline_nodes.course_id
    AND courses.user_id = auth.uid()
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM courses
    WHERE courses.id = outline_nodes.course_id
    AND courses.user_id = auth.uid()
  )
);
```

**Pattern 2: Team/Org-Based (Future)**
```sql
-- Add org_id to users via custom JWT claims
-- Set during login via Supabase Auth hooks
CREATE POLICY "Org members can read shared courses"
ON courses FOR SELECT
USING (
  org_id = (auth.jwt() -> 'app_metadata' ->> 'org_id')::uuid
);
```

**Critical best practices:**
1. **Always index RLS columns:** Missing indexes on `user_id`, `course_id`, `org_id` are the #1 RLS performance killer.
2. **Test from client SDK, not SQL Editor:** The SQL Editor bypasses RLS. Always verify policies via the actual Supabase client.
3. **Separate USING vs WITH CHECK:** `USING` controls reads/deletes, `WITH CHECK` controls inserts/updates. UPDATE needs both.
4. **Enable RLS on EVERY table:** Any table exposed via PostgREST API without RLS = data leak. Enable RLS first, add policies second.
5. **Use `auth.uid()` not `current_user`:** `auth.uid()` extracts from the JWT, which is the correct identifier for Supabase Auth.

**Recommendation for CourseHub:** Start with Pattern 1 (user-owned). Add `user_id` to `courses` table, cascade ownership to child tables via foreign key joins in policies. Index every column used in RLS policies. Enable RLS on all tables from day one -- retrofitting RLS is painful and error-prone.

**Sources:**
- [Supabase RLS Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase RLS Best Practices](https://makerkit.dev/blog/tutorials/supabase-rls-best-practices)
- [Multi-Tenant RLS Deep Dive](https://dev.to/blackie360/-enforcing-row-level-security-in-supabase-a-deep-dive-into-lockins-multi-tenant-architecture-4hd2)
- [Supabase RLS Production Patterns](https://designrevision.com/blog/supabase-row-level-security)
- [Supabase Best Practices](https://www.leanware.co/insights/supabase-best-practices)

---

## Summary: Recommended Tech Choices for CourseHub MVP

| Decision | Choice | Why |
|----------|--------|-----|
| Tree DnD | react-arborist | Purpose-built for tree editing, virtualized, minimal setup |
| File upload UI | react-dropzone | Headless, lightweight, pairs with Supabase Storage |
| File storage | Supabase Storage (signed URLs) | Already in stack, no extra cost |
| PDF parsing | Claude Sonnet + Files API + tool use (strict) | Best balance of quality and cost |
| Quiz generation | Claude Haiku + Batch API | Cheap, fast, async |
| Structured output | Zod schemas + tool use (strict: true) | Type-safe, guaranteed valid JSON |
| Tree DB model | Adjacency list (recursive CTE) | Simplest for <200 nodes, easy DnD reorder |
| Auth/access | Supabase RLS (user_id ownership) | Foundation-level security, not bolted on later |
| State management | Zustand | Already in stack, cache full tree client-side |

**Estimated per-user API cost:** ~$0.05-$0.20 per syllabus import (one-time), ~$0.01-$0.05 per quiz generation session. Well within viable SaaS economics at $5-10/month pricing.
