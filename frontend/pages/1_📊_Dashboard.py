import streamlit as st
import requests
import pandas as pd

API = "https://youtube-genius-backend.onrender.com"

st.title("📊 Learning Overview")

# ---------------- DASHBOARD METRICS ----------------
try:
    response = requests.get(f"{API}/dashboard")
    data = response.json()

    total_videos = data.get("total_videos", 0)
    total_quizzes = data.get("total_quizzes", 0)
    avg_score = data.get("avg_score", 0)
    best_score = data.get("best_score", 0)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Videos Processed", total_videos)
    col2.metric("Quizzes Taken", total_quizzes)
    col3.metric("Average Score", avg_score)
    col4.metric("Best Score", best_score)

except Exception as e:
    st.error("Backend not reachable")
    st.stop()


st.markdown("---")

# ---------------- SCORE TREND ----------------
try:
    trend_response = requests.get(f"{API}/trend")
    trend_data = trend_response.json()

    if trend_data:
        df = pd.DataFrame(trend_data, columns=["Date", "Score"])
        st.subheader("📈 Score Trend Over Time")
        st.line_chart(df.set_index("Date"))
    else:
        st.info("Complete quizzes to see performance trend.")

except:
    st.warning("Trend data unavailable")
