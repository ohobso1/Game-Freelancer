# Game Freelancer Matcher

Simple full-stack MVP that:
- takes a game idea prompt,
- parses requirements with Gemini,
- matches freelancer profiles from MongoDB,
- shows role-grouped candidates in a React UI.

## Tech Stack

- Backend: FastAPI + MongoDB (Motor)
- AI Parsing: Gemini
- Frontend: React + TypeScript + Vite

## Project Structure

- `backend/` FastAPI API, matching logic, scripts
- `frontend/` React app for prompt input, parsed review, and matches display

## Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas (or compatible MongoDB URI)

## Backend Setup

From project root:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
```

Create `backend/.env` with required values (example):

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB_NAME=game_freelancer
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-flash-latest
```

Seed data and create indexes:

```powershell
python scripts/seed_fake_freelancers.py --count 60
python scripts/create_indexes.py
```

Run backend:

```powershell
uvicorn app.main:app --reload
```

Backend URL: http://localhost:8000

## Frontend Setup

From project root:

```powershell
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Run frontend:

```powershell
npm run dev
```

Frontend URL: http://localhost:5173

## Quick Test Flow

1. Open the frontend in your browser.
2. Enter a game title and prompt.
3. Verify parsed requirements.
4. Generate matches and review role-grouped freelancer columns.

## Notes

- Keep secrets only in `.env` files. Do not commit them.
- If matching results look sparse, reseed freelancers and retry.
