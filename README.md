# KeiNews

## Overview

**KeiNews** is a Python project that fetches news stories from [NHK (日本放送協会)](https://www.nhk.or.jp/) and summarizes them using a local AI model served by [LM Studio](https://lmstudio.ai/). The summaries are output in **simple Japanese** (2–3 paragraphs) to make the news more accessible.

### Why NHK?

NHK is Japan's public broadcaster and provides reliable, balanced news coverage across topics — politics, economics, science, culture, and daily life. Their website has free, publicly available news articles in Japanese.

### Why LM Studio?

LM Studio lets you run an AI model locally on your machine (no API costs, no privacy concerns, offline-capable). KeiNews connects to LM Studio's local HTTP API to request summaries.

## Architecture

```
┌──────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────────┐
│  NHK RSS  │──▶│  FeedParser │──▶│  LM Studio │──▶│ Summary │
│  Feed     │   │  (Parsing)  │   │ (AI Model)  │   │ (JP)    │
└──────────┘    └─────────────┘    └─────────────┘    └──────────┘
```

1. **Fetch** — pull NHK RSS feed via HTTP
2. **Parse** — extract items (title, description, link) using feedparser
3. **Summarize** — send article content to LM Studio's local API for a simple Japanese summary (2–3 paragraphs)
4. **Output** — print/display the summary

## Project Structure

```
KeiNews/
├── README.md          # This document
├── pyproject.toml     # Project metadata & dependencies
├── uv.lock            # uv dependency lock file
├── src/
│   └── KeiNews/
│       └── main.py     # Entry point
└── .venv/             # Virtual environment
```

## Setup

### Prerequisites

- **Python ≥ 3.14**
- **LM Studio** installed with a model loaded and the local server enabled
- **uv** (for dependency management)

### Install Dependencies

```bash
uv sync
```

### Configure LM Studio

1. Open LM Studio
2. Load your chosen model
3. Start the local server (typically on `localhost:1234`)
4. Note the API endpoint — KeiNews will send requests to it

### Running KeiNews

```bash
uv run src/KeiNews/main.py
```

## NHK RSS Feed

KeiNews uses NHK's RSS feed for general news:

| Feed         | URL                                        |
| ------------ | ------------------------------------------ |
| General News | `https://www3.nhk.or.jp/rss/news/cat0.xml` |

Other categories available:

| Category       | URL                                        |
| -------------- | ------------------------------------------ |
| Politics       | `https://www3.nhk.or.jp/rss/news/cat1.xml` |
| Economics      | `https://www3.nhk.or.jp/rss/news/cat2.xml` |
| Science & Tech | `https://www3.nhk.or.jp/rss/news/cat3.xml` |
| Sports         | `https://www3.nhk.or.jp/rss/news/cat4.xml` |
| Culture        | `https://www3.nhk.or.jp/rss/news/cat5.xml` |
| Regional       | `https://www3.nhk.or.jp/rss/news/cat6.xml` |

## Summarization Prompt

KeiNews sends the following prompt to LM Studio:

> "Summarize the following Japanese news article into 2 to 3 paragraphs of simple Japanese. Use easy-to-understand vocabulary and clear sentences. Keep the summary concise but informative."

## Dependencies

| Package      | Purpose                                         |
| ------------ | ----------------------------------------------- |
| `feedparser` | RSS parsing to extract news items from NHK feed |

## Dev Dependencies

| Package | Purpose      |
| ------- | ------------ |
| `ruff`  | Code linting |

## TODO / Future Work

- [ ] Implement NHK RSS feed fetching in `main.py`
- [ ] Implement LM Studio API call logic
- [ ] Add error handling & retry logic
- [ ] Support multiple news categories
- [ ] Save summaries to files or database
- [ ] CLI arguments for URL selection
- [ ] Schedule / cron for daily news summaries
