import feedparser
from langchain.tools import tool
from pydantic import BaseModel, Field, HttpUrl

class Article(BaseModel):
    title: str
    link: HttpUrl
    summary: str = ""
    published: str = ""

class FeedResult(BaseModel):
    sport: str
    articles: list[Article] = Field(default_factory=list)
    error: str | None = None

class FeedInput(BaseModel):
    sport: str = Field(description="ESPN's feed slug, e.g. 'nfl', 'nba', 'mlb'.")

@tool(args_schema=FeedInput)
def get_RSS_feed(sport: str) -> dict:
    """Get the latest news articles for a sport from ESPN's RSS feed
    (https://www.espn.com/espn/rss/<sport>/news).
    Returns each article's title, link, summary and publish date."""
    sport = sport.lower()
    feed = feedparser.parse(f"https://www.espn.com/espn/rss/{sport}/news")

    if feed.bozo and not feed.entries:
        result = FeedResult(sport=sport, error=f"Could not load the ESPN feed for '{sport}'.")
    else:
        result = FeedResult(
            sport=sport,
            articles=[
                Article.model_validate(entry, from_attributes=False)
                for entry in feed.entries[:15]
                if entry.get("title") and entry.get("link")
            ],
        )

    return result.model_dump(mode="json")