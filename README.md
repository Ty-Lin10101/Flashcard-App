# Flashcard App

A desktop flashcard app in development, with a Python/FastAPI backend and a React + Tauri frontend.

## Project status

The backend and frontend are currently committed on separate branches: `backend` and `frontend`. Neither implementation is on `main` until those branches are merged. The frontend currently opens an empty window and is not yet connected to the API.

## Backend

The backend uses FastAPI and SQLite. On startup, it creates the `decks` and `cards` tables if they do not exist. Run it from the `backend` directory so the database file is `backend/flashcards.db`:

```sh
cd backend
python -m pip install fastapi uvicorn
python -m uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`.

Current endpoints:

- `GET /api/decks` lists decks.
- `POST /api/decks` creates a deck from `{"name": "Example", "type": "standard"}`.
- `GET /api/decks/{deck_id}/due-cards` lists cards due for review in a deck.

## Frontend

The frontend uses React, TypeScript, Vite, and Tauri 2. From the `frontend` directory, install the JavaScript dependencies and run the browser development server or the desktop app:

```sh
cd frontend
npm install
npm run dev
```

To run the Tauri desktop app, use `npm run tauri -- dev` from `frontend`. To type-check and create a production frontend build, run `npm run build` from the repository root or the `frontend` directory. The root command forwards to the frontend build; it does not require the backend to be running. Desktop builds also require the Rust toolchain and Tauri's platform-specific prerequisites.
