"""End-to-end test: fetch + summarize."""

from unittest.mock import MagicMock, patch

from KeiNews.main import main


@patch("KeiNews.main.requests.get")
@patch("KeiNews.main.requests.post")
def test_main_fetch_and_summarize(mock_post, mock_get):
    """main fetches news and summarizes top 3 items."""
    # RSS mock
    mock_response = MagicMock()
    mock_response.text = (
        '<?xml version="1.0" encoding="utf-8?>'
        '<rss xmlns:nhknews="http://www.nhk.or.jp/rss/rss2.0/modules/nhknews/" version="2.0">'
        "<channel>"
        "<title>NHKニュース</title>"
        "<item>"
        "<title>Article 1</title>"
        "<link>http://example.com/1</link>"
        "<description>Desc 1</description>"
        "<pubDate>Mon, 01 Jan 2026 00:00:00 +0900</pubDate>"
        "</item>"
        "<item>"
        "<title>Article 2</title>"
        "<link>http://example.com/2</link>"
        "<description>Desc 2</description>"
        "<pubDate>Mon, 01 Jan 2026 00:01:00 +0900</pubDate>"
        "</item>"
        "<item>"
        "<title>Article 3</title>"
        "<link>http://example.com/3</link>"
        "<description>Desc 3</description>"
        "<pubDate>Mon, 01 Jan 2026 00:02:00 +0900</pubDate>"
        "</item>"
        "</channel>"
        "</rss>"
    )
    mock_get.return_value = mock_response

    # LM Studio mock
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"choices": [{"message": {"content": "要約"}}]}
    mock_post.return_value = mock_resp

    captured_output = []
    with patch("builtins.print") as mock_print:
        mock_print.side_effect = lambda *args: captured_output.append(str(args[0]))
        main()

    assert len(captured_output) > 0
    assert any("Article 1" in s for s in captured_output)
    assert any("Article 2" in s for s in captured_output)
    assert any("Article 3" in s for s in captured_output)
