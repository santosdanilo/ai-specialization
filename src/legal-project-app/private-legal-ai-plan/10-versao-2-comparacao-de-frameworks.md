# Etapa 10 - Versão 2: comparação de frameworks e reescrita

## Quando iniciar

Esta etapa é **pós-V1**. Não iniciar durante a construção inicial. A reescrita começa somente depois que:

1. as etapas 0 a 9 estiverem concluídas;
2. `npm run eval` produzir um relatório versionado;
3. os critérios de conclusão da V1 estiverem marcados;
4. a V1 estiver identificada por tag ou commit;
5. os contratos e limitações da implementação manual estiverem documentados.

O objetivo não é substituir a V1 sem comparação. É reimplementar partes da mesma aplicação com diferentes bibliotecas, medir os resultados e manter a combinação que oferecer melhor equilíbrio entre qualidade, controle, observabilidade, custo e complexidade.

## Objetivos da V2

- comparar abstrações de LangChain, LlamaIndex e Haystack com os componentes manuais;
- testar Docling para parsing e normalização de documentos;
- comparar PostgreSQL + pgvector com Qdrant como vector store;
- testar DSPy para otimização de prompts e módulos de retrieval/generation;
- reduzir código de orquestração repetitivo;
- testar loaders, text splitters, retrievers, pipelines, chains e output parsers;
- preservar filtros de autorização, citations, edição determinística e audit trail;
- medir regressões de qualidade, latência, custo e depuração;
- decidir, com dados, quais abstrações ficam e quais continuam manuais;
- evitar uma dependência desnecessária de várias bibliotecas sobrepostas.

## Não transformar em abstrações

Nenhuma biblioteca deve controlar regras de segurança ou domínio jurídico. Permanecem sob responsabilidade da aplicação:

- autorização e tenant isolation;
- seleção de documentos permitidos;
- versionamento e hashes;
- aplicação determinística de patches;
- aprovação humana;
- audit log;
- formato e validação de citations;
- dataset e métricas de avaliação.

## Arquitetura alvo

```text
React
  ↓
Node / Hono API
  ↓
domain services
  ├── authorization
  ├── document versions
  ├── edit approval
  └── audit trail
  ↓
AI integration boundary
  ├── Docling adapter (PDF/DOCX)
  ├── LangChain / LangGraph adapters
  ├── LlamaIndex adapters
  ├── Haystack pipeline adapters
  ├── DSPy optimization experiments
  ├── embeddings
  ├── retrievers and rerankers
  ├── prompt templates
  └── structured output parsers
  ↓
Vector store experiment
  ├── PostgreSQL + pgvector
  └── Qdrant
  + filesystem / NAS
```

Como a aplicação atual usa Node/Hono e TypeScript, avalie uma fronteira de integração explícita para as bibliotecas mais maduras em Python. Um worker Python separado, acessado por HTTP ou fila, pode hospedar Docling, Haystack, DSPy e LlamaIndex sem contaminar o domínio da API. Não introduza um worker apenas por preferência: compare a complexidade operacional com adapters TypeScript disponíveis.

Comece com LangChain Expression Language (LCEL) e componentes `Runnable` quando a composição linear for suficiente. Só introduza LangGraph se houver um fluxo realmente stateful, com branching, revisão humana ou retomada de execução que beneficie do grafo.

## Matriz de bibliotecas candidatas

| Biblioteca | Papel nesta V2 | Limite do experimento |
|---|---|---|
| **Docling** | parsing e normalização de PDF/DOCX | preservar página, seção, tabela e offsets para citations |
| **LlamaIndex** | ingestão, indexação e RAG orientado a documentos | comparar índices, retrievers e composição de contexto |
| **Haystack** | pipelines modulares de retrieval e generation | comparar componentes, filtros e execução em produção |
| **DSPy** | otimização de prompts e módulos de retrieval/generation | otimizar somente com o dataset de treino separado do conjunto de teste |
| **Qdrant** | vector store alternativo ao pgvector | comparar filtros, payloads, latência, custo operacional e Recall@K |
| **LangChain** | loaders, retrievers, prompt templates, parsers e LCEL | avaliar redução de código sem esconder regras de domínio |
| **LangGraph** | workflows stateful e human-in-the-loop | usar apenas no fluxo de edição se o estado justificar um grafo |

