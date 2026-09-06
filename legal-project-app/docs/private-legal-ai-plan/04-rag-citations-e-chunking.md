# Etapa 4 - RAG, citations e chunking

## Fase 6 - Primeiro RAG

Arquitetura:

```text
question
  ↓
retrieval
  ↓
top chunks
  ↓
prompt
  ↓
LLM
```

Prompt conceitual:

```text
Answer the question using ONLY the provided sources.

If the answer cannot be determined from the sources,
say that the available documents do not provide enough information.

Provide citations.

<SOURCES>
...
</SOURCES>
```

O prompt deve separar instruções confiáveis de conteúdo recuperado e deixar explícito que ausência de evidência deve produzir uma resposta de insuficiência, não uma invenção.

## Fase 7 - Citations

Cada chunk deve guardar ao menos:

```json
{
  "document": "ACME Master Service Agreement",
  "page": 7,
  "section": "14.2",
  "chunkId": "..."
}
```

Uma resposta deve apontar para a origem:

```text
The agreement may be terminated with 30 days' written notice.

[ACME MSA §14.2, p.7]
```

Citation não é apenas texto decorativo: o identificador precisa levar ao trecho correto no Source Viewer quando a interface existir.

## Fase 8 - Experimentos de chunking

Compare tamanhos de 100, 250, 500 e 1000 tokens com overlap de 0, 50 e 100 tokens. Meça:

- Recall@K;
- precisão;
- latência;
- tamanho do contexto entregue ao LLM;
- custo estimado de embeddings e geração.

## Chunking estrutural

Depois dos chunks fixos, implemente chunks orientados à estrutura:

```text
Section 1
Section 2
Section 3.1
Section 3.2
```

Modelo:

```json
{
  "document": "acme-msa",
  "section": "14",
  "sectionTitle": "Termination",
  "content": "...",
  "parentSection": "General Terms"
}
```

## Entrega

Uma pergunta retorna resposta grounded, com citations verificáveis, e o relatório compara pelo menos uma configuração de chunking fixo com uma estrutural.

## Definition of done

- [ ] O RAG responde apenas com os chunks fornecidos.
- [ ] O caso sem evidência suficiente é tratado explicitamente.
- [ ] Toda citation aponta para documento, seção, página ou offset.
- [ ] Experimentos de tamanho e overlap estão registrados.
- [ ] A configuração escolhida é justificada pelos evals.
