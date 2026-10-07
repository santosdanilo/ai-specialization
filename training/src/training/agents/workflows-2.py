from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

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

# Workflow: Routing


class TipoSolicitacaoCalendario(BaseModel):
    tipo_solicitacao: Literal["novo_evento", "modificar_evento", "outro"] = Field(
        description="Tipo de solicitação de calendário sendo feita"
    )
    pontuacao_confianca: float = Field(description="Pontuação de confiança entre 0 e 1")
    descricao: str = Field(description="Descrição limpa da solicitação")


class DetalhesNovoEvento(BaseModel):
    nome: str = Field(description="Nome do evento")
    data: str = Field(description="Data e hora do evento (ISO 8601)")
    duracao_minutos: int = Field(description="Duração em minutos")
    participantes: list[str] = Field(description="Lista de participantes")


class Mudanca(BaseModel):
    campo: str = Field(description="Campo a ser alterado")
    novo_valor: str = Field(description="Novo valor para o campo")


class DetalhesModificarEvento(BaseModel):
    identificador_evento: str = Field(
        description="Descrição para identificar o evento existente"
    )
    mudancas: list[Mudanca] = Field(description="Lista de mudanças a fazer")
    participantes_adicionar: list[str] = Field(
        description="Novos participantes para adicionar"
    )
    participantes_remover: list[str] = Field(description="Participantes para remover")


class RespostaCalendario(BaseModel):
    sucesso: bool = Field(description="Se a operação foi bem-sucedida")
    mensagem: str = Field(description="Mensagem de resposta amigável ao usuário")
    link_calendario: str | None = Field(description="Link do calendário se aplicável")


def rotear_solicitacao_calendario(entrada_usuario: str) -> TipoSolicitacaoCalendario:
    response = client.responses.parse(
        model=MODEL_NAME,
        input="Determine se esta é uma solicitação para criar um novo evento de calendário ou modificar um existente.",
        instructions=f"Analise esta solicitação: '{entrada_usuario}'",
        text_format=TipoSolicitacaoCalendario,
    )
    return response.output_parsed