Essas opções não formam um stack obrigatório. O objetivo é testar componentes isolados e combinações pequenas. Por exemplo, Qdrant pode ser comparado com pgvector sem trocar o parser; Docling pode ser usado com o retrieval manual; DSPy pode otimizar um módulo sem substituir toda a orquestração.

## Mapeamento da V1 para a V2

| V1 manual | Experimento na V2 | Biblioteca ou estratégia | O que comparar |
|---|---|---|---|
| parser PDF/DOCX | document loaders ou adapters próprios | Docling, LangChain, LlamaIndex | preservação de página, seção, tabela e offsets |
| `chunkDocument()` | text splitters, inclusive splitter estrutural | LangChain, LlamaIndex, Haystack | Recall@K, metadados e tamanho dos chunks |
| `embedChunks()` | embeddings provider/integration | adapters de cada framework | vetores, custo, batch e retries |
| query pgvector | vector store/retriever alternativo | Qdrant, LlamaIndex, Haystack, LangChain | filtros, payloads, top-k, latência e controle de tenant |
| `semanticSearch()` | retriever de framework | LlamaIndex, Haystack, LangChain | scores, top-k e observabilidade |
| `lexicalSearch()` | retriever customizado ou pipeline híbrido | Haystack, LlamaIndex, implementação própria | exact match, BM25 e explicabilidade |
| RRF manual | ensemble retriever ou implementação própria | Haystack, LlamaIndex, LangChain | fórmula, pesos e explicabilidade |
| reranker | compressor/reranker adapter | adapters de cada framework | Recall@5, MRR, nDCG, latência e custo |
| prompt assembly | templates e módulos otimizáveis | LangChain, Haystack, DSPy | fidelidade, escaping de fontes e estabilidade |
| resposta JSON | structured output / output parser | LangChain, Haystack, Pydantic | validação de schema e mensagens inválidas |
| RAG | pipeline ou chain equivalente | LlamaIndex, Haystack, LangChain | qualidade, tracing e facilidade de teste |
| otimização manual de prompt | programa declarativo otimizado | DSPy | qualidade fora da amostra e reprodutibilidade |
| fluxo com aprovação | workflow stateful | LangGraph ou workflow próprio | checkpoint, retomada e human-in-the-loop |

Não assumir que um componente homônimo é equivalente. Cada linha da tabela precisa de um experimento com o mesmo dataset e os mesmos filtros. A coluna de biblioteca indica candidatos, não uma obrigação de combinar todos.

## Plano de migração incremental

### V2.0 - Harness de comparação

Antes de trocar componentes, crie um harness que execute V1 e V2 com o mesmo corpus, dataset, usuário, filtros e configuração de avaliação. Cada experimento deve registrar biblioteca, versão, configuração, métricas, latência, custo e artefatos brutos.

Mantenha um conjunto de teste que não seja usado para otimizar prompts com DSPy. O resultado da V1 deve permanecer imutável como baseline.

### V2.1 - Adapters sem mudança de comportamento

Envolva os contratos da V1 com interfaces próprias. O código de domínio deve depender de `DocumentLoader`, `TextSplitter`, `EmbeddingProvider`, `Retriever`, `Reranker` e `Generator`, não diretamente de LangChain, LlamaIndex, Haystack, DSPy ou Qdrant.

```ts
interface Retriever {
  search(input: SearchInput): Promise<SearchResult[]>;
}
```

