"""
Simple Streamlit "click to run" app for the Website Monitor Agent.
"""

import os
import streamlit as st

# -------------------------------------------------
# 1. Load the OpenAI key as early as possible
# -------------------------------------------------
def load_openai_key():
    """Load OpenAI API key from Streamlit secrets or .env file"""
    
    key = None
    source = None
    
    # First try Streamlit secrets (for Community Cloud)
    try:
        if "OPENAI_API_KEY" in st.secrets:
            key = st.secrets["OPENAI_API_KEY"]
            source = "Streamlit Secrets"
    except Exception as e:
        pass
    
    # Fallback to environment variable / .env file
    if not key:
        from dotenv import load_dotenv
        load_dotenv()
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            source = "Environment / .env file"
    
    return key, source


# Load the key immediately
api_key, key_source = load_openai_key()

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    # Also set it the way the Agents SDK likes
    try:
        from agents import set_default_openai_key
        set_default_openai_key(api_key)
    except Exception:
        pass
else:
    st.error("❌ No OpenAI API Key found!")
    st.stop()

# -------------------------------------------------
# 2. Now import the agent (after the key is set)
# -------------------------------------------------
from agent import run_monitor, log_results

st.set_page_config(
    page_title="Website Monitor Agent",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Website Landing Page Monitor")
st.markdown(
    "Enter one or more websites (one per line or comma-separated). "
    "The AI agent will check each landing page for blank content, errors, "
    "missing titles, slow responses, and other issues."
)

# Show key status (first 20 characters only for security)
masked_key = api_key[:20] + "..." if api_key and len(api_key) > 20 else "Not found"
st.caption(f"🔑 API Key loaded from: **{key_source}** | Starts with: `{masked_key}`")

# Default example sites
default_sites = """python.org
github.com
openai.com
https://httpstat.us/404
https://httpstat.us/500
example.com
"""

sites_input = st.text_area(
    "Websites to check",
    value=default_sites,
    height=180,
    help="One URL per line or separated by commas. https:// is optional.",
)

col1, col2 = st.columns([1, 3])
with col1:
    run_button = st.button("▶ Run Check", type="primary", use_container_width=True)

if run_button:
    if not sites_input.strip():
        st.warning("Please enter at least one website.")
    else:
        query = (
            "Please check the landing pages of these websites and report any issues "
            "(blank pages, HTTP errors, missing titles, timeouts, etc.). "
            "List each site and clearly mark which ones have problems:\n\n"
            + sites_input.strip()
        )

        with st.spinner("Agent is checking the sites… this may take a moment"):
            try:
                output = run_monitor(query)
                log_path = log_results(query, output)

                st.success("Check complete!")
                st.subheader("Results")
                st.markdown(output)

                st.info(f"📄 Results also written to log file:\n`{log_path}`")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.exception(e)

st.divider()
st.caption(
    "Built with the OpenAI Agents SDK + BeautifulSoup. "
    "Requires OPENAI_API_KEY in your environment or .env file. v1.02, 09-25-26 0927"
)
