# KeiNews — Project Notes

## User Identity

Always refer to the user as **Ben**, not "the user".

## Adding Dev Dependencies with `uv`

When adding a dev dependency to a `pyproject.toml` project using `uv`:

```bash
uv add --dev <package>
```

This adds the package to `[project.optional-dependencies]` under the `dev` group automatically.

## Project Goal

Fetch news stories from NHK (日本放送協会) and use a local AI model to summarize each story into 2–3 paragraphs of simple Japanese.

## Project Structure

```
KeiNews/
├── README.md          # Project documentation
├── Agents.md          # Project tracking notes (this file)
├── pyproject.toml     # Dependencies
├── uv.lock            # Dependency lock
├── src/
│   └── KeiNews/
│       └── main.py     # Entry point
└── .venv/             # Virtual environment
```

## Progress

### Done

- [x] Created README.md with full project documentation
- [x] Updated pyproject.toml description
- [x] Added Agents.md as project tracking file

### In Progress

- (none)

### Blocked

- (none)

## TODO

### Phase 1 — Core Implementation

- [x] Added feedparser for RSS parsing
- [x] Added pytest for testing
- [x] Added requests dependency
- [x] Implemented NHK RSS feed fetching in `main.py`
- [x] Implemented local model API call for summarization
- [x] Added tests for RSS fetching (3 passed)
- [x] Added tests for local model summarization (2 passed)
- [x] Added end-to-end test (1 passed)
- [x] Added error handling & retry logic
- [x] Phase 1 complete — all 6 tests pass
- [x] All 12 tests pass (includes CLI tests: list, summarize, invalid index)
- [x] CLI entry point `keinews` works — `uv run keinews list` fetches NHK RSS & displays articles

### Phase 1.5 — Dataclass refactor

- [x] Created `Article` dataclass (title, link, description, pubDate)
- [x] Updated `fetch_news` to return `list[Article]`
- [x] Updated `summarize_with_local_model` to take `Article`
- [x] Updated `main` to use `Article` fields
- [x] Updated tests to use `Article` (6 pass)
- [x] Added NHK categories dict (cat0–cat6)

### Phase 2 — Features

- [ ] Support multiple NHK news categories (headlines, top, regional, etc.)
- [ ] Save summaries to files/database
- [ ] CLI arguments for URL selection
- [ ] Daily schedule/cron for automatic news summaries

## Constraints & Preferences

- Summaries must be 2–3 paragraphs in **simple Japanese**
- Uses local AI model (no API costs)
- Python ≥ 3.14
- Uses NHK RSS feed (`https://www3.nhk.or.jp/rss/news/cat0.xml`)

## Notes

- (none)