Implemente adapters que retornem o mesmo `SearchResult` da V1. Rode os testes de contrato antes de substituir qualquer componente no fluxo principal. Um adapter de Qdrant, por exemplo, deve esconder detalhes de payload e retornar os metadados de origem do contrato da aplicação.

### V2.2 - Parsing com Docling

Teste o Docling para PDF e DOCX, convertendo o resultado para o `ParsedDocument` da V1. Compare-o com os parsers manuais e, quando fizer sentido, com loaders de LangChain e LlamaIndex. Se um loader perder página, tabela, seção ou offset, mantenha o parser próprio atrás de um adapter. A conveniência do loader não justifica perder a capacidade de citation.

Compare configurações usando o mesmo corpus e registre:

- número de chunks;
- metadados preservados;
- headings, tabelas, páginas e offsets recuperáveis;
- Recall@5;
- tokens médios e máximos;
- tempo de ingestão;
- custo de embeddings.

Docling tende a ser mais simples de isolar em um worker Python. Antes de adotá-lo, meça o custo operacional de chamar esse worker a partir da API Node/Hono.

### V2.3 - Embeddings e vector stores

Substitua primeiro apenas a integração do provedor de embeddings, depois avalie o vector store/retriever. Compare PostgreSQL + pgvector com Qdrant usando o mesmo embedding, corpus, top-k e filtro. O SQL ou payload filter final deve continuar recebendo `organization_id` e qualquer escopo de acesso do usuário.

Para Qdrant, compare pelo menos:

- payloads e filtros por `organization_id`, `document_id` e versão;
- busca vetorial exata e índices configurados;
- latência p50 e p95;
- custo e complexidade de backup;
- reindexação e atualização de documentos;
- operação local via Docker e integração com NAS.

Teste explicitamente que:

```text
Acme user -> only Acme chunks
Globex user -> only Globex chunks
```

Não aceite uma integração que aplique o filtro depois de recuperar dados de outro tenant. Qdrant deve ser tratado como alternativa ao pgvector, não como motivo para remover as regras de autorização da aplicação.

### V2.4 - Retrieval com LlamaIndex, Haystack e LangChain

Mantenha lexical search e RRF manual na primeira comparação. Depois teste uma implementação equivalente em LlamaIndex, Haystack e LangChain. Preserve a explicação dos rankings de origem para não transformar hybrid search em uma caixa-preta.

O reranker recebe apenas candidatos já filtrados. Compare:

- dense V1;
- sparse V1;
- hybrid + RRF V1;
- hybrid com LlamaIndex;
- hybrid com Haystack;
- hybrid com composição LangChain;
- cada combinação usando pgvector e Qdrant;
- hybrid + reranker em cada implementação.

Haystack deve ser avaliado como pipeline explícito, LlamaIndex como abordagem orientada a índices/documentos e LangChain como composição de retrievers e runnables. O objetivo é comparar transparência, manutenção e desempenho, não declarar um vencedor por preferência.

### V2.5 - RAG e saída estruturada

Implemente o mesmo RAG em LangChain, LlamaIndex e Haystack. Substitua prompt assembly por `ChatPromptTemplate`, prompt templates equivalentes ou componentes de pipeline e avalie structured output para a resposta com citations. O schema deve rejeitar citation sem `documentId`, `section`, `page` ou `chunkId` conforme o contrato adotado.

O conteúdo dos documentos continua delimitado como dado não confiável. Templates e parsers não podem permitir que texto recuperado sobrescreva instruções do sistema.

### V2.6 - Otimização com DSPy

Depois de congelar a implementação de referência e separar treino de teste, use DSPy para experimentar a otimização de módulos de retrieval e generation. Comece por um único módulo, como seleção de contexto ou resposta com citations.

Compare o programa otimizado com o prompt fixo da V1 e com os prompts dos demais frameworks. Registre:

- qualidade no conjunto de validação;
- qualidade no conjunto de teste não usado na otimização;
- estabilidade entre execuções;
- número de chamadas e custo durante a otimização;
- facilidade de reproduzir o programa otimizado;
- comportamento diante de perguntas sem evidência.

