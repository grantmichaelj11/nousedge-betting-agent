import requests
from langchain.tools import tool
from pydantic import BaseModel, Field, HttpUrl, ValidationError

_session = requests.Session()
_session.headers.update({"User-Agent": "curl/8.5.0", "Accept": "application/json"})

# Your old RSS slugs -> ESPN API "sport/league" paths
LEAGUES = {
    "nfl": "football/nfl",
    "nba": "basketball/nba",
    "mlb": "baseball/mlb",
    "nhl": "hockey/nhl",
}

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
    sport: str = Field(description=f"League slug, one of: {', '.join(LEAGUES)}.")

@tool(args_schema=FeedInput)
def get_RSS_feed(sport: str) -> dict:
    """Get the latest ESPN news articles for a league.
    Returns each article's title, link, summary and publish date."""
    sport = sport.lower().strip()

    def fail(msg: str) -> dict:
        return FeedResult(sport=sport, error=msg).model_dump(mode="json")

    path = LEAGUES.get(sport)
    if not path:
        return fail(f"Unknown league '{sport}'. Use one of: {', '.join(LEAGUES)}.")

    url = f"https://site.api.espn.com/apis/site/v2/sports/{path}/news"
    try:
        resp = _session.get(url, params={"limit": 15}, timeout=15)
        data = resp.json() if resp.status_code == 200 else None
    except (requests.RequestException, ValueError) as e:
        return fail(f"Could not fetch ESPN news for '{sport}' ({type(e).__name__}).")
    if not data:
        return fail(f"ESPN returned HTTP {resp.status_code} for '{sport}'.")

    articles = []
    for a in data.get("articles", [])[:15]:
        link = (a.get("links") or {}).get("web", {}).get("href")
        if not (a.get("headline") and link):
            continue
        try:
            articles.append(Article(
                title=a["headline"],
                link=link,
                summary=a.get("description") or "",
                published=a.get("published") or "",
            ))
        except ValidationError:
            continue

    if not articles:
        return fail(f"ESPN returned no usable articles for '{sport}'.")

    return FeedResult(sport=sport, articles=articles).model_dump(mode="json")