"""KeiNews CLI with Typer."""

import signal
import typer

from KeiNews.main import fetch_news, summarize_with_local_model, save_summary_as_md
from KeiNews.html import fetch_article_text


NHK_RSS_URL = "https://www3.nhk.or.jp/rss/news/cat0.xml"


class TimeOutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeOutException("Summarize timed out!")


app = typer.Typer(
    help="Fetch NHK news articles and summarize them in easy Japanese.",
)


@app.command("list")
def list_articles(url: str = NHK_RSS_URL):
    """List available NHK news articles with index numbers."""
    items = fetch_news(url)
    if not items:
        typer.echo("No news items found.")
        return
    for i, item in enumerate(items):
        typer.echo(f"{i + 1}. {item.title} ({item.pubDate})")
        typer.echo(f"   Link: {item.link}")
        typer.echo("-" * 40)


@app.command("summarize")
def summarize_article(
    index: int = typer.Argument(..., help="Article index number (1-based)"),
    url: str = NHK_RSS_URL,
):
    """Fetch selected article, get full text, and summarize."""
    items = fetch_news(url)
    if not items:
        typer.echo("No news items found.")
        return
    if index < 1 or index > len(items):
        typer.echo(f"Invalid index. Valid range: 1 to {len(items)}.")
        return
    article = items[index - 1]
    typer.echo(f"Selected: {article.title}")

    full_text = fetch_article_text(article.link)
    if not full_text:
        typer.echo("Could not fetch article text.")
        return

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)

    summary = None
    try:
        summary = summarize_with_local_model(article)
    except TimeOutException as e:
        typer.echo(f"\n{e}")
    finally:
        signal.alarm(0)

    if summary:
        typer.echo(f"Summary:\n{summary}")
        save_summary_as_md(article, summary)
        typer.echo(
            "\nTo view your summarized articles, run 'npm run dev' inside the 'astro-site' directory."
        )
    typer.echo("-" * 40)


if __name__ == "__main__":
    app()
