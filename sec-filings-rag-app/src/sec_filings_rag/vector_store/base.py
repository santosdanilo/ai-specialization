from typing import Any, NamedTuple, Protocol, TypedDict, runtime_checkable


class ScoredHit(NamedTuple):
    """DB-agnostic search result. ``score`` is higher-is-better."""

    score: float
    text: str
    metadata: dict[str, Any]


class VectorRecord(TypedDict):
    """DB-agnostic write unit produced by ingestion."""

    text: str
    metadata: dict[str, Any]
    vectors: dict[str, Any]  # {"dense", "sparse", "colbert"}


@runtime_checkable
class VectorStore(Protocol):
    """Switchable vector database interface (Qdrant today, Postgres later)."""

    def search(
        self,
        *,
        dense: Any,
        sparse: Any,
        colbert: Any,
        limit: int = 3,
        filter: dict[str, Any] | None = None,
    ) -> list[ScoredHit]: ...

    def reset(self) -> None: ...

    def upsert(self, records: list[VectorRecord]) -> int: ...

    def ensure_filter_index(self, field: str) -> None: ...
