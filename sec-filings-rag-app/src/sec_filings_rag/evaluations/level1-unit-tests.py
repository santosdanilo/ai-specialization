import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[2]

load_dotenv(WORKSPACE_ROOT / ".env")

client = OpenAI(base_url=os.getenv("GROQ_API_URL"))


def load_test_case(filename: str) -> dict:
    path = APP_ROOT / "test_cases" / filename
    with open(path, "r") as f:
        return json.load(f)


COMPANY_TICKER_MAPPINGS = {
    "apple": "AAPL",
    "microsoft": "MSFT",
    "google": "GOOGL",
    "tesla": "TSLA",
    "meta": "META",
}

TICKER_EXTRACTION_PROMPT = """You are a stock ticker symbol extractor. Given a user message, extract the stock ticker symbol for any publicly traded company mentioned.

Rules:
- Return ONLY the ticker symbol (e.g., AAPL, TSLA, MSFT)
- If no company is mentioned, return "NONE"
- If multiple companies are mentioned, return the first/main one
- Use standard US stock exchange ticker symbols (NYSE, NASDAQ)

Examples:
User: "How is Disney doing?" → DIS
User: "What about Tesla's performance?" → TSLA
User: "Tell me about IBM" → IBM
User: "What's the weather today?" → NONE

User message: {query}
Response:"""

MODEL_NAME = "openai/gpt-oss-120b"


class TickerResult(BaseModel):
    ticker: str = Field(
        pattern="^[A-Z]{1,5}$",
        description="Stock ticker symbol (1-5 uppercase letters)",
    )


def extract_ticker(query: str) -> str | None:
    query_lower = query.lower()
    for company_name, ticker in COMPANY_TICKER_MAPPINGS.items():
        if company_name in query_lower:
            return ticker

    prompt = TICKER_EXTRACTION_PROMPT.format(query=query)

    response = client.responses.parse(
        model=MODEL_NAME,
        text_format=TickerResult,
        input=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    ticker = response.output_parsed.ticker

    return ticker if ticker != "NONE" else None


def test_static_mapping_apple():
    test_case = load_test_case("apple_test.json")
    result = extract_ticker(test_case["query"])
    assert result == test_case["expected_ticker"], (
        f"Expected {test_case['expected_ticker']}, got {result}"
    )


def test_llm_fallback():
    test_case = load_test_case("ibm_test.json")
    result = extract_ticker(test_case["query"])
    assert result == test_case["expected_ticker"], (
        f"Expected {test_case['expected_ticker']}, got {result}"
    )


def test_no_company_mentioned():
    test_case = load_test_case("no_company_test.json")
    result = extract_ticker(test_case["query"])
    assert result == test_case["expected_ticker"], (
        f"Expected {test_case['expected_ticker']}, got {result}"
    )


def test_natural_language_query():
    test_case = load_test_case("natural_language_test.json")
    result = extract_ticker(test_case["query"])
    assert result == test_case["expected_ticker"], (
        f"Expected {test_case['expected_ticker']}, got {result}"
    )


if __name__ == "__main__":
    tests = [
        test_static_mapping_apple,
        test_llm_fallback,
        test_no_company_mentioned,
        test_natural_language_query,
    ]

    passed = 0

    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL {test.__name__}: {e}")

    print(f"\nResults: {passed}/{len(tests)} tests passed!")
