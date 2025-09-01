import os

class Config:
    """Holds runtime configuration (ES URL, index name, local paths)."""

    def __init__(self):
        """Initialize config values; can be overridden via environment variables."""
        self.es_url = os.environ.get("ES_URL", "http://localhost:9200")
        self.index_name = os.environ.get("INDEX_NAME", "malicious_text")
        self.csv_path = os.environ.get("CSV_PATH", "data/tweets.csv")
        self.weapon_list_path = os.environ.get("WEAPON_LIST_PATH", "data/weapon_list.txt")

        self.init_data = os.environ.get("INIT_DATA", "true").lower() == "true"
        self.force_recreate = os.environ.get("FORCE_RECREATE", "false").lower() == "true"

        try:
            self.app_port = int(os.environ.get("APP_PORT", "8000"))
        except Exception:
            self.app_port = 8000
