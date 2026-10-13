import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from mem0 import Memory
from openai import OpenAI

APP_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = APP_ROOT.parents[3]

load_dotenv(WORKSPACE_ROOT / ".env")

MODEL_NAME = "openai/gpt-oss-20b"
QDRANT_API_URL = os.getenv("QDRANT_API_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

config = {
    "llm": {
        "provider": "openai",
        "config": {
            "openai_base_url": GROQ_API_URL,
            "api_key": GROQ_API_KEY,
            "model": MODEL_NAME,
            "temperature": 0,
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "memory",
            "url": QDRANT_API_URL,
            "api_key": QDRANT_API_KEY,
            "embedding_model_dims": 384,
        },
    },
    "embedder": {
        "provider": "fastembed",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2",
        },
    },
}

client = OpenAI(base_url=GROQ_API_URL, api_key=GROQ_API_KEY)
memory = Memory.from_config(config)


def chat_with_memories(message: str, user_id: str = "danilo") -> str:
    relevant_memories = memory.search(
        query=message,
        filters={"user_id": user_id},
        top_k=3,
    )
    results = relevant_memories.get("results", [])
    memories_str = "\n".join(f"- {entry.get('memory', '')}" for entry in results)

    input_prompt = f"""Você é um assistente pessoal.
    Responda a pergunta consideerando as memórias do usuário.
    Memórias do usuário {memories_str}.
    Pergunta {message}
    """

    response = client.responses.create(
        model=MODEL_NAME,
        input=input_prompt,
    )

    assistent_response = response.output_text

    messages = [
        {
            "role": "user",
            "content": message,
        },
        {
            "role": "assistant",
            "content": assistent_response,
        },
    ]

    memory.add(messages, user_id=user_id)

    return assistent_response


def main():
    print("Chat com IA (digite 'sair' para encerrar)")
    while True:
        user_input = input("Você: ").strip()
        if user_input.lower() == "sair":
            print("Adeus!")
            break

        ai_response = chat_with_memories(user_input)
        print(f"IA: {ai_response}")


if __name__ == "__main__":
    main()
