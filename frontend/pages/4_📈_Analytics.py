import streamlit as st
import sys
import pandas as pd

sys.path.append("../backend")
from database import get_topic_performance

st.title("📈 Topic Performance")

data = get_topic_performance()

if data:
    df = pd.DataFrame(data, columns=["Topic", "Average Score"])

    st.bar_chart(df.set_index("Topic"))

    sorted_df = df.sort_values("Average Score")

    weakest = sorted_df.iloc[0]
    strongest = sorted_df.iloc[-1]

    st.markdown("## 🎯 Performance Insights")

    st.error(f"📉 Weakest Topic: {weakest['Topic']} ({round(weakest['Average Score'],2)})")
    st.success(f"📈 Strongest Topic: {strongest['Topic']} ({round(strongest['Average Score'],2)})")

else:
    st.info("Not enough data yet. Complete quizzes to unlock analytics.")
