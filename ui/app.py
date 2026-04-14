import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="GitHub Code Mentor", 
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #00d4ff;
        color: #00d4ff;
    }
    .metric-card {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2d2f39;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("ui/hero.png", width=300) # Replaced use_container_width with width='stretch' equivalent or fixed width
    st.title("Settings & Info")
    st.info("This AI-powered mentor analyzes your GitHub portfolio and provides actionable feedback to help you grow as a developer.")
    
    st.markdown("---")
    st.subheader("Example Users")
    if st.button("torvalds"):
        st.session_state.username = "torvalds"
    if st.button("karpathy"):
        st.session_state.username = "karpathy"
    
    st.markdown("---")
    st.caption("Powered by LangGraph & Llama 3.3")

# --- Main Hero Section ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🚀 Elevate Your GitHub Portfolio")
    st.markdown("""
        Unlock professional insights into your coding journey. Our AI Code Mentor reviews your 
        repositories, identifies your primary stacks, and gives you that extra push toward excellence.
    """)
    
    # Input Area
    if 'username' not in st.session_state:
        st.session_state.username = ""
        
    username = st.text_input(
        "Enter GitHub Username", 
        value=st.session_state.username,
        placeholder="e.g., torvalds",
        key="username_input"
    )
    
    analyze_btn = st.button("Analyze Portfolio", key="analyze_main")

with col2:
    # Small aesthetic touch
    st.image("ui/hero.png", width=300)

# --- Analysis Logic ---
if analyze_btn or (st.session_state.username and username != st.session_state.username):
    if username:
        with st.status(f"🔍 Analyzing {username}'s portfolio...", expanded=True) as status:
            try:
                st.write("Fetching repository data...")
                response = requests.post(f"http://127.0.0.1:8000/review?username={username}")
                
                if response.status_code == 200:
                    data = response.json()
                    status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                    
                    st.divider()
                    
                    # --- Results Dashboard ---
                    tab1, tab2 = st.tabs(["📊 Portfolio Stats", "💡 Mentor Feedback"])
                    
                    with tab1:
                        st.subheader(f"Portfolio Overview: {username}")
                        
                        github_data = data.get("extracted_data", {})
                        if "error" in github_data:
                            st.error(github_data["error"])
                        else:
                            # Metrics Row
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Public Repos", github_data.get("public_repos_count", 0))
                            m2.metric("Primary Languages", len(github_data.get("primary_languages", [])))
                            m3.metric("Top Language", github_data.get("primary_languages", ["None"])[0])
                            
                            st.markdown("#### Recent Activity")
                            repos = github_data.get("recent_repos", [])
                            for repo in repos:
                                st.markdown(f"- 📦 **{repo}**")
                            
                            st.markdown("#### Tech Stack")
                            langs = github_data.get("primary_languages", [])
                            st.info(", ".join(langs) if langs else "No languages detected")

                    with tab2:
                        st.subheader("Mentor's Deep Dive")
                        feedback = data.get("mentor_feedback", "No feedback generated.")
                        st.markdown(feedback)
                        
                        st.success("Tip: Focus on your suggested improvements to boost your portfolio visibility!")
                
                else:
                    status.update(label="❌ Backend Error", state="error")
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                status.update(label="❌ Connection Failed", state="error")
                st.error("Could not connect to the backend server. Make sure it's running!")
    else:
        st.warning("Please enter a username first!")

