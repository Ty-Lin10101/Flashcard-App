from contextlib import closing

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3 as sql
from datetime import date, timedelta
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

    with closing(sql.connect("flashcards.db")) as conn:
        # Create decks table if it doesn't exist
        conn.execute("""
                CREATE TABLE IF NOT EXISTS decks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    description TEXT
                )
            """)
        # Create cards table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                metadata JSON,
                correct_count INTEGER DEFAULT 0,
                incorrect_count INTEGER DEFAULT 0,
                next_review_date TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                use_review_dates INTEGER NOT NULL DEFAULT 1,
                max_cards_per_day INTEGER NOT NULL DEFAULT 20,
                review_count_date TEXT,
                reviews_today INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.execute(
            "INSERT OR IGNORE INTO app_settings (id, use_review_dates, max_cards_per_day) VALUES (1, 1, 20)"
        )
        settings_columns = {column[1] for column in conn.execute("PRAGMA table_info(app_settings)")}
        if "review_count_date" not in settings_columns:
            conn.execute("ALTER TABLE app_settings ADD COLUMN review_count_date TEXT")
        if "reviews_today" not in settings_columns:
            conn.execute("ALTER TABLE app_settings ADD COLUMN reviews_today INTEGER NOT NULL DEFAULT 0")
        deck_columns = {column[1] for column in conn.execute("PRAGMA table_info(decks)")}
        if "description" not in deck_columns:
            conn.execute("ALTER TABLE decks ADD COLUMN description TEXT")
        deck_settings_columns = {column[1] for column in conn.execute("PRAGMA table_info(decks)")}
        if "use_review_dates" not in deck_settings_columns:
            conn.execute("ALTER TABLE decks ADD COLUMN use_review_dates INTEGER")
        if "daily_limit" not in deck_settings_columns:
            conn.execute("ALTER TABLE decks ADD COLUMN daily_limit INTEGER")
        if "review_interval_days" not in deck_settings_columns:
            conn.execute("ALTER TABLE decks ADD COLUMN review_interval_days INTEGER")
        if "review_count_date" not in deck_settings_columns:
            conn.execute("ALTER TABLE decks ADD COLUMN review_count_date TEXT")
        if "reviews_today" not in deck_settings_columns:
            conn.execute("ALTER TABLE decks ADD COLUMN reviews_today INTEGER NOT NULL DEFAULT 0")
        columns = {column[1] for column in conn.execute("PRAGMA table_info(cards)")}
        if "type" not in columns:
            conn.execute("ALTER TABLE cards ADD COLUMN type TEXT NOT NULL DEFAULT 'basic'")
        conn.execute(
            "UPDATE cards SET next_review_date = ? WHERE next_review_date IS NULL",
            (date.today().isoformat(),),
        )
        conn.commit()


