"""Tests for KeiNews HTML fetch."""

from unittest.mock import MagicMock, patch

from KeiNews.html import fetch_article_text


@patch("KeiNews.html.requests.get")
def test_fetch_article_with_article_tag(mock_get):
    """fetch_article_text returns text from article tag."""
    mock_response = MagicMock()
    mock_response.text = (
        "<html><body><article><p>Article text</p></article></body></html>"
    )
    mock_get.return_value = mock_response

    result = fetch_article_text("http://example.com")

    assert result == "Article text"


@patch("KeiNews.html.requests.get")
def test_fetch_article_with_paragraphs(mock_get):
    """fetch_article_text returns text from paragraphs when no article tag."""
    mock_response = MagicMock()
    mock_response.text = "<html><body><p>Para 1</p><p>Para 2</p></body></html>"
    mock_get.return_value = mock_response

    result = fetch_article_text("http://example.com")

    assert result == "Para 1\nPara 2"


@patch("KeiNews.html.requests.get")
def test_fetch_article_raises_on_error(mock_get):
    """fetch_article_text raises HTTPError on failed response."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP error")
    mock_get.return_value = mock_response

    try:
        fetch_article_text("http://example.com")
    except Exception as e:
        assert str(e) == "HTTP error"
