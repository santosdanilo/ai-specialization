from types import SimpleNamespace

from conftest import FakeEmbeddingService, FakeVectorStore
from sec_filings_rag.ingestion.create_indexes import create_filter_indexes
from sec_filings_rag.ingestion.ingestion import ingest_filings
from sec_filings_rag.ingestion.news_ingestion import ingest_news
from sec_filings_rag.ingestion.utils.edgar_client import EdgarClient
from sec_filings_rag.ingestion.utils.news_client import NewsClient
from sec_filings_rag.ingestion.utils.records import build_records
from sec_filings_rag.ingestion.utils.simple_chunker import SimpleChunker

TEXT = "para one " * 15 + "\n\n" + "para two " * 15


class FakeTokenizer:
    def encode(self, text, add_special_tokens=True):
        return [0] * len(text.split())


class FakeFiling:
    company = "Acme"
    report_date = "2025-01-01"
    form = "10-K"

    def obj(self):
        return {"Item 1": "business text", "Item 1A": "risk text"}


class FakeFilings:
    def latest(self):
        return FakeFiling()


class FakeCompany:
    def __init__(self, name):
        self.name = name

    def get_filings(self, form=None):
        return FakeFilings()


class TestSimpleChunker:
    def test_splits_on_token_budget(self):
        chunker = SimpleChunker(tokenizer=FakeTokenizer(), max_tokens=20)
        chunks = chunker.create_chunks(TEXT)
        assert len(chunks) == 2

    def test_empty_text(self):
        chunker = SimpleChunker(tokenizer=FakeTokenizer(), max_tokens=20)
        assert chunker.create_chunks("") == []


class TestEdgarClient:
    def test_fetch_filing_data_with_injected_company_factory(self):
        client = EdgarClient(company_factory=FakeCompany)
        data = client.fetch_filing_data("ACME", "10-K")

        assert data["metadata"] == {
            "ticker": "ACME",
            "company_name": "Acme",
            "report_date": "2025-01-01",
            "form_type": "10-K",
        }
        assert data["items"] == {"Item 1": "business text", "Item 1A": "risk text"}

    def test_get_combined_text(self):
        client = EdgarClient(company_factory=FakeCompany)
        text = client.get_combined_text({"items": {"Item 1": "hello"}})
        assert text == "## Item 1\n\nhello"


class TestNewsClient:
    def test_filters_non_stories_and_extracts(self):
        def news_fetcher(ticker, count):
            return SimpleNamespace(
                news=[
                    {
                        "content": {
                            "contentType": "AD",
                            "title": "x",
                            "canonicalUrl": {"url": "https://finance.yahoo.com/1"},
                        }
                    },
                    {
                        "content": {
                            "contentType": "STORY",
                            "title": "t",
                            "pubDate": "d",
                            "canonicalUrl": {"url": "https://other.com/2"},
                        }
                    },
                    {
                        "content": {
                            "contentType": "STORY",
                            "title": "t3",
                            "pubDate": "d3",
                            "canonicalUrl": {"url": "https://finance.yahoo.com/3"},
                        }
                    },
                ]
            )

        client = NewsClient(
            news_fetcher=news_fetcher,
            url_fetcher=lambda url: "raw-html",
            text_extractor=lambda raw: "extracted text",
        )

        result = client.fetch_news("AAPL", max_stories=5)

        assert result == [
            {
                "text": "extracted text",
                "metadata": {
                    "ticker": "AAPL",
                    "title": "t3",
                    "url": "https://finance.yahoo.com/3",
                    "date": "d3",
                    "source": "yahoo_finance",
                },
            }
        ]

    def test_drops_articles_without_extracted_text(self):
        def news_fetcher(ticker, count):
            return SimpleNamespace(
                news=[
                    {
                        "content": {
                            "contentType": "STORY",
                            "title": "t",
                            "canonicalUrl": {"url": "https://finance.yahoo.com/3"},
                        }
                    }
                ]
            )

        client = NewsClient(
            news_fetcher=news_fetcher,
            url_fetcher=lambda url: None,
            text_extractor=lambda raw: None,
        )
        assert client.fetch_news("AAPL") == []


class TestBuildRecords:
    def test_builds_record_per_chunk(self):
        items = [
            {"text": "a", "metadata": {"ticker": "AAPL"}},
            {"text": "b", "metadata": {"ticker": "MSFT"}},
        ]
        embedder = FakeEmbeddingService()

        records = build_records(items, embedder)

        assert embedder.passage_calls == [["a", "b"]]
        assert len(records) == 2
        assert records[0] == {
            "text": "a",
            "metadata": {"ticker": "AAPL"},
            "vectors": {
                "dense": [0.5] * 3,
                "sparse": {"indices": [0], "values": [1.0]},
                "colbert": [[1.0]],
            },
        }


class TestIngestFilings:
    def test_end_to_end_with_fakes(self):
        class Chunker:
            def create_chunks(self, text):
                return [text]

        edgar = EdgarClient(company_factory=FakeCompany)
        store = FakeVectorStore()

        count = ingest_filings(
            store=store,
            edgar=edgar,
            chunker=Chunker(),
            embedding_service=FakeEmbeddingService(),
            ticker="ACME",
            form_types=["10-K"],
        )

        assert count == 1
        assert store.upserted[0]["metadata"]["ticker"] == "ACME"
        assert set(store.upserted[0]["vectors"]) == {"dense", "sparse", "colbert"}


class TestIngestNews:
    def test_end_to_end_with_fakes(self):
        class Chunker:
            def create_chunks(self, text):
                return [text[:5], text[5:]]

        news_client = SimpleNamespace(
            fetch_news=lambda ticker, max_stories=10: [
                {
                    "text": "hello world",
                    "metadata": {"ticker": "AAPL", "source": "yahoo_finance"},
                }
            ]
        )
        store = FakeVectorStore()

        count = ingest_news(
            store=store,
            news_client=news_client,
            chunker=Chunker(),
            embedding_service=FakeEmbeddingService(),
            ticker="AAPL",
        )

        assert count == 2
        assert len(store.upserted) == 2


class TestCreateFilterIndexes:
    def test_creates_all_fields(self):
        store = FakeVectorStore()
        fields = create_filter_indexes(store, fields=["a", "b", "c"])
        assert fields == ["a", "b", "c"]
        assert store.indexed_fields == ["a", "b", "c"]
