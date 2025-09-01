import os
from manager import Manager
from api_server import ApiServer

def init_data(mgr):
    init_flag = os.environ.get("INIT_DATA", "true").lower() == "true"
    if not init_flag:
        return

    force = os.environ.get("FORCE_RECREATE", "false").lower() == "true"

    index_name = mgr.cfg.index_name
    exists = mgr.es.index_exists(index_name)
    count = 0
    if exists:
        try:
            count = mgr.es.count(index_name)
        except Exception:
            count = 0

    if force or (not exists) or (count == 0):
        mgr.bootstrap()
        mgr.load_csv()

    mgr.add_sentiment()
    mgr.tag_weapons()
    mgr.cleanup()

def create_app():
    mgr = Manager()
    init_data(mgr)
    api = ApiServer(mgr)
    return api.app

app = create_app()
