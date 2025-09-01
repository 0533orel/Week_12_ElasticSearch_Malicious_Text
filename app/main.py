from .manager import Manager
from .api_server import ApiServer

def init_data(mgr):
    """Optionally (INIT_DATA) bootstrap/load/enrich/cleanup the dataset on startup."""
    if not mgr.cfg.init_data:
        return

    index_name = mgr.cfg.index_name
    exists = mgr.es.index_exists(index_name)
    count = 0
    if exists:
        try:
            count = mgr.es.count(index_name)
        except Exception:
            count = 0

    if mgr.cfg.force_recreate or (not exists) or (count == 0):
        mgr.bootstrap()
        mgr.load_csv()

    mgr.add_sentiment()
    mgr.tag_weapons()
    mgr.cleanup()

def create_app():
    """Create Manager, initialize data (if enabled), build and return the FastAPI app."""
    mgr = Manager()
    init_data(mgr)
    api = ApiServer(mgr)
    return api.app

app = create_app()
