import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "database.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        topic TEXT,
        processed_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT,
        score INTEGER,
        total INTEGER,
        attempted_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- SAVE ----------------

def save_video(video_id, topic):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO videos (video_id, topic, processed_at) VALUES (?, ?, ?)",
        (video_id, topic, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()


def save_quiz_attempt(video_id, score, total):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO quiz_attempts (video_id, score, total, attempted_at) VALUES (?, ?, ?, ?)",
        (video_id, score, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()


# ---------------- DASHBOARD ----------------

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM videos")
    total_videos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), AVG(score), MAX(score) FROM quiz_attempts")
    result = cursor.fetchone()

    total_quizzes = result[0] if result[0] else 0
    avg_score = round(result[1], 2) if result[1] else 0
    best_score = result[2] if result[2] else 0

    conn.close()
    return total_videos, total_quizzes, avg_score, best_score


# ---------------- HISTORY ----------------

def get_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT v.video_id, v.topic, q.score, q.total, q.attempted_at
    FROM quiz_attempts q
    JOIN videos v ON v.video_id = q.video_id
    ORDER BY q.attempted_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


# ---------------- ANALYTICS ----------------

def get_topic_performance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT v.topic, AVG(q.score)
    FROM quiz_attempts q
    JOIN videos v ON v.video_id = q.video_id
    GROUP BY v.topic
    """)

    data = cursor.fetchall()
    conn.close()
    return data


#addind to redefin 

def get_score_trend():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT attempted_at, score
    FROM quiz_attempts
    ORDER BY attempted_at ASC
    """)

    data = cursor.fetchall()
    conn.close()
    return data
