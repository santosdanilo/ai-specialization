from groq import Groq

client = Groq()
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": "Atue como um especialista em machine learning",
        },
        {
            "role": "user",
            "content": "O que é ,de forma simples machine learning?",
        },
    ],
    temperature=1,
    top_p=1,
)
print(response.choices[0].message.content)
