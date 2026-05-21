"""Fetch article text from NHK HTML links."""

import requests
from bs4 import BeautifulSoup


def fetch_article_text(url: str) -> str | None:
    """Fetch full article text from a NHK news link."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article: {e}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    article_body = soup.find("article")
    if article_body:
        return article_body.get_text()
    paragraphs = soup.find_all("p")
    if paragraphs:
        return "\n".join(p.get_text() for p in paragraphs)
    return None
