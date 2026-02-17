import streamlit as st
import sys
import requests

requests.get("https://youtube-genius-backend.onrender.com/dashboard")


st.title("📂 Quiz History")

history = get_history()

if history:
    for row in history:
        video_id, topic, score, total, date = row
        st.markdown(f"""
        ### 🎥 {video_id}
        **Topic:** {topic}  
        **Score:** {score}/{total}  
        **Date:** {date}
        """)
        st.markdown("---")
else:
    st.info("No quiz history yet.")
