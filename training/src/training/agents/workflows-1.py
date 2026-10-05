from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]
MODEL_NAME = "openai/gpt-oss-120b"

load_dotenv(WORKSPACE_ROOT / ".env")

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
)

# Workflow: Prompt Chaining


class ExtracaoEvento(BaseModel):
    descricao: str = Field(
        description="Descrição bruta do evento",
    )
    eh_event_calendario: bool = Field(
        description="Se este texto descreve um evento de calendário",
    )
    pontuacao_confiaca: float = Field(description="Potuação de confianla entre 0 e 1")


class DetalhesEvento(BaseModel):
    nome: str = Field(
        description="Nome de evento",
    )
    data: str = Field(
        description="Data e hora do evento. Uso formato ISO 8601 para este valor.",
    )
    duracao_minutos: int | None = Field(
        description="Duração esperado em minutos.",
    )
    participantes: list[str] = Field(
        description="Lista de participantes.",
    )


class ConfirmacaoEvento(BaseModel):
    mensagem_confirmacao: str = Field(
        description="Mensagem de confirmação em linguagem natural.",
    )
    link_calendario: str | None = Field(
        description="Link do calendário gerado se aplicável.",
    )


def extrair_informacao_evento(entrada_usuario: str) -> ExtracaoEvento:
    hoje = datetime.now(timezone.utc)
    contexto_data = f"Hoje é {hoje.strftime('%A, %d de %B de %Y')}"

    response = client.responses.parse(
        model=MODEL_NAME,
        input=f"{contexto_data} analise se o texto descreve um evento de calendário",
        instructions=f"Extraia informações sobre um possível evento desse texto: {entrada_usuario}",
        text_format=ExtracaoEvento,
    )
    return response.output_parsed


def analisar_datalhes_evento(descricao: str) -> DetalhesEvento:
    hoje = datetime.now(timezone.utc)
    contexto_data = f"Hoje é {hoje.strftime('%A, %d de %B de %Y')}"

    response = client.responses.parse(
        model=MODEL_NAME,
        input=f"{contexto_data} extraia informações datalhadas do evento. Quando as datas fizerem referência, a 'próxima terça-feita' ou datas relativas similares, use data atual como referência",
        instructions=f"Extraia detalhes extruturados deste texto de evento {descricao}",
        text_format=DetalhesEvento,
    )
    return response.output_parsed


def gerar_confirmacao(detalhes_evento: DetalhesEvento) -> ConfirmacaoEvento:
    response = client.responses.parse(
        model=MODEL_NAME,
        input="Gere uma mensagem de confirmação natural para o evento. Assine a mensagem com seu nome: Skynet",
        instructions=f"Crie uma confirmação para este evento: {detalhes_evento.model_dump()}",
        text_format=ConfirmacaoEvento,
    )
    return response.output_parsed


def processar_solicitacao_calendario(entrada_usuario: str) -> ConfirmacaoEvento | None:
    extracao_inicial = extrair_informacao_evento(entrada_usuario=entrada_usuario)

    if (
        not extracao_inicial.eh_event_calendario
        or extracao_inicial.pontuacao_confiaca < 0.7
    ):
        return None

    detalhes_eventos = analisar_datalhes_evento(extracao_inicial.descricao)
    confirmacao = gerar_confirmacao(detalhes_eventos)

    return confirmacao


def exemplo_sucesso():
    entrada_usuario = """
    Vamos fazer uma transmissão ao vivo na próxima segunda-feira às 20h 
    com Daniel e Alberto para apresentar o lançamento do novo curso,
    deve durar umas 2 horas.
"""

    resultado = processar_solicitacao_calendario(entrada_usuario)
    if resultado:
        print(f"Confirmação: {resultado.mensagem_confirmacao}")
        if resultado.link_calendario:
            print(f"Link do calendário: {resultado.link_calendario}")
    else:
        print("Isso não parece ser uma solicitação de evento de calendário")


def exemplo_falha():
    entrada_usuario = """
    Você pode enviar um email para Daniel e Alberto para discutir o roteiro do projeto?
"""

    resultado = processar_solicitacao_calendario(entrada_usuario)
    if resultado:
        print(f"Confirmação: {resultado.mensagem_confirmacao}")
        if resultado.link_calendario:
            print(f"Link do calendário: {resultado.link_calendario}")
    else:
        print("Isso não parece ser uma solicitação de evento de calendário")


exemplo_sucesso()
print("###")
exemplo_falha()
