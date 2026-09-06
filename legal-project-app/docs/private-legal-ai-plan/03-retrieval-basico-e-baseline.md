# Etapa 3 - Retrieval básico e baseline

## Fase 4 - Semantic search

Criar:

```ts
search(query, topK)
```

Fluxo:

```text
question
   ↓
embedding
   ↓
pgvector
   ↓
top 5 chunks
```

Retorne resultados com origem suficiente para depuração:

```json
[
  {
    "document": "acme-msa",
    "section": "Termination",
    "score": 0.87,
    "text": "..."
  }
]
```

Ainda não use LLM. Primeiro construa um search engine observável, capaz de mostrar query, filtros, scores e chunks retornados.

## Fase 5 - Primeira avaliação

Rode as 30 perguntas do dataset.

### Recall@5

Para cada pergunta, verifique se pelo menos um chunk correto apareceu nos cinco primeiros resultados. Exemplo:

```text
26 / 30 = 86.7%
```

Esse resultado é o baseline da V1. Guarde também os resultados brutos por pergunta para explicar regressões, não apenas a média.

## Entrega

```text
question
   ↓
embedding
   ↓
vector search
   ↓
top-k chunks + scores + source metadata
   ↓
Recall@5 report
```

## Definition of done

- [ ] `search(query, topK)` funciona sem geração de texto.
- [ ] A busca é filtrável por organização quando essa dimensão já existir.
- [ ] O relatório registra Recall@5 por pergunta e agregado.
- [ ] Os resultados retornados permitem abrir a origem e auditar o score.
- [ ] O baseline está salvo antes de experimentar chunking, lexical search ou reranking.
