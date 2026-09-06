# Etapa 6 - Reranking e contextual retrieval

## Fase 12 - Reranking

Arquitetura:

```text
30.000 chunks
     ↓
hybrid search
     ↓
top 30
     ↓
reranker
     ↓
top 5
     ↓
LLM
```

Meça Recall@5, MRR e nDCG. Compare os resultados antes e depois do reranker e registre latência e custo, não apenas qualidade.

O reranker deve receber query e candidatos já autorizados. Nunca use reranking para tentar corrigir um filtro de tenant aplicado tarde demais.

## Fase 13 - Contextual retrieval

Teste adicionar contexto estrutural aos chunks.

Antes:

```text
The term is thirty-six months.
```

Depois:

```text
ACME Master Service Agreement,
Section 7 - Term.

The term is thirty-six months.
```

Rode os evals novamente e compare a recuperação, o tamanho do contexto e o custo. A contextualização deve manter o vínculo com a fonte original.

## Entrega

```text
query
  ↓
hybrid top 30
  ↓
rerank top 5
  ↓
contextual chunks
  ↓
RAG com citations
```

## Definition of done

- [ ] Há comparação antes/depois do reranker.
- [ ] Recall@5, MRR e nDCG são calculados.
- [ ] Latência e custo do reranking estão registrados.
- [ ] Contextual retrieval melhora ou explica seu impacto no dataset.
- [ ] O pipeline mantém filtros de autorização antes de todos os modelos.
