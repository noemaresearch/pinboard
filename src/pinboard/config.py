import shelve
from platformdirs import user_config_dir

CONFIG_DIR = user_config_dir("pinboard")
CONFIG_FILE = f"{CONFIG_DIR}/config"

def get_config():
    with shelve.open(CONFIG_FILE) as config:
        return dict(config)

def set_config(key, value):
    with shelve.open(CONFIG_FILE, writeback=True) as config:
        config[key] = value

def set_llm_config(model):
    if not model.startswith("anthropic/"):
        raise ValueError("Only Anthropic models are supported at the moment.")
    set_config("llm_provider", "anthropic")
    set_config("llm_model", model.split("/")[1])

def get_llm_config():
    config = get_config()
    return {
        "provider": config.get("llm_provider"),
        "model": config.get("llm_model", "claude-3-5-sonnet-20240620")
    }