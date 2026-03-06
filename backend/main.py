from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import uuid
from datetime import datetime

app = FastAPI(title="Academy Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 후 프론트엔드 URL로 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "academy.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT '#7c6af7',
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            academy TEXT,
            content TEXT NOT NULL,
            score TEXT,
            hw_done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)
    # 기본 과목 추가
    defaults = [
        ("수학", "#7c6af7"),
        ("영어", "#f76a8a"),
        ("과학", "#6af7c8"),
        ("국어", "#f7c46a"),
    ]
    for name, color in defaults:
        exists = c.execute("SELECT id FROM subjects WHERE name=?", (name,)).fetchone()
        if not exists:
            c.execute(
                "INSERT INTO subjects (id, name, color, created_at) VALUES (?,?,?,?)",
                (str(uuid.uuid4()), name, color, datetime.now().isoformat())
            )
    conn.commit()
    conn.close()

init_db()

# ── Models ──────────────────────────────────────────
class SubjectCreate(BaseModel):
    name: str
    color: str = "#7c6af7"

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class MessageCreate(BaseModel):
    subject_id: str
    date: str
    academy: Optional[str] = None
    content: str
    score: Optional[str] = None

class MessageUpdate(BaseModel):
    hw_done: Optional[bool] = None
    content: Optional[str] = None
    score: Optional[str] = None
    academy: Optional[str] = None

# ── Subjects ─────────────────────────────────────────
@app.get("/subjects")
def list_subjects():
    conn = get_db()
    rows = conn.execute("SELECT * FROM subjects ORDER BY created_at").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/subjects", status_code=201)
def create_subject(body: SubjectCreate):
    conn = get_db()
    sid = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO subjects (id, name, color, created_at) VALUES (?,?,?,?)",
        (sid, body.name, body.color, datetime.now().isoformat())
    )
    conn.commit()
    row = conn.execute("SELECT * FROM subjects WHERE id=?", (sid,)).fetchone()
    conn.close()
    return dict(row)

@app.put("/subjects/{sid}")
def update_subject(sid: str, body: SubjectUpdate):
    conn = get_db()
    subj = conn.execute("SELECT * FROM subjects WHERE id=?", (sid,)).fetchone()
    if not subj:
        raise HTTPException(404, "Subject not found")
    name = body.name if body.name is not None else subj["name"]
    color = body.color if body.color is not None else subj["color"]
    conn.execute("UPDATE subjects SET name=?, color=? WHERE id=?", (name, color, sid))
    conn.commit()
    row = conn.execute("SELECT * FROM subjects WHERE id=?", (sid,)).fetchone()
    conn.close()
    return dict(row)

@app.delete("/subjects/{sid}", status_code=204)
def delete_subject(sid: str):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE subject_id=?", (sid,))
    conn.execute("DELETE FROM subjects WHERE id=?", (sid,))
    conn.commit()
    conn.close()

# ── Messages ─────────────────────────────────────────
@app.get("/messages")
def list_messages(subject_id: Optional[str] = None):
    conn = get_db()
    if subject_id:
        rows = conn.execute(
            "SELECT m.*, s.name as subject_name, s.color as subject_color "
            "FROM messages m JOIN subjects s ON m.subject_id=s.id "
            "WHERE m.subject_id=? ORDER BY m.date DESC, m.time DESC",
            (subject_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT m.*, s.name as subject_name, s.color as subject_color "
            "FROM messages m JOIN subjects s ON m.subject_id=s.id "
            "ORDER BY m.date DESC, m.time DESC"
        ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["hw_done"] = bool(d["hw_done"])
        result.append(d)
    return result

@app.post("/messages", status_code=201)
def create_message(body: MessageCreate):
    conn = get_db()
    subj = conn.execute("SELECT * FROM subjects WHERE id=?", (body.subject_id,)).fetchone()
    if not subj:
        raise HTTPException(404, "Subject not found")
    mid = str(uuid.uuid4())
    now = datetime.now()
    conn.execute(
        "INSERT INTO messages (id, subject_id, date, time, academy, content, score, hw_done, created_at) "
        "VALUES (?,?,?,?,?,?,?,0,?)",
        (mid, body.subject_id, body.date, now.strftime("%H:%M"),
         body.academy, body.content, body.score, now.isoformat())
    )
    conn.commit()
    row = conn.execute(
        "SELECT m.*, s.name as subject_name, s.color as subject_color "
        "FROM messages m JOIN subjects s ON m.subject_id=s.id WHERE m.id=?", (mid,)
    ).fetchone()
    conn.close()
    d = dict(row)
    d["hw_done"] = bool(d["hw_done"])
    return d

@app.patch("/messages/{mid}")
def update_message(mid: str, body: MessageUpdate):
    conn = get_db()
    msg = conn.execute("SELECT * FROM messages WHERE id=?", (mid,)).fetchone()
    if not msg:
        raise HTTPException(404, "Message not found")
    hw_done = int(body.hw_done) if body.hw_done is not None else msg["hw_done"]
    content = body.content if body.content is not None else msg["content"]
    score = body.score if body.score is not None else msg["score"]
    academy = body.academy if body.academy is not None else msg["academy"]
    conn.execute(
        "UPDATE messages SET hw_done=?, content=?, score=?, academy=? WHERE id=?",
        (hw_done, content, score, academy, mid)
    )
    conn.commit()
    row = conn.execute(
        "SELECT m.*, s.name as subject_name, s.color as subject_color "
        "FROM messages m JOIN subjects s ON m.subject_id=s.id WHERE m.id=?", (mid,)
    ).fetchone()
    conn.close()
    d = dict(row)
    d["hw_done"] = bool(d["hw_done"])
    return d

@app.delete("/messages/{mid}", status_code=204)
def delete_message(mid: str):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE id=?", (mid,))
    conn.commit()
    conn.close()

@app.get("/health")
def health():
    return {"status": "ok"}
