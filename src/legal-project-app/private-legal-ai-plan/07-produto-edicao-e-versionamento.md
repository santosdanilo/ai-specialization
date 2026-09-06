# Etapa 7 - Produto jurídico: pesquisa, edição e versionamento

## Fase 14 - Frontend

Crie três telas principais.

### Document Library

```text
Documents

✓ ACME MSA
✓ ACME Amendment #1
✓ Globex NDA

[ Upload document ]
```

### Research

```text
┌───────────────────────────────────┐
│ What is ACME's termination period?│
└───────────────────────────────────┘

30 days.

Sources
────────────────────────
ACME MSA
§14.2 · page 12

[View source]
```

### Source Viewer

```text
Page 12

Section 14 - Termination

...Either party may terminate
with thirty days written notice...
```

A fonte citada deve ficar destacada e a navegação deve preservar o identificador da citation.

## Fase 15 - Document editing

Para um pedido como:

```text
Change the termination notice from 30 to 60 days.
```

o LLM não edita diretamente o arquivo. Ele propõe uma alteração estruturada:

```json
{
  "documentId": "acme-msa",
  "operation": "replace",
  "section": "14.2",
  "original": "thirty (30) days",
  "replacement": "sixty (60) days",
  "reason": "Requested change to termination notice"
}
```

Frontend:

```diff
- thirty (30) days
+ sixty (60) days
```

Ações: `[Reject]` e `[Approve change]`.

Fluxo:

```text
LLM proposes
    ↓
structured patch
    ↓
diff
    ↓
human approval
    ↓
deterministic editor
    ↓
new document version
```

Regra: **LLM propõe. Software determinístico executa.**

## Fase 16 - Versionamento

Estrutura:

```text
 ├── v1
 ├── v2
 └── v3
```

Audit log:

```text
user
old_value
new_value
reason
```

Cada versão deve apontar para o arquivo, hash, autor, patch aprovado e estado do processamento. A edição precisa ser reprodutível e rejeitar patches que não encontrem o `original` esperado.

## Definition of done

- [ ] Usuário consegue subir, pesquisar e abrir uma fonte.
- [ ] Citation navega para trecho destacado.
- [ ] Alteração é exibida como diff antes da aprovação.
- [ ] Apenas uma aprovação humana cria nova versão.
- [ ] O editor determinístico não depende de uma nova decisão do LLM.
- [ ] Audit log registra quem, quando, o que mudou e por quê.
