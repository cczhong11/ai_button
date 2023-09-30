import openai
import os


def set_openai_key(key):
    openai.api_key = key


def get_openai_response(text, stream=False, max_tokens=1000):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        stream=stream,
        max_tokens=max_tokens,
    )
    if stream:
        return completion
    return completion.choices[0].message.content
