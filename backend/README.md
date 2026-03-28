# Game Freelancer Backend (POC)

Minimal FastAPI backend for project prompt parsing (Gemini), fake freelancer profile discovery, and persisted project-freelancer matches in MongoDB Atlas.

## Quick start

1. Copy `.env.example` to `.env` and fill in your Atlas and Gemini keys.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run index creation:
   - `python backend/scripts/create_indexes.py`
4. Seed fake freelancers:
   - `python backend/scripts/seed_fake_freelancers.py`
   - default seeds 60 freelancers + skill/role catalogs
   - custom count: `python backend/scripts/seed_fake_freelancers.py --count 80`
   - append mode: `python backend/scripts/seed_fake_freelancers.py --count 20 --append`
5. Start API:
   - `uvicorn app.main:app --reload --app-dir backend`

## API endpoints

- `GET /health`
- `GET /api/v1/freelancers`
- `GET /api/v1/freelancers/{freelancer_id}`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `POST /api/v1/parsing`
- `POST /api/v1/matching/{project_id}`
- `GET /api/v1/matching/{project_id}`
