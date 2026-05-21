"""Tests for KeiNews RSS fetching."""

from unittest.mock import MagicMock, patch


from KeiNews.main import fetch_news


@patch("KeiNews.main.requests.get")
def test_fetch_news_returns_items(mock_get):
    """fetch_news returns a list of Article dataclass items."""
    mock_response = MagicMock()
    mock_response.text = (
        '<?xml version="1.0" encoding="utf-8?>'
        '<rss xmlns:nhknews="http://www.nhk.or.jp/rss/rss2.0/modules/nhknews/" version="2.0">'
        "<channel>"
        "<title>NHKニュース</title>"
        "<item>"
        "<title>Test Article</title>"
        "<link>http://example.com</link>"
        "<description>Test description</description>"
        "<pubDate>Mon, 01 Jan 2026 00:00:00 +0900</pubDate>"
        "</item>"
        "</channel>"
        "</rss>"
    )
    mock_get.return_value = mock_response

    items = fetch_news()

    assert len(items) == 1
    assert items[0].title == "Test Article"
    assert items[0].link == "http://example.com"
    assert items[0].description == "Test description"
    assert items[0].pubDate == "Mon, 01 Jan 2026 00:00:00 +0900"


@patch("KeiNews.main.requests.get")
def test_fetch_news_empty_feed(mock_get):
    """fetch_news returns empty list when no items."""
    mock_response = MagicMock()
    mock_response.text = (
        '<?xml version="1.0" encoding="utf-8?>'
        '<rss xmlns:nhknews="http://www.nhk.or.jp/rss/rss2.0/modules/nhknews/" version="2.0">'
        "<channel>"
        "<title>NHKニュース</title>"
        "</channel>"
        "</rss>"
    )
    mock_get.return_value = mock_response

    items = fetch_news()

    assert items == []


@patch("KeiNews.main.requests.get")
def test_fetch_news_raises_on_error(mock_get):
    """fetch_news raises HTTPError on failed response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP error")
    mock_get.return_value = mock_response

    try:
        fetch_news()
    except Exception as e:
        assert str(e) == "HTTP error"
