"""
Simple Streamlit "click to run" app for the Website Monitor Agent.
Reads URLs from urllist.txt and adds a Download results button.
"""

import streamlit as st
from datetime import datetime
from agent import run_monitor, log_results

st.set_page_config(
    page_title="Website Monitor Agent",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Website Landing Page Monitor")

# Read URLs from the text file
url_file = "/mount/src/website-monitor-agent/urllist.txt"
lines = []

try:
    with open(url_file, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line:
                lines.append(line)
except FileNotFoundError:
    st.error(f"Could not find URL file: {url_file}")
    st.stop()

if not lines:
    st.warning("The URL file is empty.")
    st.stop()

# Build one query from all URLs in the file
query = (
    "Please check the landing pages of these websites and report any issues "
    "(blank pages, HTTP errors, missing titles, timeouts, etc.). "
    "List each site and clearly mark which ones have problems:\n\n"
    + "\n".join(lines)
)

st.write("Checking these sites:")
st.code("\n".join(lines))

# Only run the agent once per session so Download does not re-check everything
if "last_output" not in st.session_state:
    with st.spinner("Agent is checking the sites… this may take a moment"):
        try:
            output = run_monitor(query)
            log_path = log_results(query, output)

            st.session_state["last_output"] = output
            st.session_state["last_query"] = "\n".join(lines)
            st.session_state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state["log_path"] = str(log_path)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.exception(e)
            st.stop()

st.success("Check complete!")
st.subheader("Results")
st.markdown(st.session_state["last_output"])
st.info(f"📄 Results also written to log file:\n`{st.session_state.get('log_path', '')}`")

# Download button
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
st.caption(
    "Built with the OpenAI Agents SDK + BeautifulSoup. "
    "Requires OPENAI_API_KEY in your environment or .env file."
)
