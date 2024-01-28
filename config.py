import dataclasses
import json
import os
import sys

USER_HOME = os.path.expanduser("~") + "/.ai_bottom"


@dataclasses.dataclass
class AIConfig:
    generation_key1: str
    generation_key2: str
    openai_api_key: str
    streaming: bool
    play_sound: bool
    system_prompt: str = ""


def read_config():
    if not os.path.exists(USER_HOME):
        os.mkdir(USER_HOME)
    if not os.path.exists(os.path.join(USER_HOME, "config.json")):
        return AIConfig(
            "Key.ctrl", "`", os.environ.get("OPENAI_API_KEY") or "", True, True
        )
    with open(os.path.join(USER_HOME, "config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
    for key in AIConfig.__dataclass_fields__.keys():
        if key not in config:
            if key == "streaming" or key == "play_sound":
                config[key] = True
            else:
                config[key] = ""
    return AIConfig(**config)


def write_config(config: AIConfig):
    with open(os.path.join(USER_HOME, "config.json"), "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(config), f, indent=4)
