from openai import OpenAI
import os


def full_prompt(context, text):
    return f"context: {context}\n\n user question:{text}"


def get_openai_response(text, key, stream=False, max_tokens=1000, prompt=""):
    client = OpenAI(api_key=key)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": full_prompt(prompt, text)}],
        stream=stream,
        max_tokens=max_tokens,
    )
    if stream:
        return completion
    return completion.choices[0].message.content
