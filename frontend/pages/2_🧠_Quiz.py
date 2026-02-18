import streamlit as st
import requests
import time
from youtube_transcript_api import YouTubeTranscriptApi

API = "https://youtube-genius-backend.onrender.com"
PROCESS_URL = f"{API}/process"
SUBMIT_URL = f"{API}/submit"

st.title("🧠 Interactive Quiz")

url = st.session_state.get("global_url", "")

# ---------------- Video Preview ----------------
if url:
    video_id = url.split("v=")[-1].split("&")[0]
    st.video(f"https://www.youtube.com/watch?v={video_id}")

# ---------------- Session State ----------------
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answered" not in st.session_state:
    st.session_state.answered = False


# ---------------- Transcript Fetch ----------------
def fetch_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            transcript = next(iter(transcript_list))

        snippets = transcript.fetch()

        transcript_text = " ".join(
            s["text"] if isinstance(s, dict) else s.text
            for s in snippets
        )

        return transcript_text

    except Exception:
        st.error("Could not fetch transcript. Video may not have captions.")
        return None


# ---------------- Fetch Quiz ----------------
def fetch_quiz(regenerate=False):
    video_id = url.split("v=")[-1].split("&")[0]

    transcript_text = fetch_transcript(video_id)

    if not transcript_text:
        return {}

    response = requests.post(
        PROCESS_URL,
        json={
            "video_id": video_id,
            "transcript": transcript_text,
            "regenerate": regenerate
        },
        timeout=120
    )

    return response.json()


# ---------------- Generate Quiz ----------------
if st.button("Generate Quiz 🚀"):
    if not url:
        st.warning("Enter YouTube URL in sidebar")
    else:
        with st.spinner("Generating quiz..."):
            progress = st.progress(0)
            for i in range(0, 90, 10):
                time.sleep(0.05)
                progress.progress(i)

            data = fetch_quiz()
            progress.progress(100)

        if "quiz" in data:
            st.session_state.quiz_data = data["quiz"]
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.rerun()
        else:
            st.error(data)


# ---------------- Quiz Logic ----------------
if st.session_state.quiz_data:
    quiz = st.session_state.quiz_data
    total = len(quiz)
    q_index = st.session_state.current_q

    if q_index < total:
        q = quiz[q_index]

        st.markdown(f"### Question {q_index+1} / {total}")
        st.write(q["question"])

        selected = st.radio(
            "Select answer:",
            q["options"],
            key=f"radio_{q_index}",
            disabled=st.session_state.answered
        )

        if not st.session_state.answered:
            if st.button("Submit"):
                correct_letter = q["answer"].strip()[0].lower()
                selected_letter = selected.strip()[0].lower()

                st.session_state.answered = True

                if selected_letter == correct_letter:
                    st.success("Correct ✅")
                    st.session_state.score += 1
                else:
                    st.error("Incorrect ❌")
                    st.info(f"Correct Answer: {q['answer']}")

                st.markdown("### Explanation")
                st.write(q["explanation"])

        if st.session_state.answered:
            if st.button("Next ➡"):
                st.session_state.current_q += 1
                st.session_state.answered = False
                st.rerun()

    else:
        percentage = int((st.session_state.score / total) * 100)

        st.success(f"Final Score: {st.session_state.score}/{total} ({percentage}%)")

        video_id = url.split("v=")[-1].split("&")[0]

        try:
            requests.post(
                SUBMIT_URL,
                json={
                    "video_id": video_id,
                    "score": st.session_state.score,
                    "total": total
                }
            )
        except:
            st.warning("Could not save result to server.")

        if percentage >= 80:
            st.info("🔥 Strong understanding of the topic.")
        elif percentage >= 50:
            st.warning("⚡ Moderate understanding. Some concepts need review.")
        else:
            st.error("📚 Weak grasp. Revisit the video and retry.")

        if st.button("Generate New Questions 🔄"):
            data = fetch_quiz(regenerate=True)

            if "quiz" in data:
                st.session_state.quiz_data = data["quiz"]
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.rerun()
