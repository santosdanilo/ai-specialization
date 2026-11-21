FIELDS_TO_INDEX = [
    "ticker",
    "form_type",
    "source",
]


def create_filter_indexes(store, fields: list[str] = FIELDS_TO_INDEX) -> list[str]:
    indexed = []
    for field in fields:
        store.ensure_filter_index(field)
        print(f"Index created for field {field}")
        indexed.append(field)
    return indexed


def main() -> None:
    from sec_filings_rag.api.config.settings import get_settings
    from sec_filings_rag.vector_store import create_vector_store

    settings = get_settings()
    store = create_vector_store(settings)
    create_filter_indexes(store)


if __name__ == "__main__":
    main()
