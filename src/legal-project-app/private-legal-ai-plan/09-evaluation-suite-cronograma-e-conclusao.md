# Etapa 9 - Evaluation suite, cronograma e conclusão da V1

## Fase 20 - Evaluation suite

Meta:

```bash
npm run eval
```

Exemplo de saída:

```text
Retrieval evaluation
─────────────────────────────
Vector Recall@5       82.4%
Lexical Recall@5      71.3%
Hybrid Recall@5       91.7%
Hybrid + rerank       95.1%

Generation
─────────────────────────────
Answer correctness     92%
Citation correctness   97%
Groundedness           95%
```

Métricas de retrieval:

- Recall@K;
- Precision@K;
- MRR;
- nDCG.

Métricas de geração:

- correctness;
- groundedness;
- citation correctness;
- hallucination rate.

O comando deve salvar dataset, configuração, timestamp, versão do código/modelo e resultados brutos para permitir comparação entre V1 e V2.

## Cronograma de 4 semanas

### Semana 1 - Retrieval

```text
Dia 1  embeddings
Dia 2  pgvector
Dia 3  ingestion
Dia 4  vector search
Dia 5  naive RAG
Dia 6  eval dataset
Dia 7  chunking experiments
```

Entrega: `TXT/PDF -> RAG -> response + citation`.

### Semana 2 - Retrieval Engineering

```text
Dia 8   DOCX/PDF parsing
Dia 9   structural chunking
Dia 10  lexical search
Dia 11  hybrid search
Dia 12  RRF
Dia 13  reranking
Dia 14  retrieval evals
```

Entrega: comparação entre dense, sparse, hybrid e hybrid + reranking.

### Semana 3 - Produto jurídico

```text
Dia 15  document library
Dia 16  source viewer
Dia 17  citation navigation
Dia 18  amendments / cross-document reasoning
Dia 19  editing proposals
Dia 20  diff + approval
Dia 21  versioning
```

Entrega: research + editing.

### Semana 4 - Segurança e deployment

```text
Dia 22  authentication
Dia 23  tenant isolation
Dia 24  audit trail
Dia 25  prompt injection tests
Dia 26  Docker deployment
Dia 27  NAS/local storage
Dia 28  README + architecture
```

## Critérios de conclusão da V1

```text
PRIVATE LEGAL AI

✓ DOCX
✓ PDF
✓ RAG
✓ embeddings
✓ vector search
✓ lexical search
✓ hybrid retrieval
✓ reranking
✓ citations
✓ evals
✓ document editing
✓ diff approval
✓ version history
✓ authorization
✓ tenant isolation
✓ audit logging
✓ Docker
✓ NAS-compatible storage
```

Antes de iniciar a V2, registre:

- baseline e resultado final por métrica;
- latência e custo por fluxo;
- limitações conhecidas;
- exemplos de falhas de retrieval e geração;
- contratos internos de `ParsedDocument`, `Chunk`, `SearchResult`, `Citation` e `EditProposal`;
- uma tag ou commit identificando a V1 concluída.

Somente depois desse registro a reescrita com LangChain está autorizada.
