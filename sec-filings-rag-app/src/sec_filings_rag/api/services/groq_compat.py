from groq import AsyncGroq, Groq, RateLimitError

from sec_filings_rag.api.config.settings import settings

_GROQ_PATH_PREFIX = "/openai/v1/"


def _maybe_rewrite(opts, needs_rewrite: bool):
    if not needs_rewrite:
        return
    url = getattr(opts, "url", None)
    if isinstance(url, str) and url.startswith(_GROQ_PATH_PREFIX):
        opts.url = url.replace(_GROQ_PATH_PREFIX, "/", 1)


def _needs_base_url_rewrite(base_url: str | None) -> bool:
    return "/openai/v1" not in (base_url or "")


def _model_chain() -> list[str]:
    chain = [settings.llm_model]
    fallbacks = [m.strip() for m in settings.llm_fallback_models.split(",") if m.strip()]
    chain.extend(m for m in fallbacks if m not in chain)
    return chain


def _set_model(options, model: str):
    if isinstance(options.json_data, dict) and "model" in options.json_data:
        options.json_data = {**options.json_data, "model": model}


class OpenRouterGroq(Groq):
    def __init__(self, *args, **kwargs):
        self._rewrite_path = _needs_base_url_rewrite(kwargs.get("base_url"))
        super().__init__(*args, **kwargs)

    def request(self, cast_to, options, **kwargs):
        _maybe_rewrite(options, self._rewrite_path)
        models = _model_chain()
        for index, model in enumerate(models):
            _set_model(options, model)
            try:
                return super().request(cast_to, options, **kwargs)
            except RateLimitError:
                if index == len(models) - 1:
                    raise


class AsyncOpenRouterGroq(AsyncGroq):
    def __init__(self, *args, **kwargs):
        self._rewrite_path = _needs_base_url_rewrite(kwargs.get("base_url"))
        super().__init__(*args, **kwargs)

    async def request(self, cast_to, options, **kwargs):
        _maybe_rewrite(options, self._rewrite_path)
        models = _model_chain()
        for index, model in enumerate(models):
            _set_model(options, model)
            try:
                return await super().request(cast_to, options, **kwargs)
            except RateLimitError:
                if index == len(models) - 1:
                    raise


def create_groq_client(async_client: bool = False):
    cls = AsyncOpenRouterGroq if async_client else OpenRouterGroq
    return cls(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=120.0,
        max_retries=2,
    )
