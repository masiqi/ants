from openai import OpenAI

client = OpenAI(api_key="<DeepSeek API Key>", base_url="http://10.1.0.242:11434/v1")

response = client.chat.completions.create(
    model="qwen2.5:14b-instruct-q4_0",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)
