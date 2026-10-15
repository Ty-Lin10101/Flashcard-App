from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3 as sql
from datetime import date
import json

app = FastAPI()

# Allows the desktop UI to securely talk to the Python API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tauri apps run on custom local origins, "*" ensures a stable connection
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    """Initializes the SQLite database and creates the necessary tables if they don't exist."""
    
    conn = sql.connect("flashcards.db")
    cursor = conn.cursor()
    # Create decks table if it doesn't exist
    cursor.execute("""
                CREATE TABLE IF NOT EXISTS decks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL
                )
            """)
    # Create cards table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            metadata JSON,
            correct_count INTEGER DEFAULT 0,
            incorrect_count INTEGER DEFAULT 0,
            next_review_date TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    """Initializes the database when the application starts."""
    
    init_db()

@app.get("/api/decks")
def get_decks():
    """Queries the database for all decks and returns them as a list of dictionaries."""
    
    conn = sql.connect("flashcards.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type FROM decks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "type": r[2]} for r in rows]

@app.post("/api/decks")
def create_deck(deck: dict):
    """Creates a new deck in the database."""
    
    conn = sql.connect("flashcards.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO decks (name, type) VALUES (?, ?)", (deck["name"], deck["type"]))
        conn.commit()
    except sql.IntegrityError:
        conn.close()
        return {"error": "Deck name already exists"}
    conn.close()
    return {"message": "Deck created successfully"}

@app.get("/api/decks/{deck_id}/due-cards")
def get_due_cards_for_deck(deck_id: int):
    """Queries the database for cards that are due for review in the specified deck."""
    
    conn = sql.connect("flashcards.db")
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("SELECT id, front, back, metadata FROM cards WHERE next_review_date <= ? AND deck_id = ?", (today, deck_id))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r[0], 
        "front": r[1], 
        "back": r[2],
        "metadata": json.loads(r[3]) if r[3] else {},
        } for r in rows]
