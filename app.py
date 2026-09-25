"""
Simple Streamlit "click to run" app for the Website Monitor Agent.
"""

import os
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Website Monitor Agent",
    page_icon="🔍",
    layout="centered",
)

# -------------------------------------------------
# Load the OpenAI key before importing the agent
# -------------------------------------------------
api_key = None
try:
    api_key = st.secrets.get("OPENAI_API_KEY")
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    try:
        from agents import set_default_openai_key
        set_default_openai_key(api_key)
    except Exception:
        pass
else:
    st.error("No OpenAI API key found. Add it in Streamlit Secrets.")
    st.stop()

from agent import run_monitor

st.title("🔍 Website Landing Page Monitor")
st.markdown(
    "Enter one or more websites (one per line or comma-separated). "
    "The AI agent will check each landing page for blank content, errors, "
    "missing titles, slow responses, and other issues."
)

default_sites = """highcalgames.com
python.org
highcalharding.com
zonestalkers.com
"""

sites_input = st.text_area(
    "Websites to check",
    value=default_sites,
    height=180,
    help="One URL per line or separated by commas. https:// is optional.",
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
                st.session_state["last_output"] = output
                st.session_state["last_query"] = sites_input.strip()
                st.session_state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.exception(e)

# Show results + download button if a report exists
if "last_output" in st.session_state:
    st.success("Check complete!")
    st.subheader("Results")
    st.markdown(st.session_state["last_output"])

    report_text = (
        "Website Landing Page Monitor Report\n"
        f"Run time: {st.session_state.get('last_run', '')}\n"
        "Checked sites:\n"
        f"{st.session_state.get('last_query', '')}\n"
        + ("-" * 40) + "\n"
        + st.session_state["last_output"]
        + "\n"
    )

    filename = f"website_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    st.download_button(
        label="⬇️ Download results",
        data=report_text,
        file_name=filename,
        mime="text/plain",
    )

st.divider()
st.caption("Built with the OpenAI Agents SDK + BeautifulSoup. App v1.01, 09-25-26 1832")
