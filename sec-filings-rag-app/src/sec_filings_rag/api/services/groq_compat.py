from groq import AsyncGroq, Groq, RateLimitError

_GROQ_PATH_PREFIX = "/openai/v1/"


def _maybe_rewrite(opts, needs_rewrite: bool):
    if not needs_rewrite:
        return
    url = getattr(opts, "url", None)
    if isinstance(url, str) and url.startswith(_GROQ_PATH_PREFIX):
        opts.url = url.replace(_GROQ_PATH_PREFIX, "/", 1)


def _needs_base_url_rewrite(base_url: str | None) -> bool:
    return "/openai/v1" not in (base_url or "")


def build_model_chain(primary_model: str, fallback_models: str) -> list[str]:
    chain = [primary_model]
    fallbacks = [m.strip() for m in fallback_models.split(",") if m.strip()]
    chain.extend(m for m in fallbacks if m not in chain)
    return chain


def _set_model(options, model: str):
    if isinstance(options.json_data, dict) and "model" in options.json_data:
        options.json_data = {**options.json_data, "model": model}


class ModelFallbackMixin:
    def __init__(self, *, models: list[str], **kwargs):
        self._model_chain = list(models)
        self._rewrite_path = _needs_base_url_rewrite(kwargs.get("base_url"))
        super().__init__(**kwargs)


class OpenRouterGroq(ModelFallbackMixin, Groq):
    def request(self, cast_to, options, **kwargs):
        _maybe_rewrite(options, self._rewrite_path)
        models = self._model_chain
        for index, model in enumerate(models):
            _set_model(options, model)
            try:
                return super().request(cast_to, options, **kwargs)
            except RateLimitError:
                if index == len(models) - 1:
                    raise


class AsyncOpenRouterGroq(ModelFallbackMixin, AsyncGroq):
    async def request(self, cast_to, options, **kwargs):
        _maybe_rewrite(options, self._rewrite_path)
        models = self._model_chain
        for index, model in enumerate(models):
            _set_model(options, model)
            try:
                return await super().request(cast_to, options, **kwargs)
            except RateLimitError:
                if index == len(models) - 1:
                    raise


def create_groq_client(
    *,
    api_key: str,
    base_url: str,
    model: str,
    fallback_models: str = "",
    async_client: bool = False,
    timeout: float = 120.0,
    max_retries: int = 2,
):
    cls = AsyncOpenRouterGroq if async_client else OpenRouterGroq
    return cls(
        models=build_model_chain(model, fallback_models),
        api_key=api_key,
        base_url=base_url,
        timeout=timeout,
        max_retries=max_retries,
    )
