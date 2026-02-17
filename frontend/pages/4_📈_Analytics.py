import streamlit as st
import requests
import pandas as pd

API = "https://youtube-genius-backend.onrender.com"

st.title("📈 Topic Performance")

try:
    response = requests.get(f"{API}/analytics")
    data = response.json()

    if data:
        df = pd.DataFrame(data, columns=["Topic", "Average Score"])

        st.bar_chart(df.set_index("Topic"))

        sorted_df = df.sort_values("Average Score")

        weakest = sorted_df.iloc[0]
        strongest = sorted_df.iloc[-1]

        st.markdown("## 🎯 Performance Insights")

        st.error(
            f"📉 Weakest Topic: {weakest['Topic']} "
            f"({round(weakest['Average Score'],2)})"
        )

        st.success(
            f"📈 Strongest Topic: {strongest['Topic']} "
            f"({round(strongest['Average Score'],2)})"
        )

    else:
        st.info("Not enough data yet. Complete quizzes to unlock analytics.")

except Exception as e:
    st.error("Backend not reachable")
