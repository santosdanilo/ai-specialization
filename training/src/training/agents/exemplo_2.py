import json
from pathlib import Path

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


def get_stock(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    output = {
        "ticker": ticker,
        "company_name": info.get("shortName", ticker),
        "current_price": info.get("currentPrice", 0),
    }
    return json.dumps(output)


tools = [
    {
        "type": "function",
        "name": "get_stock",
        "description": "Retorna informações básicas de uma ação",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Símbolo da ação (ex: APPL, NVDA)",
                },
            },
            "required": ["ticker"],
        },
    }
]

input_list = [
    {
        "role": "user",
        "content": "Qual o preço da ação da Apple?",
    }
]

response = client.responses.create(
    model=MODEL_NAME,
    tools=tools,
    input=input_list,
)
response.model_dump()

for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        result = get_stock(**args)
        input_list.append(item)
        input_list.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": result,
            }
        )

final_response = client.responses.create(
    model=MODEL_NAME,
    instructions="Response com análise baseada nos dados retornados pela função.",
    tools=tools,
    input=input_list,
)
print(final_response.output_text)