DSPy não deve receber documentos de tenants não autorizados durante a otimização e não deve alterar as regras de citations, autorização ou edição.

### V2.7 - Fluxos stateful

Só avaliar LangGraph ou outro orquestrador de workflow para fluxos que precisem de estado explícito, por exemplo:

```text
request edit
  ↓
retrieve sources
  ↓
propose structured patch
  ↓
human approval
  ├── reject -> finish
  └── approve -> deterministic editor -> new version
```

Mesmo com LangGraph, a criação da nova versão e a aplicação do patch continuam sendo operações de domínio determinísticas e autorizadas.

## Estratégia de comparação

Execute V1 e V2 sobre:

- o mesmo `questions.json`;
- o mesmo corpus e versões de documentos;
- o mesmo modelo de embedding, quando a comparação não for sobre o modelo;
- o mesmo top-k e filtros de tenant;
- o mesmo conjunto de prompts, salvo quando a mudança for justamente o template;
- o mesmo protocolo de avaliação;
- pgvector e Qdrant em ambientes equivalentes;
- conjunto de treino/validação separado do teste usado pelo DSPy.

Além das métricas da V1, registre:

- tempo de ingestão;
- latência p50 e p95;
- custo por pergunta;
- memória e tamanho do bundle, quando relevante;
- número de chamadas externas;
- facilidade de reproduzir e depurar uma resposta;
- comportamento em falhas e retries;
- quantidade de código de integração mantido;
- complexidade operacional de um worker Python, quando necessário;
- qualidade dos metadados produzidos pelo Docling;
- custo de backup, reindexação e operação do Qdrant.

## Gates de segurança para a V2

Nenhum componente novo entra no fluxo principal sem passar por:

- testes de tenant isolation;
- testes de prompt injection em documentos;
- teste de citation verificável;
- teste de schema inválido e resposta parcial;
- teste de timeout, retry e rate limit;
- teste de não vazamento em logs e traces;
- teste de patch que não corresponde ao texto original;
- teste de filtro por payload no Qdrant;
- teste de isolamento entre o worker Python e a API;
- teste de que o DSPy não otimiza com dados de outro tenant.

Tracing e telemetria de LangChain, LlamaIndex, Haystack, DSPy ou qualquer serviço associado devem ser desativados, sanitizados ou configurados para não enviar conteúdo jurídico confidencial a um serviço externo sem decisão explícita.

## Critério de adoção

Adotar qualquer componente, framework ou serviço apenas se ele demonstrar ganho claro em pelo menos uma dimensão sem degradar segurança e avaliação:

- qualidade de retrieval ou geração;
- simplicidade significativa de manutenção;
- observabilidade útil;
- facilidade de trocar provedores;
- suporte a retries, batching ou streaming;
- custo ou latência;
- operação local, backup e recuperação;
- preservação de metadados e citations.

Caso contrário, manter a implementação manual. A V2 é uma comparação técnica, não uma migração obrigatória nem uma justificativa para usar todas as bibliotecas juntas.

## Entregas da V2

- [ ] Relatório V1 versus V2 no mesmo dataset.
- [ ] Adapters de LangChain, LlamaIndex, Haystack, DSPy e Qdrant isolados do domínio.
- [ ] Docling comparado com os parsers da V1 e com preservação de citations.
- [ ] pgvector e Qdrant comparados com tenant filtering.
- [ ] Loaders/splitters comparados com preservação de citations.
- [ ] Retriever e reranker comparados em LangChain, LlamaIndex e Haystack.
- [ ] RAG com prompt template e saída estruturada validado.
- [ ] DSPy avaliado com separação entre treino, validação e teste.
- [ ] LangGraph usado somente se o fluxo stateful justificar.
- [ ] Testes de segurança executados novamente.
- [ ] Decisão documentada por componente: adotar, manter manual ou remover.
