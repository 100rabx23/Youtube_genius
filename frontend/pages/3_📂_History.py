import streamlit as st
import sys
sys.path.append("../backend")

from database import get_history

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
