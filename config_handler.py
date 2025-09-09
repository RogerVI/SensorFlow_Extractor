import json
import os

# Dossier commun pour la config
CONFIG_DIR = r"C:\Temp\API"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Flags en mémoire (si tu en as besoin ailleurs)
project_reuse_flags = {}  # { project_id or "global": True/False }

def ensure_config_dir():
    """Crée le dossier CONFIG_DIR si besoin."""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    """Charge le fichier config.json si présent, sinon retourne {}."""
    ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_config(config):
    """Sauvegarde le dictionnaire dans config.json."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_or_ask(key, fallback_value="", project_key=None, sensitive=False):
    """
    key : clé à chercher
    fallback_value : valeur proposée par défaut
    project_key : identifiant de projet (scope)
    sensitive : si True, ne sauvegarde jamais la valeur (ex: password)
    """
    config = load_config()
    scope_key = project_key if project_key else "global"
    scope = config.get(scope_key, {})

    if not sensitive and key in scope:
        return scope[key]

    if fallback_value:
        if not sensitive:  # <<< pas de sauvegarde des valeurs sensibles
            scope[key] = fallback_value
            config[scope_key] = scope
            save_config(config)
        return fallback_value

    return ""
