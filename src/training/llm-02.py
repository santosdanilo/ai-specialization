import openai

client = openai.OpenAI(base_url="https://api.groq.com/openai/v1")

response = client.responses.create(
    model="openai/gpt-oss-120b",
    instructions="Responsda de forma simples em apenas 1 parágrafo curto.",
    input="O que é machine learning",
    temperature=1,
    top_p=1,
)

print(response.output_text)
