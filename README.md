# Website Landing Page Monitor Agent

Turn your old BeautifulSoup website checker into a simple AI agent you can click to run.

## What it does

- You paste a list of websites
- Click **Run Check**
- The agent calls a tool that fetches each page (requests + BeautifulSoup)
- It detects blank pages, HTTP errors, missing titles, timeouts, error-page keywords, etc.
- Results are shown on screen **and** appended to a log file in the `logs/` folder

## Setup (one-time) — Windows 11

```bash
cd website_monitor_agent

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
# then edit .env and put your real OpenAI API key