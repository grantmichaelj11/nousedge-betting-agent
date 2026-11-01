from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from agent_tools import TOOLS
import human_tools
from dotenv import load_dotenv
import os
load_dotenv()

with open("instructions.md") as f:
        raw_instructions = f.read()

now = datetime.now(ZoneInfo("America/New_York"))
yesterday = now - timedelta(days=1)

instructions = (
    raw_instructions
    .replace("{today}", now.strftime("%A, %B %d, %Y"))
    .replace("{yesterday}", yesterday.strftime("%A, %B %d, %Y"))
    .replace("{yesterday_ymd}", yesterday.strftime("%Y%m%d"))
)

model = ChatOpenRouter(
    model="deepseek/deepseek-v4.1-flash-1017",
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1",
    streaming=True,
    temperature=0.0,
    reasoning={'effort': 'medium'},
)

agent = create_agent(
    model=model,
    tools=TOOLS,
    system_prompt=instructions
)

result = agent.invoke({"messages": [{"role": "user", "content": "Get news and scores for the NFL, NBA and NHL"}]})
report = result["messages"][-1].content

human_tools.send_report(report)