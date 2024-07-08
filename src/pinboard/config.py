import shelve
import os
from platformdirs import user_config_dir

CONFIG_DIR = user_config_dir("pinboard")
CONFIG_FILE = f"{CONFIG_DIR}/config"

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def get_config():
    ensure_config_dir()
    try:
        with shelve.open(CONFIG_FILE) as config:
            return dict(config)
    except Exception as e:
        print(f"Error reading config: {e}")
        return {}

def set_config(key, value):
    ensure_config_dir()
    try:
        with shelve.open(CONFIG_FILE, writeback=True) as config:
            config[key] = value
    except Exception as e:
        print(f"Error writing config: {e}")

def set_llm_config(model):
    if not model.startswith("anthropic/"):
        raise ValueError("Only Anthropic models are supported at the moment.")
    set_config("llm_provider", "anthropic")
    set_config("llm_model", model.split("/")[1])

def get_llm_config():
    config = get_config()
    return {
        "provider": config.get("llm_provider", "anthropic"),
        "model": config.get("llm_model", "claude-3-5-sonnet-20240620")
    }

def init_config():
    if not get_config():
        set_config("llm_provider", "anthropic")
        set_config("llm_model", "claude-3-5-sonnet-20240620")

# Initialize config on import
init_config()