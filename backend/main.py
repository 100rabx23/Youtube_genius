import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai

from database import (
    init_db,
    save_video,
    save_quiz_attempt,
    get_dashboard_stats,
    get_history,
    get_topic_performance,
    get_score_trend
)

# ---------------- INIT ----------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Gemini Client (uses Render ENV variable)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------- MODELS ----------------

class VideoRequest(BaseModel):
    url: str
    regenerate: bool = False


class QuizResult(BaseModel):
    video_id: str
    score: int
    total: int


# ---------------- UTIL ----------------

def extract_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


# ---------------- QUIZ GENERATION ----------------

@app.post("/process")
async def process_video(request: VideoRequest):
    try:
        video_id = extract_video_id(request.url)

        # -------- Transcript --------
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = next(iter(transcript_list))

        snippets = transcript.fetch()

        transcript_text = " ".join(
            s.text if hasattr(s, "text") else s.get("text", "")
            for s in snippets
        )

        regenerate_instruction = (
            "Generate completely NEW different quiz questions."
            if request.regenerate else ""
        )

        prompt = f"""
Return STRICT JSON only.

{{
  "topic": "",
  "quiz": [
    {{
      "question": "",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "",
      "explanation": ""
    }}
  ]
}}

Generate exactly 5 MCQs.

{regenerate_instruction}

Transcript:
{transcript_text[:12000]}
"""

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        match = re.search(r"\{.*\}", response.text, re.DOTALL)

        if not match:
            raise HTTPException(status_code=500, detail="Invalid AI response")

        data = json.loads(match.group(0))

        if "quiz" not in data:
            raise HTTPException(status_code=500, detail="Quiz not generated")

        save_video(video_id, data.get("topic", "General"))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- SAVE QUIZ RESULT ----------------

@app.post("/submit")
def submit_quiz(result: QuizResult):
    try:
        save_quiz_attempt(result.video_id, result.score, result.total)
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- DASHBOARD ----------------

@app.get("/dashboard")
def dashboard():
    total_videos, total_quizzes, avg_score, best_score = get_dashboard_stats()
    return {
        "total_videos": total_videos,
        "total_quizzes": total_quizzes,
        "avg_score": avg_score,
        "best_score": best_score
    }


@app.get("/history")
def history():
    return get_history()


@app.get("/analytics")
def analytics():
    return get_topic_performance()


@app.get("/trend")
def trend():
    return get_score_trend()
