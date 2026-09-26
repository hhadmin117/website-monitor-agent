"""
Simple Streamlit "click to run" app for the Website Monitor Agent.
"""

import streamlit as st
from agent import run_monitor, log_results

st.set_page_config(
    page_title="Website Monitor Agent",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Website Landing Page Monitor")
#st.markdown(
#    "Enter one or more websites (one per line or comma-separated). "
#    "The AI agent will check each landing page for blank content, errors, "
#    "missing titles, slow responses, and other issues."
#)

# Default example sites
# Replace the textbox URL list with a text file.  This way, there are no prompts and can be run once a day without intervention.

default_sites = """
costco.com
"""
lines = []

with open("/mount/src/website-monitor-agent/urllist.txt", "r", encoding="utf-8") as f:
    line = f.readline()          # reads one line
    if line:                     # skip if the file is empty
        lines.append(line.strip())

#sites_input = st.text_area(
#    "Websites to check",
    #value=default_sites,
#    value=lines,
#    height=180,
#    help="One URL per line or separated by commas. https:// is optional.",
#)

#col1, col2 = st.columns([1, 3])
#with col1:
#    run_button = st.button("▶ Run Check", type="primary", use_container_width=True)

i=0
#if run_button:
#    if not sites_input.strip():
#        st.warning("Please enter at least one website.")
#    else:
        # Build a clear query for the agent
query = (
    "Please check the landing pages of these websites and report any issues "
    "(blank pages, HTTP errors, missing titles, timeouts, etc.). "
    "List each site and clearly mark which ones have problems:\n\n"
    + lines[i]
)
i = i + 1
st.warning(query)
        
# + sites_input.strip()
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
    "Requires OPENAI_API_KEY in your environment or .env file."
)
