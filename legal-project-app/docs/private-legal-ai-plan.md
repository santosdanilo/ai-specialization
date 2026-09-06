# Private Legal AI - Plano de Construção

Este arquivo é o índice do plano. A execução da primeira versão está dividida por etapas em [`private-legal-ai-plan/`](private-legal-ai-plan/).

## Objetivo

Construir, do zero, um **Proof of Concept de pesquisa e edição de documentos jurídicos privados**, cobrindo:

- ingestão de documentos;
- parsing de PDF e DOCX;
- chunking;
- embeddings;
- vector search;
- lexical search / BM25;
- hybrid search;
- reranking;
- RAG;
- citations;
- avaliação;
- edição assistida;
- versionamento;
- segurança;
- deployment local / NAS.

Ao terminar a primeira versão, deve ser possível demonstrar:

> “Construí uma aplicação privada de legal-document research/editing com RAG, embeddings, vector search, hybrid retrieval, reranking, citations, evals e deployment local.”

## Regra da versão 1

Não usar LangChain ou LlamaIndex no início. A primeira implementação deve construir manualmente ingestion, chunking, embeddings, retrieval, ranking, prompt assembly e evaluation. Isso cria um baseline que poderá ser comparado com a versão 2.

## Ordem de execução

| Etapa | Arquivo | Resultado principal |
|---|---|---|
| 0 | [Visão geral e setup](private-legal-ai-plan/00-visao-geral-e-setup.md) | escopo, stack e estrutura inicial |
| 1 | [Corpus e ground truth](private-legal-ai-plan/01-corpus-e-ground-truth.md) | 20-25 documentos e 30 perguntas avaliáveis |
| 2 | [Fundamentos](private-legal-ai-plan/02-fundamentos-embeddings-pgvector-ingestao.md) | embeddings, pgvector e ingestão TXT |
| 3 | [Retrieval básico](private-legal-ai-plan/03-retrieval-basico-e-baseline.md) | busca semântica e Recall@5 baseline |
| 4 | [RAG, citations e chunking](private-legal-ai-plan/04-rag-citations-e-chunking.md) | respostas fundamentadas e chunks estruturais |
| 5 | [Parsing e hybrid search](private-legal-ai-plan/05-parsing-lexical-e-hybrid-search.md) | PDF/DOCX, lexical search e RRF |
| 6 | [Reranking e contextual retrieval](private-legal-ai-plan/06-reranking-e-contextual-retrieval.md) | comparação de ranking e contexto enriquecido |
| 7 | [Produto jurídico](private-legal-ai-plan/07-produto-edicao-e-versionamento.md) | library, viewer, edição aprovada e histórico |
| 8 | [Segurança e deployment](private-legal-ai-plan/08-seguranca-tenant-e-deployment.md) | isolamento, auditoria e execução local/NAS |
| 9 | [Evaluation suite e entrega](private-legal-ai-plan/09-evaluation-suite-cronograma-e-conclusao.md) | `npm run eval`, cronograma e critérios de conclusão |
| 10 | [Versão 2: comparação de frameworks](private-legal-ai-plan/10-versao-2-comparacao-de-frameworks.md) | plano pós-V1 para comparar e migrar componentes |

As etapas de 0 a 9 são a **versão 1**, sem framework de orquestração. A etapa 10 só começa quando os critérios de conclusão da V1 forem atendidos e registrados.

## Primeiro milestone

Não começar pela aplicação completa. O primeiro marco é:

> **20 documentos + 30 perguntas + vector search + Recall@5 mensurável.**

Sem frontend sofisticado, agent, LangChain, LLM local ou edição de documentos. Primeiro prove que o retrieval funciona; depois evolua o sistema.
