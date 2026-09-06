# Etapa 1 - Corpus jurídico e ground truth

## Objetivo

Criar um conjunto controlado de documentos jurídicos fictícios e perguntas com respostas conhecidas. O corpus existe antes do RAG para que o sistema possa ser medido sem depender de opiniões subjetivas.

## Corpus inicial

Comece com aproximadamente:

- 5 empresas fictícias;
- 4 a 5 documentos por empresa;
- total de 20 a 25 documentos.

Empresas:

- Acme Corp;
- Globex;
- Initech;
- Umbrella Systems;
- Wayne Analytics.

Estrutura de exemplo:

```text
test-data/contracts/

acme/
├── master-service-agreement.docx
├── master-service-agreement.pdf
├── amendment-01.docx
├── statement-of-work-01.docx
└── nda.docx

globex/
├── master-service-agreement.docx
├── amendment-termination.docx
├── statement-of-work-01.docx
└── nda.pdf
```

Use DOCX como fonte original e exporte parte dos documentos para PDF. Assim será possível comparar parsing, source mapping e edição de um arquivo editável com seu PDF derivado.

## Tipos de documentos

| Tipo | Quantidade inicial |
|---|---:|
| NDA | 3 |
| Master Service Agreement | 3 |
| Statement of Work | 3 |
| Amendment | 3 |
| Data Processing Agreement | 2 |
| Termination Notice | 1 |

Os documentos podem ser criados com Word, LibreOffice, Google Docs exportado, scripts de geração de DOCX ou LLMs. O conteúdo deve ser fictício e não conter dados jurídicos reais.

## Diferenças deliberadas

Inclua documentos que obriguem o retrieval a localizar e relacionar fontes.

Exemplo de alteração de cláusula:

```text
ACME MSA, SECTION 7 - TERM
The initial term of this Agreement shall be twenty-four (24) months.
```

```text
ACME AMENDMENT 01, SECTION 2 - MODIFICATION OF TERM
Section 7 of the Master Services Agreement is hereby amended.
The initial term shall be thirty-six (36) months.
```

Pergunta:

```text
What is the current term of the ACME agreement?
```

Resposta correta: `36 months`. O sistema precisa relacionar MSA, valor original e amendment aplicável.

## Dataset de avaliação

Criar `test-data/evals/questions.json`:

```json
[
  {
    "id": "q001",
    "question": "What is the current duration of the ACME agreement?",
    "expectedAnswer": "36 months",
    "relevantDocuments": ["acme-msa", "acme-amendment-01"],
    "relevantSections": ["MSA Section 7", "Amendment Section 2"]
  }
]
```

Meta inicial: aproximadamente 30 perguntas, sendo 10 semânticas, 10 de exact match, 5 cross-document e 5 adversariais.

Inclua exemplos de:

- **Semantic search:** “Can the customer terminate the contract without cause?” para um trecho sobre 60 dias de aviso;
- **Exact match:** busca pelo identificador `ACME-MSA-2026-047`, onde lexical search pode superar embeddings;
- **Cross-document reasoning:** MSA define limite de `$1M`, SOW herda o MSA e amendment altera para `$2M`; a resposta atual é `$2M`.

## Definition of done

- [ ] 20 a 25 documentos estão versionados ou reproduzivelmente geráveis.
- [ ] Há DOCX original e PDFs derivados em parte do corpus.
- [ ] Cada documento tem empresa, tipo, identificador e versão registrados.
- [ ] Existem cerca de 30 perguntas com resposta esperada e fontes relevantes.
- [ ] O corpus contém pelo menos um caso de amendment que substitui uma cláusula.
- [ ] Há perguntas que distinguem busca semântica de busca lexical.
