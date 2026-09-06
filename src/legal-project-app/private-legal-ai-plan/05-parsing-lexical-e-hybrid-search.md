# Etapa 5 - Parsing, lexical search e hybrid search

## Fase 9 - PDF e DOCX

Crie parsers diferentes que convergem para um modelo comum:

```ts
interface ParsedDocument {
  id: string;
  title: string;
  blocks: DocumentBlock[];
}

interface DocumentBlock {
  type: "heading" | "paragraph" | "table";
  text: string;
  page?: number;
  section?: string;
}
```

Pipeline:

```text
DOCX       PDF
  ↓          ↓
parser     parser
  └────┬─────┘
       ↓
ParsedDocument
```

Preserve page, section, block type, offsets e tabelas sempre que o formato permitir. O parser não deve misturar parsing, chunking e embedding: cada etapa deve ser substituível e testável.

## Fase 10 - Lexical search

Adicione busca textual começando com PostgreSQL Full Text Search. Implemente:

```ts
semanticSearch()
lexicalSearch()
```

Compare uma consulta exata como:

```text
ACME-MSA-2026-047
```

com uma consulta semântica como:

```text
right to terminate the agreement
```

Avalie também BM25 se ele oferecer vantagem mensurável sobre o ranking textual inicial.

## Fase 11 - Hybrid search

Arquitetura:

```text
                query
                 │
         ┌───────┴───────┐
         ▼               ▼
      vector          lexical
       search           search
         │               │
         └───────┬───────┘
                 ↓
                RRF
                 ↓
              Top 20
```

Implemente manualmente o **Reciprocal Rank Fusion (RRF)** e registre os rankings de origem antes da fusão. Não esconda a fórmula atrás de uma biblioteca nesta versão.

## Entrega

O mesmo conjunto de perguntas pode comparar dense, sparse e hybrid retrieval, com explicação de quais fontes contribuíram para cada resultado.

## Definition of done

- [ ] DOCX e PDF convergem para `ParsedDocument`.
- [ ] Parsing tem testes com headings, parágrafos, tabelas e páginas.
- [ ] Busca lexical encontra identificadores e termos exatos.
- [ ] RRF tem testes unitários e resultados reproduzíveis.
- [ ] O relatório compara vector, lexical e hybrid.
