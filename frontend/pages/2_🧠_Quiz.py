import streamlit as st
import requests
import sys
import time

sys.path.append("../backend")
from database import save_quiz_attempt

BACKEND_URL = "https://youtube-genius-backend.onrender.com/process"

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


def fetch_quiz(regenerate=False):
    return requests.post(
        BACKEND_URL,
        json={"url": url, "regenerate": regenerate},
        timeout=120
    ).json()


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
                with st.spinner("Checking answer..."):
                    correct = q["answer"].strip().lower()
                    selected_norm = selected.strip().lower()

                    if len(correct) == 1:
                        is_correct = selected_norm.startswith(correct)
                    else:
                        is_correct = selected_norm == correct

                    st.session_state.answered = True

                    if is_correct:
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

    # ---------------- Final Result ----------------
    else:
        percentage = int((st.session_state.score / total) * 100)

        st.success(f"Final Score: {st.session_state.score}/{total} ({percentage}%)")

        # Save attempt correctly
        video_id = url.split("v=")[-1].split("&")[0]
        save_quiz_attempt(video_id, st.session_state.score, total)

        # Performance Feedback
        if percentage >= 80:
            st.info("🔥 Strong understanding of the topic.")
        elif percentage >= 50:
            st.warning("⚡ Moderate understanding. Some concepts need review.")
        else:
            st.error("📚 Weak grasp. Revisit the video and retry.")

        # AI Insight Block (NOW CORRECTLY INSIDE)
        st.markdown("## 🤖 AI Learning Insight")

        if percentage < 50:
            st.write("You should revisit foundational concepts and attempt similar quizzes.")
        elif percentage < 80:
            st.write("Focus on understanding explanations deeply for better retention.")
        else:
            st.write("Great performance. Try more advanced topics to level up.")

        if st.button("Generate New Questions 🔄"):
            with st.spinner("Generating new questions..."):
                data = fetch_quiz(regenerate=True)

            if "quiz" in data:
                st.session_state.quiz_data = data["quiz"]
                st.session_state.current_q = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.rerun()
