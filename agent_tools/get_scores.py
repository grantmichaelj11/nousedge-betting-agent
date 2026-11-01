from datetime import date as _date
from typing import Optional
from sports_skills import nfl, nba, mlb, nhl
from langchain.tools import tool

LEAGUES = {"nba": nba, "nfl": nfl, "mlb": mlb, "nhl": nhl}

@tool
def get_scoreboard(league: str, day: Optional[str] = None) -> dict:
    """
    Get the scoreboard for all games in a league.
    Args:
        league: one of nfl, nba, mlb, nhl
        day: Optional date as 'YYYYMMDD'. Leave this out to get today's games.
             Only set it when the user asks about a specific past or future date.
    """
    mod = LEAGUES.get(league.lower())
    if mod is None:
        return {"error": f"League '{league}' is not supported by this tool."}
    try:
        return mod.get_scoreboard(date=day or None)  # treat "" as today
    except Exception as e:
        return {"error": f"Failed to retrieve data: {e}"}