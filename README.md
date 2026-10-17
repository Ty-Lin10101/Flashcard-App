# Flashcard App

A desktop flashcard app with a Python/FastAPI backend and a React + Tauri frontend.

## Backend

The backend uses FastAPI and SQLite. Start it from the `backend` directory so the database is stored at `backend/flashcards.db`:

```sh
cd backend
python -m pip install fastapi uvicorn
python -m uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`.

The API supports deck management, card management, review scheduling, and application review settings under `/api`.

## Frontend

The frontend uses React, TypeScript, Vite, and Tauri 2. Install dependencies and start the browser development server from the repository root:

```sh
npm --prefix frontend install
npm --prefix frontend run dev
```

Open the local URL printed by Vite. Deck data and management actions require the backend to be running.

To type-check and create a production frontend build, run `npm run build` from the repository root or `npm run build` from `frontend`. The root command forwards to the frontend build and does not require the backend to be running.

To run the Tauri desktop app, run `npm run tauri -- dev` from `frontend`. Desktop builds also require the Rust toolchain and Tauri's platform-specific prerequisites.

The frontend currently provides deck library and management flows. Study and review screens are not yet implemented.
