"""KeiNews — Fetch NHK news RSS and summarize with LM Studio."""

import dataclasses
import feedparser
import requests
import os
from pathlib import Path
from datetime import datetime


NHK_RSS_URL = "https://www3.nhk.or.jp/rss/news/cat0.xml"
LM_STUDIO_URL = "http://192.168.11.64:1234/v1/chat/completions"


@dataclasses.dataclass
class Article:
    title: str
    link: str
    description: str
    pubDate: str


NHK_categories = {
    "cat0": "Headlines",
    "cat1": "Politics",
    "cat2": "Economics",
    "cat3": "Science & Tech",
    "cat4": "Sports",
    "cat5": "Culture",
    "cat6": "Regional",
}


def save_summary_as_md(article: Article, summary: str):
    """Save article summary as a Markdown file."""
    os.makedirs("data/articles", exist_ok=True)
    try:
        dt = datetime.strptime(article.pubDate, "%a, %d %b %Y %H:%M:%S %Z")
    except (ValueError, TypeError):
        dt = datetime.now()
    date_str = dt.strftime("%Y-%m-%d")
    slug = "".join([c if c.isalnum() else "-" for c in article.title[:20]]).lower().strip("-")
    filename = f"{date_str}-{slug}.md"
    path = Path("data/articles") / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: {article.title}\ndate: {dt.isoformat()}\nlink: {article.link}\n---\n\n")
        f.write(summary)
    print(f"Saved: {path}")


def fetch_news(url: str = NHK_RSS_URL) -> list[Article]:
    """Fetch news items from NHK RSS feed."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS: {e}")
        return []
    feed = feedparser.parse(response.text)
    items = []
    for entry in feed.entries:
        items.append(
            Article(
                title=str(entry.get("title", "")),
                link=str(entry.get("link", "")),
                description=str(entry.get("description", "")),
                pubDate=str(entry.get("published", "")),
            )
        )
    return items


def summarize_with_lm_studio(
    article: Article,
    url: str = LM_STUDIO_URL,
) -> str | None:
    """Send article to LM Studio for a simple Japanese summary."""
    prompt = (
        "Summarize the following Japanese news article into "
        "2 to 3 paragraphs of simple Japanese. "
        "Use easy-to-understand vocabulary and clear sentences. "
        "Keep the summary concise but informative.\n\n"
        f"Title: {article.title}\n\n"
        f"Article: {article.description}"
        "\n/no_think"
    )
    payload = {
        "model": "default",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error summarizing: {e}")
        return None


def main():
    """Fetch NHK news and summarize."""
    items = fetch_news()
    if not items:
        print("No news items found.")
        return
    for item in items[:3]:  # Process top 3 items
        print(f"Title: {item.title}")
        print(f"Date: {item.pubDate}")
        summary = summarize_with_lm_studio(item)
        if summary:
            print(f"Summary:\n{summary}")
        print("-" * 40)


if __name__ == "__main__":
    from KeiNews.cli import app

    app()
