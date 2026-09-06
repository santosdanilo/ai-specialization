# Etapa 0 - Visão geral e setup

## Objetivo

Definir o escopo da primeira versão, preparar o repositório e deixar explícito o que será implementado manualmente antes da comparação com LangChain.

## Stack sugerida

Use uma stack próxima do que já é conhecido:

```text
React + TypeScript
        │
        ▼
Node / Hono
        │
   ┌────┴──────────┐
   │               │
PostgreSQL       Filesystem
+ pgvector       /documents
   │
   ├── chunks
   ├── embeddings
   ├── metadata
   └── full-text search
        │
        ▼
OpenAI / Anthropic
```

## Estrutura inicial

```text
private-legal-ai/

apps/
├── web/
└── api/

packages/
├── database/
├── embeddings/
├── parsers/
├── ingestion/
├── retrieval/
├── generation/
├── evaluation/
└── shared/

test-data/
├── contracts/
└── evals/

infra/
├── docker-compose.yml
└── postgres/

scripts/
├── ingest.ts
├── evaluate.ts
└── generate-test-corpus.ts
```

## Princípios de implementação

- A V1 não usa LangChain nem LlamaIndex.
- Retrieval deve ser testável sem LLM.
- O LLM nunca edita o arquivo diretamente.
- Conteúdo recuperado é dado não confiável, nunca instrução do sistema.
- Autorização deve acontecer antes da chamada ao LLM.
- Toda decisão importante deve ter uma métrica ou um teste reproduzível.

## Saídas desta etapa

- estrutura de pastas criada;
- PostgreSQL com pgvector definido no Docker Compose;
- variáveis de ambiente documentadas;
- comandos para executar API, web, ingestão e avaliação;
- definição de como medir o baseline antes de otimizar.
