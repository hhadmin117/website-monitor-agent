"""
Website checking tool using requests + BeautifulSoup.
Detects blank pages, HTTP errors, missing titles, and very short content.
"""

from time import perf_counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from agents import function_tool


def _normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


@function_tool
def check_website(url: str) -> str:
    """
    Check a website's landing page health.

    Returns a clear status report including:
    - HTTP status code
    - Response time (latency)
    - Page title
    - Whether the page looks blank, empty, or like an error page
    - Any obvious problems found
    """
    url = _normalize_url(url)
    start = perf_counter()

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, timeout=12, headers=headers, allow_redirects=True)
        latency = perf_counter() - start

        status = response.status_code
        final_url = response.url
        content_type = response.headers.get("Content-Type", "")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "(no title)"

        # Get visible text length (rough measure of "blankness")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text_len = len(text)

        # Detect problems
        problems = []

        if status >= 400:
            problems.append(f"HTTP error status {status}")
        elif status >= 300:
            problems.append(f"Unexpected redirect status {status}")

        if text_len < 80:
            problems.append(f"Page looks blank or nearly empty (only {text_len} characters of text)")

        error_keywords = [
            "404", "not found", "page not found", "error", "server error",
            "something went wrong", "access denied", "forbidden",
            "under construction", "coming soon", "maintenance"
        ]
        lower_text = text.lower()[:2000]  # check beginning
        lower_title = title.lower()
        for kw in error_keywords:
            if kw in lower_title or kw in lower_text:
                problems.append(f"Possible error page content detected (keyword: '{kw}')")
                break

        if not title or title == "(no title)":
            problems.append("Missing or empty <title> tag")

        if "text/html" not in content_type.lower() and status == 200:
            problems.append(f"Unexpected Content-Type: {content_type}")

        # Build report
        report_lines = [
            f"URL: {url}",
            f"Final URL: {final_url}",
            f"HTTP Status: {status}",
            f"Latency: {latency:.2f} seconds",
            f"Title: {title}",
            f"Visible text length: {text_len} chars",
        ]

        if problems:
            report_lines.append("ISSUES FOUND:")
            for p in problems:
                report_lines.append(f"  - {p}")
            report_lines.append("Overall: PROBLEMATIC")
        else:
            report_lines.append("Overall: OK - looks like a healthy landing page")

        return "\n".join(report_lines)

    except requests.exceptions.Timeout:
        return f"URL: {url}\nISSUES FOUND:\n  - Request timed out after 12 seconds\nOverall: PROBLEMATIC"
    except requests.exceptions.ConnectionError as e:
        return f"URL: {url}\nISSUES FOUND:\n  - Connection error: {str(e)[:150]}\nOverall: PROBLEMATIC"
    except Exception as e:
        return f"URL: {url}\nISSUES FOUND:\n  - Unexpected error: {type(e).__name__}: {str(e)[:150]}\nOverall: PROBLEMATIC"