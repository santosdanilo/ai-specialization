import json
from pathlib import Path

import requests
import yfinance as yf
from dotenv import load_dotenv
from openai import OpenAI

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
MODEL_NAME = "openai/gpt-oss-120b"

load_dotenv(WORKSPACE_ROOT / ".env")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
)


def search_kb(query: str):
    response = requests.post(
        "http://localhost:8000/search",
        json={
            "query": query,
            "limit": 3,
        },
    )
    return response.json()


tools = [
    {
        "type": "function",
        "name": "search_kb",
        "description": "Busca informações na base de conhecimento para responder perguntas",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A pergunta do usuário",
                },
            },
            "required": ["query"],
        },
    }
]

input_list = [
    {
        "role": "user",
        "content": "Quais sãos os principais riscos financeiros da Apple?",
    }
]

response = client.responses.create(
    model=MODEL_NAME,
    tools=tools,
    input=input_list,
)
response.model_dump()

input_list += response.output

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        result = search_kb(**args)

        texts = [r["text"] for r in result["results"]]

        input_list.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(
                    {"results": texts},
                    ensure_ascii=True,
                ),
            }
        )

final_response = client.responses.create(
    model=MODEL_NAME,
    instructions="Response à perguta do usuário usando as informações retornadas pela busca.",
    tools=tools,
    input=input_list,
)
print(final_response.output_text)
