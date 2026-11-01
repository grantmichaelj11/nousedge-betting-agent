import feedparser
from curl_cffi import requests as cffi_requests
from curl_cffi.requests.exceptions import RequestException
from langchain.tools import tool
from pydantic import BaseModel, Field, HttpUrl, ValidationError

_session = cffi_requests.Session(impersonate="chrome")

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
    sport = sport.lower().strip()
    url = f"https://www.espn.com/espn/rss/{sport}/news"

    def fail(msg: str) -> dict:
        return FeedResult(sport=sport, error=msg).model_dump(mode="json")

    try:
        resp = _session.get(url, timeout=15)
    except RequestException as e:
        return fail(f"Could not fetch ESPN feed for '{sport}' ({type(e).__name__}: {e}).")

    body_start = resp.content[:200].lstrip().lower()
    if resp.status_code != 200 or not body_start.startswith((b"<?xml", b"<rss")):
        return fail(f"ESPN did not return a feed for '{sport}' "
                    f"(HTTP {resp.status_code}, {len(resp.content)} bytes): blocked or invalid slug.")

    feed = feedparser.parse(resp.content)

    articles = []
    for entry in feed.entries[:15]:
        if not (entry.get("title") and entry.get("link")):
            continue
        try:
            articles.append(Article.model_validate(dict(entry)))
        except ValidationError:
            continue

    if not articles:
        return fail(f"ESPN feed for '{sport}' had no usable articles.")

    return FeedResult(sport=sport, articles=articles).model_dump(mode="json")