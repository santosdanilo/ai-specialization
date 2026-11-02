import argparse
import re


def parse_ticker(value: str) -> str:
    ticker = value.upper()
    if not re.fullmatch(r"[A-Z]{1,5}", ticker):
        raise argparse.ArgumentTypeError(
            f"Invalid ticker: '{value}'. Expected 1-5 uppercase letters, e.g. 'AAPL'"
        )
    return ticker
