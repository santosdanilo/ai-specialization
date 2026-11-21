from collections.abc import Callable
from typing import Any


class EdgarClient:
    """Fetches SEC filing items for a ticker.

    ``company_factory`` is required and injected so the parsing and
    item-combining logic can be tested without network access. Use
    ``load_edgar_client()`` to build the real ``edgar``-backed instance.
    """

    FORM_ITEMS = {"10-K": ["1", "1A", "7", "8", "9A"], "10-Q": ["1", "2", "3", "4"]}

    def __init__(self, company_factory: Callable[[str], Any]):
        self._company_factory = company_factory

    def fetch_filing_data(self, ticker: str, form_type: str) -> dict[str, any]:
        company = self._company_factory(ticker)
        filing = company.get_filings(form=form_type).latest()

        metadata = {
            "ticker": ticker,
            "company_name": filing.company,
            "report_date": str(filing.report_date),
            "form_type": filing.form,
        }

        filing_obj = filing.obj()
        items = {}

        for item_num in self.FORM_ITEMS[form_type]:
            item_key = f"Item {item_num}"
            try:
                items[item_key] = filing_obj[item_key]
            except (KeyError, IndexError):
                continue

        return {"metadata": metadata, "items": items}

    def get_combined_text(self, data: dict) -> str:
        texts = []
        for item_name, item_content in data["items"].items():
            texts.append(f"## {item_name}\n\n{item_content}")

        return "\n\n".join(texts)


def load_edgar_client(email: str) -> EdgarClient:
    """Build the real EdgarClient backed by the ``edgar`` package."""
    from edgar import Company, set_identity

    if email:
        set_identity(email)
    return EdgarClient(company_factory=Company)
