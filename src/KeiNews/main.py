"""KeiNews — Fetch NHK news RSS and summarize with a local model."""

import dataclasses
from datetime import datetime
import feedparser
import re
import requests
import os
from pathlib import Path


# Hiragana-to-Romaji mapping (Hepburn)
_HIRA_TO_ROMAJI = {
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
    "か": "ka",
    "き": "ki",
    "く": "ku",
    "け": "ke",
    "こ": "ko",
    "さ": "sa",
    "し": "shi",
    "す": "su",
    "せ": "se",
    "そ": "so",
    "た": "ta",
    "ち": "chi",
    "つ": "tsu",
    "て": "te",
    "と": "to",
    "な": "na",
    "に": "ni",
    "ぬ": "nu",
    "ね": "ne",
    "の": "no",
    "は": "ha",
    "ひ": "hi",
    "ふ": "fu",
    "へ": "he",
    "ほ": "ho",
    "ま": "ma",
    "み": "mi",
    "む": "mu",
    "め": "me",
    "も": "mo",
    "や": "ya",
    "ゆ": "yu",
    "よ": "yo",
    "ら": "ra",
    "り": "ri",
    "る": "ru",
    "れ": "re",
    "ろ": "ro",
    "わ": "wa",
    "を": "wo",
    "ん": "n",
    "がい": "gai",
    "ぎ": "gi",
    "ぐ": "gu",
    "げ": "ge",
    "ご": "go",
    "ざ": "za",
    "じ": "ji",
    "ず": "zu",
    "ぜ": "ze",
    "ぞ": "zo",
    "だ": "da",
    "ぢ": "di",
    "づ": "du",
    "で": "de",
    "ど": "do",
    "ぱ": "pa",
    "ぴ": "pi",
    "ぷ": "pu",
    "ぺ": "pe",
    "ぽ": "po",
    "ば": "ba",
    "び": "bi",
    "ぶ": "bu",
    "べ": "be",
    "ぼ": "bo",
    "っ": "",
    "ぁ": "a",
    "ぃ": "i",
    "ぅ": "u",
    "ぇ": "e",
    "ぉ": "o",
    "ゔ": "bu",
    "ゕ": "ka",
    "ゖ": "ke",
}

# Special long-vowel combinations (ー is katakana long vowel)
# These are handled by the katakana-to-romaji step


def _katakana_to_hiragana(text: str) -> str:
    """Convert katakana characters to hiragana."""
    result = []
    for c in text:
        code = ord(c)
        # Katakana range: ゠-ヿ
        if 0x30A0 <= code <= 0x30FF:
            if c == "ー":
                result.append("ー")
            else:
                # Convert to hiragana by offset
                result.append(chr(code - 0x30A0 + 0x3040))
        else:
            result.append(c)
    return "".join(result)


NHK_RSS_URL = "https://www3.nhk.or.jp/rss/news/cat0.xml"
# Generic local model URL
LOCAL_MODEL_URL = "http://localhost:8215/v1/chat/completions"


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


def _slugify_romanji(title: str) -> str:
    """Convert a title to a romanji (Latin) slug.

    Converts katakana to hiragana, maps hiragana to romaji, strips all
    remaining non-ASCII characters (kanji, punctuation, etc.), and cleans
    up the result into a filename-safe slug.
    """
    # Convert katakana -> hiragana
    text = _katakana_to_hiragana(title)

    # Map hiragana -> romaji
    romaji_parts = []
    i = 0
    while i < len(text):
        # Try 2-char combination first (e.g., "きゃ" -> "kya")
        if i + 1 < len(text):
            two_char = text[i] + text[i + 1]
            special_combo = {
                "きゃ": "kya",
                "きゅ": "kyu",
                "きょ": "kyo",
                "しゃ": "sha",
                "しゅ": "shu",
                "しょ": "sho",
                "ちゃ": "cha",
                "ちゅ": "chu",
                "ちょ": "cho",
                "にゃ": "nya",
                "にゅ": "nyu",
                "にょ": "nyo",
                "ひゃ": "hya",
                "ひゅ": "hyu",
                "ひょ": "hyo",
                "みゃ": "mya",
                "みゅ": "myu",
                "みょ": "myo",
                "りゃ": "rya",
                "りゅ": "ryu",
                "りょ": "ryo",
                "ぎゃ": "gya",
                "ぎゅ": "gyu",
                "ぎょ": "gyo",
                "じゃ": "ja",
                "じゅ": "ju",
                "じょ": "jo",
                "びゃ": "bya",
                "びゅ": "byu",
                "びょ": "byo",
                "ぴゃ": "pya",
                "ぴゅ": "pyu",
                "ぴょ": "pyo",
            }
            if two_char in special_combo:
                romaji_parts.append(special_combo[two_char])
                i += 2
                continue

        c = text[i]
        if c in _HIRA_TO_ROMAJI:
            romaji_parts.append(_HIRA_TO_ROMAJI[c])
            i += 1
        elif c == "ー":
            # Katakana long vowel mark — preserve the vowel sound
            if romaji_parts:
                # Extend last vowel (simple: just keep it)
                romaji_parts.append(romaji_parts[-1][-1])
            i += 1
        else:
            # Keep ASCII characters (letters, digits, punctuation)
            if c.isascii():
                romaji_parts.append(c)
            i += 1

    result = "".join(romaji_parts)

    # Strip all remaining non-ASCII characters
    result = "".join(c for c in result if c.isascii())

    # Clean up: replace non-alphanumeric with single dash, strip dashes
    slug = (
        "".join(c if c.isalnum() else "-" for c in result.lower()).strip("-").strip(".")
    )
    # Collapse multiple dashes
    slug = re.sub(r"-+-", "-", slug)
    return slug


def save_summary_as_md(article: Article, summary: str):
    """Save article summary as a Markdown file."""
    os.makedirs("data/articles", exist_ok=True)
    try:
        dt = datetime.strptime(article.pubDate, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError, TypeError:
        dt = datetime.now()
    date_str = dt.strftime("%Y-%m-%d")
    slug = _slugify_romanji(article.title[:50])
    # slug = article.title[:50]
    filename = f"{date_str}-{slug}.md"
    path = Path("data/articles") / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            f"---\ntitle: {article.title}\ndate: {dt.isoformat()}\nlink: {article.link}\n---\n\n"
        )
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


def summarize_with_local_model(
    article: Article,
    url: str = LOCAL_MODEL_URL,
) -> str | None:
    """Send article to the local model for a simple Japanese summary."""
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
        # 5 seconds to connect, 30 seconds to get the response
        response = requests.post(url, json=payload, timeout=(5, 30))
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to local model at {url}. Is it running?")
        return None
    except requests.exceptions.Timeout:
        print("Error: Request to local model timed out.")
        return None
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
        summary = summarize_with_local_model(item)
        if summary:
            print(f"Summary:\n{summary}")
        print("-" * 40)


if __name__ == "__main__":
    from KeiNews.cli import app

    app()
# I need to edit the file to add these
