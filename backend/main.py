from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, uuid
from datetime import datetime

app = FastAPI(title="Academy Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB 연결: PostgreSQL(Railway) 또는 SQLite(로컬) 자동 선택 ──
DATABASE_URL = os.environ.get("DATABASE_URL")  # Railway PostgreSQL 환경변수

if DATABASE_URL:
    # PostgreSQL
    import psycopg2
    import psycopg2.extras

    def get_db():
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    def rowdict(cursor, rows):
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in rows]

    def init_db():
        conn = get_db()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#4B9EF8',
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
                created_at TEXT NOT NULL
            )
        """)
        defaults = [("수학","#4B9EF8"),("영어","#F87171"),("과학","#34D399"),("국어","#FBBF24")]
        for name, color in defaults:
            c.execute("SELECT id FROM subjects WHERE name=%s", (name,))
            if not c.fetchone():
                c.execute("INSERT INTO subjects (id,name,color,created_at) VALUES (%s,%s,%s,%s)",
                          (str(uuid.uuid4()), name, color, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    PH = "%s"  # PostgreSQL placeholder

else:
    # SQLite (로컬 개발용)
    import sqlite3

    def get_db():
        conn = sqlite3.connect("academy.db")
        conn.row_factory = sqlite3.Row
        return conn

    def rowdict(cursor, rows):
        return [dict(r) for r in rows]

    def init_db():
        conn = get_db()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY, name TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT '#4B9EF8', created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, subject_id TEXT NOT NULL,
            date TEXT NOT NULL, time TEXT NOT NULL, academy TEXT,
            content TEXT NOT NULL, score TEXT,
            hw_done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL)""")
        defaults = [("수학","#4B9EF8"),("영어","#F87171"),("과학","#34D399"),("국어","#FBBF24")]
        for name, color in defaults:
            if not c.execute("SELECT id FROM subjects WHERE name=?", (name,)).fetchone():
                c.execute("INSERT INTO subjects (id,name,color,created_at) VALUES (?,?,?,?)",
                          (str(uuid.uuid4()), name, color, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    PH = "?"  # SQLite placeholder

init_db()

# ── Models ──
class SubjectCreate(BaseModel):
    name: str
    color: str = "#4B9EF8"

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

def q(sql):
    """SQLite ? → PostgreSQL %s 자동 변환"""
    if PH == "%s":
        return sql.replace("?", "%s")
    return sql

# ── Subjects ──
@app.get("/subjects")
def list_subjects():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM subjects ORDER BY created_at")
    rows = c.fetchall()
    conn.close()
    return rowdict(c, rows)

@app.post("/subjects", status_code=201)
def create_subject(body: SubjectCreate):
    conn = get_db(); c = conn.cursor()
    sid = str(uuid.uuid4())
    c.execute(q("INSERT INTO subjects (id,name,color,created_at) VALUES (?,?,?,?)"),
              (sid, body.name, body.color, datetime.now().isoformat()))
    conn.commit()
    c.execute(q("SELECT * FROM subjects WHERE id=?"), (sid,))
    row = c.fetchall(); conn.close()
    return rowdict(c, row)[0]

@app.put("/subjects/{sid}")
def update_subject(sid: str, body: SubjectUpdate):
    conn = get_db(); c = conn.cursor()
    c.execute(q("SELECT * FROM subjects WHERE id=?"), (sid,))
    rows = c.fetchall()
    if not rows: raise HTTPException(404, "Not found")
    subj = rowdict(c, rows)[0]
    name = body.name if body.name is not None else subj["name"]
    color = body.color if body.color is not None else subj["color"]
    c.execute(q("UPDATE subjects SET name=?,color=? WHERE id=?"), (name, color, sid))
    conn.commit()
    c.execute(q("SELECT * FROM subjects WHERE id=?"), (sid,))
    row = c.fetchall(); conn.close()
    return rowdict(c, row)[0]

@app.delete("/subjects/{sid}", status_code=204)
def delete_subject(sid: str):
    conn = get_db(); c = conn.cursor()
    c.execute(q("DELETE FROM messages WHERE subject_id=?"), (sid,))
    c.execute(q("DELETE FROM subjects WHERE id=?"), (sid,))
    conn.commit(); conn.close()

# ── Messages ──
@app.get("/messages")
def list_messages(subject_id: Optional[str] = None):
    conn = get_db(); c = conn.cursor()
    if subject_id:
        c.execute(q(
            "SELECT m.*,s.name as subject_name,s.color as subject_color "
            "FROM messages m JOIN subjects s ON m.subject_id=s.id "
            "WHERE m.subject_id=? ORDER BY m.date DESC,m.time DESC"), (subject_id,))
    else:
        c.execute(
            "SELECT m.*,s.name as subject_name,s.color as subject_color "
            "FROM messages m JOIN subjects s ON m.subject_id=s.id "
            "ORDER BY m.date DESC,m.time DESC")
    rows = c.fetchall()
    conn.close()
    result = rowdict(c, rows)
    for r in result:
        r["hw_done"] = bool(r["hw_done"])
    return result

@app.post("/messages", status_code=201)
def create_message(body: MessageCreate):
    conn = get_db(); c = conn.cursor()
    c.execute(q("SELECT id FROM subjects WHERE id=?"), (body.subject_id,))
    if not c.fetchone(): raise HTTPException(404, "Subject not found")
    mid = str(uuid.uuid4())
    now = datetime.now()
    c.execute(q("INSERT INTO messages (id,subject_id,date,time,academy,content,score,hw_done,created_at) "
                "VALUES (?,?,?,?,?,?,?,0,?)"),
              (mid, body.subject_id, body.date, now.strftime("%H:%M"),
               body.academy, body.content, body.score, now.isoformat()))
    conn.commit()
    c.execute(q("SELECT m.*,s.name as subject_name,s.color as subject_color "
                "FROM messages m JOIN subjects s ON m.subject_id=s.id WHERE m.id=?"), (mid,))
    row = c.fetchall(); conn.close()
    r = rowdict(c, row)[0]; r["hw_done"] = bool(r["hw_done"]); return r

@app.patch("/messages/{mid}")
def update_message(mid: str, body: MessageUpdate):
    conn = get_db(); c = conn.cursor()
    c.execute(q("SELECT * FROM messages WHERE id=?"), (mid,))
    rows = c.fetchall()
    if not rows: raise HTTPException(404, "Not found")
    msg = rowdict(c, rows)[0]
    hw_done = int(body.hw_done) if body.hw_done is not None else msg["hw_done"]
    content = body.content if body.content is not None else msg["content"]
    score = body.score if body.score is not None else msg["score"]
    academy = body.academy if body.academy is not None else msg["academy"]
    c.execute(q("UPDATE messages SET hw_done=?,content=?,score=?,academy=? WHERE id=?"),
              (hw_done, content, score, academy, mid))
    conn.commit()
    c.execute(q("SELECT m.*,s.name as subject_name,s.color as subject_color "
                "FROM messages m JOIN subjects s ON m.subject_id=s.id WHERE m.id=?"), (mid,))
    row = c.fetchall(); conn.close()
    r = rowdict(c, row)[0]; r["hw_done"] = bool(r["hw_done"]); return r

@app.delete("/messages/{mid}", status_code=204)
def delete_message(mid: str):
    conn = get_db(); c = conn.cursor()
    c.execute(q("DELETE FROM messages WHERE id=?"), (mid,))
    conn.commit(); conn.close()

@app.get("/health")
def health():
    return {"status": "ok", "db": "postgresql" if DATABASE_URL else "sqlite"}
