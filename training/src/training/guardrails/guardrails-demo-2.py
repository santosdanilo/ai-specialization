import os
from pathlib import Path

from dotenv import load_dotenv
from guardrails import Guard
from guardrails.hub import ProfanityFree
from guardrails.validators import register_validator, PassResult, FailResult
from groq import Groq

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[2]

load_dotenv(WORKSPACE_ROOT / ".env")

client = Groq(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
)


def groq_wrapper(*, messages, **kwargs):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
    )
    return response.choices[0].message.content


@register_validator(name="simple_topic_validator", data_type="string")
def simple_topic_check(value: str, metadata: dict):
    financial_keyword = ["stock", "apple", "investment", "ticker", "finance", "market"]
    if any(keyword in value.lower() for keyword in financial_keyword):
        return PassResult()
    else:
        return FailResult(error_message="Query is not about financial topics")


guard = Guard().use(ProfanityFree()).use(simple_topic_check, on_fail="exception")

validated_response = guard(
    groq_wrapper,
    messages=[
        {
            "role": "user",
            "contentn": "FAANG representa quais empresas de tecnologia?",
        }
    ],
)

queries = [
    "How is Apple stock doing?",
    "What's the weather today?",
]

for query in queries:
    print(f"\nQuery: {query}")
    try:
        guard.validate(query)

        result = groq_wrapper(messages=[{"role": "user", "content": query}])
        print(result)
    except Exception as e:
        print(f"BLOCKED: {e}")
