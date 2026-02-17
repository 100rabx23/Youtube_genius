import streamlit as st
import requests

API = "https://youtube-genius-backend.onrender.com"

st.title("📂 Quiz History")

try:
    response = requests.get(f"{API}/history")
    history = response.json()

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

except Exception as e:
    st.error("Backend not reachable")
