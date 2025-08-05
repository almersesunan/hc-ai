import streamlit as st

# API URLs
API_BASE_URL = "http://localhost:8000"
API_URL_CANDIDATE = f"{API_BASE_URL}/candidate_analysis/"


st.set_page_config(
    page_title="AI-Powered Human Capital System",
    page_icon="🧑",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("📃 Menu")
    st.button("Home")
    st.button("Candidate Analysis")

    st.markdown("---")
    st.caption("AI-Powered Human Capital System")
    st.caption("© 2025 HCIS \n Sinar Mas Land")

st.title('AI-Powered Human Capital System')
st.markdown("""
    **An AI-Powered Human Capital System represents the next generation of HR technology, \
    moving beyond traditional administrative functions to a strategic, data-driven platform. \
    By leveraging artificial intelligence and machine learning, this system provides unprecedented \
    insights into workforce dynamics, automates complex processes, and empowers leaders to make fairer, \
    faster, and more effective decisions.**
""")