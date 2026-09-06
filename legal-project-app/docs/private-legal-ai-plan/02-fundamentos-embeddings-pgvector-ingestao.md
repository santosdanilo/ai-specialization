# Etapa 2 - Fundamentos: embeddings, pgvector e ingestão

## Objetivo

Entender e implementar o caminho mínimo de um documento TXT até chunks persistidos, sem esconder as decisões atrás de um framework.

## Fase 1 - Embeddings

Antes de usar banco vetorial, teste frases simples:

```text
This contract expires in 24 months.
This agreement has a term of two years.
Bananas are yellow.
```

Fluxo:

```text
embedding(text)
       ↓
number[]
       ↓
cosine similarity
```

Implemente manualmente:

```ts
cosineSimilarity(a, b)
```

Registre o que foi aprendido sobre embedding, dimensionalidade, cosine similarity, dot product, distância euclidiana e normalização. Os vetores de produção podem vir de OpenAI ou outro provedor, mas a função de comparação deve ser compreendida e testada localmente.

## Fase 2 - PostgreSQL + pgvector

Suba PostgreSQL com pgvector usando Docker Compose. Comece com busca vetorial exata; só adicione HNSW ou IVFFlat depois de medir o comportamento da busca exata.

Modelo inicial:

```text
documents
---------
id
filename
content_type
created_at

chunks
------
id
document_id
content
embedding
page
section
start_offset
end_offset
metadata
```

Reserve espaço para `organization_id`, `document_version_id` e identificadores de origem mesmo que isolamento e versionamento sejam implementados em etapas posteriores.

## Fase 3 - Ingestão TXT

Antes de PDF e DOCX:

```text
    ↓
read
    ↓
split
    ↓
embedding
    ↓
INSERT chunks
```

Implemente:

```ts
chunkDocument()
embedChunks()
storeChunks()
```

O pipeline deve ser idempotente: reprocessar o mesmo documento não pode criar duplicatas silenciosas. Registre o hash do arquivo e a configuração de chunking usada.

## Entrega

Um TXT é ingerido, dividido, vetorizado, persistido no PostgreSQL e consultável por um teste automatizado que verifica dimensões do vetor e metadados básicos.

## Definition of done

- [ ] `cosineSimilarity` tem testes para vetores iguais, ortogonais e normalizados.
- [ ] PostgreSQL + pgvector sobe por Docker Compose.
- [ ] O schema guarda conteúdo, vetor e origem do chunk.
- [ ] A ingestão TXT é repetível e observável.
- [ ] O pipeline não chama um LLM para fazer retrieval.
