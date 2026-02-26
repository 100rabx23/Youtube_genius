## Overview
This repository contains a FastAPI backend for an AI-powered quiz application using Google's Gemini model. The app exposes endpoints for generating and grading quizzes based on YouTube video transcripts and providing analytics about user performance.

## Features
- Generate MCQ quizzes (5 questions each) by passing video transcripts to Gemini-2.5-Flash.
- Regenerate quizzes for the same video on demand.
- Save quiz results (score, total) to the database.
- Dashboard with statistics, topic-wise analytics, and score trend.
- CORS enabled for frontend integration.

## Requirements
- Python 3.8+
- FastAPI
- pydantic
- google's genai module
- Any supported DB module (see `database.py`)
- Uvicorn (for running the server)

## Environment
- Requires a valid Google Gemini API key (`GEMINI_API_KEY` environment variable).

## How to Run
1. Clone this repository
2. Install dependencies (pip install -r requirements.txt)
3. Set up environment variable: `export GEMINI_API_KEY=your_key_here`
4. Start the server: `uvicorn main:app --reload`

## API Endpoints
- `POST /process` : Generate a quiz from a video transcript. Returns topic and 5 MCQs.
- `POST /submit` : Submit quiz results. Body: `{ video_id, score, total }`
- `GET /dashboard` : Get usage and score summary.
- `GET /history` : Get quiz attempt history.
- `GET /analytics` : Get topic-wise performance.
- `GET /trend` : Get score trends over time.

## File Structure
- `main.py` : Main FastAPI app
- `database.py` : DB utilities and models (not shown in snippet)

## Notes
- This app only contains the backend logic; you'll need a frontend and a valid DB.
- Quiz logic expects Gemini's model to respond in strict JSON format.
- Ensure you have valid DB functions implemented in `database.py` as expected by the app.

---
Feel free to contribute or raise issues if you have suggestions!
