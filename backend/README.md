# Learning Recommendation Engine - Backend (Team 2)

FastAPI backend for the personalized learning recommendation engine. Consumes skill-analysis JSON produced by Team 1 and generates course roadmaps.

## Tech Stack

- **FastAPI** — REST API
- **Supabase (PostgreSQL)** — data storage, accessed via the `supabase-py` client over the REST API
- **pgvector** — course similarity search over Gemini embeddings
- **Gemini API** — generates course embeddings and (optionally) natural-language recommendation text

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your Supabase project's API credentials (Dashboard → Project Settings → API):
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   SUPABASE_JWT_SECRET=your-supabase-jwt-secret
   GEMINI_API_KEY=your-gemini-api-key
   ```
   Get a Gemini key from https://aistudio.google.com/app/apikey. If left blank, course matching falls back to naive keyword overlap instead of vector search.

3. Create the tables (including the `vector` extension, `courses.embedding` column, and `match_courses` RPC): run `app/db/schema.sql` once in the Supabase SQL editor.

4. Run the server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8001
   ```

   The async Supabase client is initialised on startup (see `app/core/supabase_client.py`). API docs available at `http://localhost:8001/docs`.

## Data Flow

1. **Team 1** posts the skill-analysis JSON to `POST /api/v1/skills/ingest`.
2. Backend stores it in `skill_profiles` and derives skill gaps.
3. User submits learning preferences via `POST /api/v1/learning/recommend` (`hours_per_week`, `learning_rate`).
4. Backend embeds the skill gaps with Gemini, runs a pgvector similarity search over `courses.embedding` (via the `match_courses` RPC) to find the closest-matching courses, and builds a sequenced, month-by-month roadmap, stored in `roadmaps` / `roadmap_courses`.
5. Frontend fetches the roadmap via `GET /api/v1/learning/roadmap/{user_id}`.
6. User manually reports progress via `POST /api/v1/learning/progress/{roadmap_course_id}`.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/skills/ingest` | Ingest skill-analysis JSON from Team 1 |
| GET | `/api/v1/skills/{user_id}` | Fetch stored skill profile |
| GET | `/api/v1/courses` | List courses (filter by `category`, `difficulty`) |
| POST | `/api/v1/courses` | Add a course (MVP seeding helper) |
| POST | `/api/v1/learning/recommend` | Generate a roadmap from skill gaps + preferences |
| GET | `/api/v1/learning/roadmap/{user_id}` | Fetch the active roadmap |
| POST | `/api/v1/learning/progress/{roadmap_course_id}` | Update completion/quiz progress for a course |
| GET | `/health` | Health check |

## Notes

- No auth layer yet — add JWT verification (mirroring `backend/app/middleware/auth.py`) before this goes beyond MVP/demo.
- Every course created via `POST /api/v1/courses` is automatically embedded with Gemini (`app/core/gemini_client.py`) and stored in `courses.embedding`. If `GEMINI_API_KEY` is unset, courses are saved without an embedding and matching falls back to naive tag-overlap (`app/repositories/course.py::list_by_skills`).
- Seed courses via `POST /api/v1/courses` (or a script) before testing `/learning/recommend`, otherwise the roadmap will be empty.
