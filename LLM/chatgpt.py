import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise Exception("OPENAI_API_KEY is not set. Set it as an environment variable.")


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
