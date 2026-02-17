import streamlit as st

st.set_page_config(
    page_title="YouTube Genius Pro",
    page_icon="🚀",
    layout="wide"
)

# ---- Custom CSS ----
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.main {
    background-color: #0f172a;
}
h1, h2, h3, h4 {
    color: white;
}
.stMetric {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🎥 Video Input")

if "global_url" not in st.session_state:
    st.session_state.global_url = ""

st.session_state.global_url = st.sidebar.text_input(
    "Paste YouTube URL",
    value=st.session_state.global_url
)

st.sidebar.markdown("---")
st.sidebar.success("AI Learning Dashboard")

st.title("🚀 YouTube Genius Pro")
st.markdown("### Transform Passive Learning into Measurable Progress")
