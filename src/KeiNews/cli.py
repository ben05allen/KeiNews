"""KeiNews CLI with Typer."""

import typer

from KeiNews.main import fetch_news, summarize_with_lm_studio, save_summary_as_md
from KeiNews.html import fetch_article_text


NHK_RSS_URL = "https://www3.nhk.or.jp/rss/news/cat0.xml"
LM_STUDIO_URL = "http://192.168.11.64:1234/v1/chat/completions"


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

    summary = summarize_with_lm_studio(
        article,
        url=LM_STUDIO_URL,
    )
    if summary:
        typer.echo(f"Summary:\n{summary}")
        save_summary_as_md(article, summary)
        typer.echo("\nTo view your summarized articles, run 'npm run dev' inside the 'astro-site' directory.")
    typer.echo("-" * 40)


if __name__ == "__main__":
    app()
