from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
MODEL_NAME = "openai/gpt-oss-120b"

load_dotenv(WORKSPACE_ROOT / ".env")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
)


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


response = client.responses.parse(
    model=MODEL_NAME,
    input="Daniel e Alberto vão gravar uma aula na terça-feira",
    instructions="Extraia informações do evento.",
    text_format=CalendarEvent,
)

event = response.output_parsed
print(event)
