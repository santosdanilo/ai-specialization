import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[2]

load_dotenv(WORKSPACE_ROOT / ".env")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def load_test_case(filename: str) -> dict:
    path = APP_ROOT / "test_cases" / filename
    with open(path, "r") as f:
        return json.load(f)


def test_agent_endpoint_apple():
    test_case = load_test_case("apple_test.json")

    response = requests.post(
        f"{API_BASE_URL}/agent",
        json={"query": test_case["query"], "limit": 3},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ticker"] == test_case["expected_ticker"]
    assert "fundamental_analysis" in data
    assert "momentum_analysis" in data
    assert "sentiment_analysis" in data
    assert "final_recommendation" in data


def test_agent_endpoint_ibm():
    test_case = load_test_case("ibm_test.json")

    response = requests.post(
        f"{API_BASE_URL}/agent",
        json={"query": test_case["query"], "limit": 3},
    )

    if response.status_code != 200:
        print(f"\nError response: {response.json()}")

    assert response.status_code == 200

    data = response.json()

    assert data["ticker"] == test_case["expected_ticker"]


def test_agent_endpoint_no_company():
    test_case = load_test_case("no_company_test.json")

    response = requests.post(
        f"{API_BASE_URL}/agent",
        json={"query": test_case["query"], "limit": 3},
    )

    assert response.status_code == 400

    data = response.json()

    assert data["ticker"] == test_case["expected_ticker"]


def test_agent_natural_language():
    test_case = load_test_case("natural_language_test.json")

    response = requests.post(
        f"{API_BASE_URL}/agent",
        json={"query": test_case["query"], "limit": 3},
    )

    if response.status_code != 200:
        print(f"\nError response: {response.json()}")

    assert response.status_code == 200

    data = response.json()

    assert data["ticker"] == test_case["expected_ticker"]
    assert data["final_recommendation"]["action"] in ["BUY", "HOLD", "SELL"]
