import os
import yaml

_CONFIG = None

def load_config(path=None):
    global _CONFIG
    if _CONFIG is not None:
        return _CONFIG
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "config.yaml")
    with open(path) as f:
        _CONFIG = yaml.safe_load(f)
    return _CONFIG

def get_dsn(cfg=None):
    if cfg is None:
        cfg = load_config()
    db = cfg["database"]
    return f"{db['host']}:{db['port']}/{db['service']}"

def get_db_user(cfg=None):
    if cfg is None:
        cfg = load_config()
    return cfg["database"]["user"]

def get_db_owner(cfg=None):
    if cfg is None:
        cfg = load_config()
    return cfg["database"].get("owner", cfg["database"]["user"])
