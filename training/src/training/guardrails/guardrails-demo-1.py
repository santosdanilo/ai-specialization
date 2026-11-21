import os
from pathlib import Path

from dotenv import load_dotenv
from guardrails import Guard
from guardrails.hub import ProfanityFree
from openai import OpenAI

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[2]

load_dotenv(WORKSPACE_ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
)


def groq_wrapper(*, messages, **kwargs):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
    )
    return response.choices[0].message.content


guard = Guard().use(ProfanityFree())

validated_response = guard(
    groq_wrapper,
    messages=[
        {
            "role": "user",
            "contentn": "FAANG representa quais empresas de tecnologia?",
        }
    ],
)

print(validated_response.validated_output)
