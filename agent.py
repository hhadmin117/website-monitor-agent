"""
Website Monitor Agent using the OpenAI Agents SDK.
"""

import os
from datetime import datetime
from pathlib import Path

from agents import Agent, Runner
from dotenv import load_dotenv

from check_tool import check_website

load_dotenv()

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_agent() -> Agent:
    return Agent(
        name="Website Monitor",
        model="gpt-4.1-nano",  # cheap & fast; change to gpt-4o or whatever you prefer
        instructions="""
You are a careful website health monitoring agent.

Your job:
1. Take a list of websites (or a natural language request).
2. Use the check_website tool for each URL.
3. Clearly report any issues found (blank pages, HTTP errors, missing titles, timeouts, etc.).
4. Summarize the overall health of the sites.
5. Be concise but complete. Use bullet points for issues.
6. If a site is fine, say so briefly. Focus most attention on problems.

Always call the tool for every URL you are asked to check.
Do not invent results — only report what the tool returns.
""",
        tools=[check_website],
    )


def run_monitor(query: str) -> str:
    """Run the agent and return its final text output."""
    agent = get_agent()
    result = Runner.run_sync(agent, query)
    return result.final_output


def log_results(query: str, output: str) -> Path:
    """Append results to a dated log file and return the path."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"website_check_{datetime.now().strftime('%Y%m%d')}.log"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Query: {query}\n")
        f.write("-" * 40 + "\n")
        f.write(output)
        f.write("\n\n")

    return log_file