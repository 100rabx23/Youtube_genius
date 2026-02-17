import streamlit as st
import sys
import pandas as pd

requests.get("https://youtube-genius-backend.onrender.com/dashboard")

st.title("📊 Learning Overview")

total_videos, total_quizzes, avg_score, best_score = get_dashboard_stats()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Videos Processed", total_videos)
col2.metric("Quizzes Taken", total_quizzes)
col3.metric("Average Score", avg_score)
col4.metric("Best Score", best_score)

st.markdown("---")

trend_data = get_score_trend()

if trend_data:
    df = pd.DataFrame(trend_data, columns=["Date", "Score"])
    st.subheader("📈 Score Trend Over Time")
    st.line_chart(df.set_index("Date"))
else:
    st.info("Complete quizzes to see performance trend.")
