"""
Simple Streamlit "click to run" app for the Website Monitor Agent.
"""

import os
import streamlit as st

st.set_page_config(
    page_title="Website Monitor Agent",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Website Landing Page Monitor")

# -------------------------------------------------
# Force load the API key
# -------------------------------------------------
st.subheader("🔑 Debug Info")

api_key = None

# Try Streamlit secrets
try:
    st.write("Secrets available:", list(st.secrets.keys()))
    api_key = st.secrets.get("OPENAI_API_KEY")
    if api_key:
        st.success("Found key in st.secrets")
except Exception as e:
    st.warning(f"Could not read st.secrets: {e}")

# Fallback to environment
if not api_key:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        st.success("Found key in environment variable")

if api_key:
    # Force set it for the OpenAI Agents SDK
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Also try the Agents SDK helper
    try:
        from agents import set_default_openai_key
        set_default_openai_key(api_key)
        st.success("Called set_default_openai_key()")
    except Exception as e:
        st.warning(f"set_default_openai_key failed: {e}")
    
    # Show masked key
    masked = api_key[:15] + "..." + api_key[-6:] if len(api_key) > 25 else "???"
    st.code(f"Using key: {masked}")
else:
    st.error("❌ No API key found in secrets or environment")
    st.stop()

# -------------------------------------------------
from agent import run_monitor, log_results

st.markdown(
    "Enter one or more websites (one per line or comma-separated). "
    "The AI agent will check each landing page for blank content, errors, "
    "missing titles, slow responses, and other issues."
)

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
)

if st.button("▶ Run Check", type="primary"):
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
