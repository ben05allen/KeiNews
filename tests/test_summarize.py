"""Tests for KeiNews LM Studio summarization."""

from unittest.mock import MagicMock, patch

import sys

sys.path.insert(0, "../../src")

from KeiNews.main import summarize_with_lm_studio, Article


@patch("KeiNews.main.requests.post")
def test_summarize_returns_text(mock_post):
    """summarize_with_lm_studio returns summary text."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "テストの要約"}}]
    }
    mock_post.return_value = mock_response

    article = Article(
        title="Test Article",
        link="http://example.com",
        description="Test content",
        pubDate="Mon, 01 Jan 2026 00:00:00 +0900",
    )
    result = summarize_with_lm_studio(article)

    assert result == "テストの要約"


@patch("KeiNews.main.requests.post")
def test_summarize_raises_on_error(mock_post):
    """summarize_with_lm_studio raises HTTPError on failed response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP error")
    mock_post.return_value = mock_response

    article = Article(
        title="Test Article",
        link="http://example.com",
        description="Test content",
        pubDate="Mon, 01 Jan 2026 00:00:00 +0900",
    )

    try:
        summarize_with_lm_studio(article)
    except Exception as e:
        assert str(e) == "HTTP error"
