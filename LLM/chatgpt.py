from openai import OpenAI
import os


def get_openai_response(text, key, stream=False, max_tokens=1000):
    client = OpenAI(api_key=key)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        stream=stream,
        max_tokens=max_tokens,
    )
    if stream:
        return completion
    return completion.choices[0].message.content
