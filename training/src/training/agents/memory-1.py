import json
from pathlib import Path

import requests
import yfinance as yf
from dotenv import load_dotenv
from mem0 import MemoryClient
from openai import OpenAI

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
MODEL_NAME = "openai/gpt-oss-120b"

load_dotenv(WORKSPACE_ROOT / ".env")
client = MemoryClient()

# messages = [
#    {
#        "role": "user",
#        "content": "Meu nome é Daniel e eu gosto de fazer automações com IA!",
#    },
#    {
#        "role": "assistant",
#        "content": "Oi Daniel! Anotei que você gosta de construir automações com IA! Vou manter isso em mente para recomendações e discussões relacionadas.",
#    },
# ]

# client.add(messages, user_id="daniel")

client.add("Sou o Daniel e gosto de robótica!", user_id="daniel")

query = "Qual o meu nome?"
response = client.search(query, filters={"user_id": "daniel"})
response
response["results"][0]["memory"]
