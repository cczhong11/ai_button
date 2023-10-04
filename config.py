import dataclasses
import json
import os
import sys

PATH = os.path.dirname(sys.argv[0])


@dataclasses.dataclass
class AIConfig:
    generation_key1: str
    generation_key2: str
    openai_api_key: str


def read_config():
    if not os.path.exists(os.path.join(PATH, "config.json")):
        return AIConfig("Key.ctrl", "`", os.environ.get("OPENAI_API_KEY") or "")
    with open(os.path.join(PATH, "config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
    return AIConfig(**config)


def write_config(config: AIConfig):
    with open(os.path.join(PATH, "config.json"), "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(config), f, indent=4)
