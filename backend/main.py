import os
import json
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from dotenv import load_dotenv
from database import init_db, save_video

# ---------------- ENV ----------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class VideoRequest(BaseModel):
    url: str
    regenerate: bool = False


def extract_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url


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
      "options": ["A", "B", "C", "D"],
      "answer": "",
      "explanation": ""
    }}
  ]
}}

Generate 5 MCQs.

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
