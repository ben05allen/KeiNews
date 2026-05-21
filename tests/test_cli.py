"""Tests for KeiNews CLI."""

from unittest.mock import patch
from typer.testing import CliRunner

from KeiNews.main import Article
from KeiNews.cli import app

runner = CliRunner()


@patch("KeiNews.cli.fetch_news")
def test_list_articles(mock_fetch):
    """list command displays articles with indices."""
    mock_fetch.return_value = [
        Article(
            title="Article 1",
            link="http://example.com/1",
            description="Desc 1",
            pubDate="Mon, 01 Jan 2026",
        ),
        Article(
            title="Article 2",
            link="http://example.com/2",
            description="Desc 2",
            pubDate="Mon, 01 Jan 2026",
        ),
    ]

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Article 1" in result.stdout
    assert "Article 2" in result.stdout
    assert "1." in result.stdout
    assert "2." in result.stdout


@patch("KeiNews.cli.fetch_news")
@patch("KeiNews.cli.fetch_article_text")
@patch("KeiNews.cli.summarize_with_lm_studio")
def test_summarize_article(mock_summarize, mock_fetch_text, mock_fetch):
    """summarize command fetches full text and summarizes."""
    mock_fetch.return_value = [
        Article(
            title="Article 1",
            link="http://example.com/1",
            description="Desc 1",
            pubDate="Mon, 01 Jan 2026",
        ),
        Article(
            title="Article 2",
            link="http://example.com/2",
            description="Desc 2",
            pubDate="Mon, 01 Jan 2026",
        ),
    ]
    mock_fetch_text.return_value = "Full article text"
    mock_summarize.return_value = "Summary of Article 1"

    result = runner.invoke(app, ["summarize", "1"])

    assert result.exit_code == 0
    assert "Article 1" in result.stdout
    assert "Summary of Article 1" in result.stdout


@patch("KeiNews.cli.fetch_news")
def test_summarize_invalid_index(mock_fetch):
    """summarize with invalid index shows error."""
    mock_fetch.return_value = [
        Article(
            title="Article 1",
            link="http://example.com/1",
            description="Desc 1",
            pubDate="Mon, 01 Jan 2026",
        ),
    ]

    result = runner.invoke(app, ["summarize", "99"])

    assert result.exit_code == 0
    assert "Invalid index" in result.stdout
