import shelve
import os
from platformdirs import user_config_dir
from typing import Dict, Any, Optional, List

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

def store_last_operation(operation_data: Dict[str, Any]):
    set_config("last_operation", operation_data)

def get_last_operation() -> Dict[str, Any]:
    return get_config().get("last_operation", {})

def clear_last_operation():
    set_config("last_operation", {})

def store_file_version(file_path: str, content: str):
    with shelve.open(CONFIG_FILE, writeback=True) as config:
        if "file_versions" not in config:
            config["file_versions"] = {}
        config["file_versions"][file_path] = content

def get_file_version(file_path: str) -> Optional[str]:
    with shelve.open(CONFIG_FILE) as config:
        return config.get("file_versions", {}).get(file_path)

def clear_file_versions():
    with shelve.open(CONFIG_FILE, writeback=True) as config:
        if "file_versions" in config:
            del config["file_versions"]
            
def init_config():
    if not get_config():
        set_config("llm_provider", "anthropic")
        set_config("llm_model", "claude-3-5-sonnet-20240620")

def store_succeed_operation(operation_data: Dict[str, Any]):
    with shelve.open(CONFIG_FILE, writeback=True) as config:
        if "succeed_operations" not in config:
            config["succeed_operations"] = []
        config["succeed_operations"].append(operation_data)

def get_succeed_operations() -> List[Dict[str, Any]]:
    with shelve.open(CONFIG_FILE) as config:
        return config.get("succeed_operations", [])

def clear_succeed_operations():
    with shelve.open(CONFIG_FILE, writeback=True) as config:
        if "succeed_operations" in config:
            del config["succeed_operations"]

# Initialize config on import
init_config()