def get_db():
    conn = sql.connect("flashcards.db", check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

@app.on_event("startup")
def startup_event():
    """Initializes the database when the application starts."""
    
    init_db()


def read_review_settings(conn: sql.Connection):
    row = conn.execute(
        "SELECT use_review_dates, max_cards_per_day, review_count_date, reviews_today FROM app_settings WHERE id = 1"
    ).fetchone()
    reviews_today = row[3] if row[2] == date.today().isoformat() else 0
    return {
        "use_review_dates": bool(row[0]),
        "max_cards_per_day": row[1],
        "reviews_today": reviews_today,
        "daily_recommendation_reached": bool(row[0]) and reviews_today >= row[1],
    }


def read_deck_review_settings(conn: sql.Connection, deck_id: int):
    row = conn.execute(
        """SELECT COALESCE(decks.use_review_dates, app_settings.use_review_dates),
                  COALESCE(decks.daily_limit, app_settings.max_cards_per_day),
                  decks.review_interval_days,
                  CASE WHEN decks.review_count_date = ? THEN decks.reviews_today ELSE 0 END
           FROM decks CROSS JOIN app_settings
           WHERE decks.id = ? AND app_settings.id = 1""",
        (date.today().isoformat(), deck_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    return {
        "use_review_dates": bool(row[0]),
        "daily_limit": row[1],
        "review_interval_days": row[2],
        "reviews_today": row[3],
        "daily_recommendation_reached": bool(row[0]) and row[3] >= row[1],
    }


@app.get("/api/settings")
def get_settings(conn: sql.Connection = Depends(get_db)):
    return read_review_settings(conn)


@app.patch("/api/settings")
def update_settings(settings: dict, conn: sql.Connection = Depends(get_db)):
    allowed_fields = {"use_review_dates", "max_cards_per_day"}
    if not settings or not settings.keys() <= allowed_fields:
        raise HTTPException(status_code=400, detail="Provide supported review settings")

    current = read_review_settings(conn)
    use_review_dates = settings.get("use_review_dates", current["use_review_dates"])
    max_cards_per_day = settings.get("max_cards_per_day", current["max_cards_per_day"])
    if type(use_review_dates) is not bool:
        raise HTTPException(status_code=422, detail="use_review_dates must be a boolean")
    if type(max_cards_per_day) is not int or max_cards_per_day < 1:
        raise HTTPException(status_code=422, detail="max_cards_per_day must be a positive integer")
    if "max_cards_per_day" in settings and not use_review_dates:
        raise HTTPException(status_code=400, detail="Enable review dates to change the daily card limit")

    conn.execute(
        "UPDATE app_settings SET use_review_dates = ?, max_cards_per_day = ? WHERE id = 1",
        (int(use_review_dates), max_cards_per_day),
    )
    conn.commit()
    return read_review_settings(conn)

@app.get("/api/decks")
def get_decks(conn: sql.Connection = Depends(get_db)):
    """Queries the database for all decks and returns them as a list of dictionaries."""

    rows = conn.execute(
        """SELECT decks.id, decks.name, decks.type, decks.description,
                  COALESCE(decks.use_review_dates, app_settings.use_review_dates),
                  COALESCE(decks.daily_limit, app_settings.max_cards_per_day),
                  decks.review_interval_days,
                  CASE WHEN decks.review_count_date = ? THEN decks.reviews_today ELSE 0 END
           FROM decks CROSS JOIN app_settings
           WHERE app_settings.id = 1""",
        (date.today().isoformat(),),
    ).fetchall()
    return [{
        "id": row[0], "name": row[1], "type": row[2], "description": row[3],
        "use_review_dates": bool(row[4]), "daily_limit": row[5],
        "review_interval_days": row[6], "reviews_today": row[7],
        "daily_recommendation_reached": bool(row[4]) and row[7] >= row[5],
    } for row in rows]

@app.post("/api/decks")
def create_deck(deck: dict, conn: sql.Connection = Depends(get_db)):
    """Creates a new deck in the database."""

    try:
        conn.execute("INSERT INTO decks (name, type, description) VALUES (?, ?, ?)", (deck["name"], deck["type"], deck.get("description")))
        conn.commit()
    except sql.IntegrityError:
        return {"error": "Deck name already exists"}
    return {"message": "Deck created successfully"}

@app.patch("/api/decks/{deck_id}")
def update_deck(deck_id: int, deck: dict, conn: sql.Connection = Depends(get_db)):
    """Updates deck details and its review settings."""

    fields = (
        "name", "type", "description", "use_review_dates", "daily_limit", "review_interval_days"
    )
    updates = {field: deck[field] for field in fields if field in deck}
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one deck field to update")
    for field in ("name", "type"):
        if field in updates and not isinstance(updates[field], str):
            raise HTTPException(status_code=422, detail=f"{field} must be a string")
    if "description" in updates and updates["description"] is not None and not isinstance(updates["description"], str):
        raise HTTPException(status_code=422, detail="description must be a string or null")
    if "use_review_dates" in updates and updates["use_review_dates"] is not None and type(updates["use_review_dates"]) is not bool:
        raise HTTPException(status_code=422, detail="use_review_dates must be a boolean or null")
    for field in ("daily_limit", "review_interval_days"):
        value = updates.get(field)
        if field in updates and value is not None and (type(value) is not int or value < 1):
            raise HTTPException(status_code=422, detail=f"{field} must be a positive integer or null")

    assignments = ", ".join(f"{field} = ?" for field in updates)
    values = tuple(
        int(value) if field == "use_review_dates" and value is not None else value
        for field, value in updates.items()
    )
    result = conn.execute(
        f"UPDATE decks SET {assignments} WHERE id = ?",
        (*values, deck_id),
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Deck not found")

    conn.commit()
    return {"message": "Deck updated successfully"}


@app.delete("/api/decks/{deck_id}")
def delete_deck(deck_id: int, conn: sql.Connection = Depends(get_db)):
    if conn.execute("SELECT 1 FROM decks WHERE id = ?", (deck_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    conn.execute("DELETE FROM cards WHERE deck_id = ?", (deck_id,))
    conn.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
    conn.commit()
    return {"message": "Deck deleted successfully"}

@app.get("/api/decks/{deck_id}/due-cards")
def get_due_cards_for_deck(deck_id: int, conn: sql.Connection = Depends(get_db)):
    """Queries the database for cards that are due for review in the specified deck."""

    settings = read_deck_review_settings(conn, deck_id)
    today = date.today().isoformat()
    if settings["use_review_dates"]:
        rows = conn.execute(
            """SELECT id, type, front, back, metadata, correct_count, incorrect_count, next_review_date
               FROM cards
               WHERE deck_id = ? AND (next_review_date IS NULL OR next_review_date <= ?)
               ORDER BY COALESCE(next_review_date, ?), id""",
            (deck_id, today, today),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT id, type, front, back, metadata, correct_count, incorrect_count, next_review_date
               FROM cards WHERE deck_id = ? ORDER BY id""",
            (deck_id,),
        ).fetchall()
    return [serialize_card(row) for row in rows]


def serialize_card(row):
    return {
        "id": row[0],
        "type": row[1],
        "front": row[2],
        "back": row[3],
        "metadata": json.loads(row[4]) if row[4] else {},
        "correct_count": row[5],
        "incorrect_count": row[6],
        "next_review_date": row[7],
    }


@app.get("/api/decks/{deck_id}/cards")
def get_cards_for_deck(deck_id: int, conn: sql.Connection = Depends(get_db)):
    rows = conn.execute(
        """SELECT id, type, front, back, metadata, correct_count, incorrect_count, next_review_date
           FROM cards WHERE deck_id = ? ORDER BY id""",
        (deck_id,),
    ).fetchall()
    return [serialize_card(row) for row in rows]

@app.post("/api/decks/{deck_id}/cards")
def create_card(deck_id: int, card: dict, conn: sql.Connection = Depends(get_db)):
    """Creates a new card in the specified deck."""

    metadata_json = json.dumps(card.get("metadata", {}))
    conn.execute(
        "INSERT INTO cards (deck_id, type, front, back, metadata, next_review_date) VALUES (?, ?, ?, ?, ?, ?)",
        (deck_id, card["type"], card["front"], card["back"], metadata_json, date.today().isoformat())
    )
    conn.commit()
    return {"message": "Card created successfully"}


@app.patch("/api/decks/{deck_id}/cards/{card_id}")
def update_card(deck_id: int, card_id: int, card: dict, conn: sql.Connection = Depends(get_db)):
    """Updates any supplied front, back, or type fields on a card."""

    updates = {field: card[field] for field in ("front", "back", "type") if field in card}
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one of front, back, or type")
    if any(not isinstance(value, str) for value in updates.values()):
        raise HTTPException(status_code=422, detail="Card fields must be strings")

    assignments = ", ".join(f"{field} = ?" for field in updates)
    result = conn.execute(
        f"UPDATE cards SET {assignments} WHERE id = ? AND deck_id = ?",
        (*updates.values(), card_id, deck_id),
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Card not found in this deck")

    conn.commit()
    return {"message": "Card updated successfully"}


@app.post("/api/decks/{deck_id}/cards/{card_id}/review")
def review_card(deck_id: int, card_id: int, review: dict, conn: sql.Connection = Depends(get_db)):
    if type(review.get("correct")) is not bool:
        raise HTTPException(status_code=422, detail="correct must be a boolean")

    row = conn.execute(
        "SELECT correct_count, next_review_date FROM cards WHERE id = ? AND deck_id = ?",
        (card_id, deck_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Card not found in this deck")

    correct = review["correct"]
    correct_count = row[0] + 1 if correct else 0
    incorrect_increment = 0 if correct else 1
    settings = read_deck_review_settings(conn, deck_id)
    if settings["use_review_dates"]:
        today = date.today().isoformat()
        if row[1] is not None and row[1] > today:
            raise HTTPException(status_code=409, detail="Card is not due for review")
        conn.execute(
            """UPDATE app_settings
               SET review_count_date = ?,
                   reviews_today = CASE WHEN review_count_date = ? THEN reviews_today + 1 ELSE 1 END
               WHERE id = 1""",
            (today, today),
        )
        conn.execute(
            """UPDATE decks
               SET review_count_date = ?,
                   reviews_today = CASE WHEN review_count_date = ? THEN reviews_today + 1 ELSE 1 END
               WHERE id = ?""",
            (today, today, deck_id),
        )
        interval_days = (
            settings["review_interval_days"]
            if correct and settings["review_interval_days"] is not None
            else min(2 ** (correct_count - 1), 30) if correct else 1
        )
        next_review_date = (date.today() + timedelta(days=interval_days)).isoformat()
        conn.execute(
            """UPDATE cards
               SET correct_count = ?, incorrect_count = incorrect_count + ?, next_review_date = ?
               WHERE id = ? AND deck_id = ?""",
            (correct_count, incorrect_increment, next_review_date, card_id, deck_id),
        )
    else:
        conn.execute(
            """UPDATE cards
               SET correct_count = ?, incorrect_count = incorrect_count + ?
               WHERE id = ? AND deck_id = ?""",
            (correct_count, incorrect_increment, card_id, deck_id),
        )
        next_review_date = conn.execute(
            "SELECT next_review_date FROM cards WHERE id = ?", (card_id,)
        ).fetchone()[0]

    conn.commit()
    updated_settings = read_review_settings(conn)
    return {
        "correct_count": correct_count,
        "incorrect_count": conn.execute(
            "SELECT incorrect_count FROM cards WHERE id = ?", (card_id,)
        ).fetchone()[0],
        "next_review_date": next_review_date,
        **updated_settings,
        "deck_settings": read_deck_review_settings(conn, deck_id),
    }


@app.delete("/api/decks/{deck_id}/cards/{card_id}")
def delete_card(deck_id: int, card_id: int, conn: sql.Connection = Depends(get_db)):
    result = conn.execute(
        "DELETE FROM cards WHERE id = ? AND deck_id = ?",
        (card_id, deck_id),
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Card not found in this deck")
    conn.commit()
    return {"message": "Card deleted successfully"}