from sec_filings_rag.api.config.prompts import RAG_PROMPT
from sec_filings_rag.api.config.settings import settings
from sec_filings_rag.api.models.rag import RAGResponse
from sec_filings_rag.api.services.groq_compat import create_groq_client
from sec_filings_rag.api.services.search import SearchService


class RAGService:
    def __init__(self, search_service: SearchService):
        self.search_service = search_service
        self.client = create_groq_client()

    def generate_answer(self, query: str, limit: int = 3):
        search_results = self.search_service.query(
            query,
            limit,
        )

        context = "".join(result.text for result in search_results.results)

        prompt = RAG_PROMPT.format(context=context, query=query)

        response = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        metadata = [
            {**result.metadata, "score": result.score}
            for result in search_results.results
        ]

        return RAGResponse(
            query=query, answer=response.choices[0].message.content, metadata=metadata
        )
