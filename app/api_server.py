from fastapi import FastAPI, Request

class ApiServer:
    def __init__(self, manager):
        self.mgr = manager
        self.app = FastAPI(title="Malicious Text API")
        self._register_routes()

    def _register_routes(self):
        app = self.app
        mgr = self.mgr

        @app.get("/status")
        def status():
            return mgr.status()

        @app.get("/antisemitic-with-weapons")
        def antisemitic_with_weapons():
            st = mgr.status()
            if not st.get("processed"):
                return {
                    "message": "הנתונים טרם עובדו בשלמות. יש להריץ add_sentiment + tag_weapons.",
                    "counts": st.get("counts", {})
                }
            return mgr.query_antisemitic_with_weapons()

        @app.get("/two-or-more-weapons")
        def two_or_more_weapons():
            st = mgr.status()
            if not st.get("processed"):
                return {
                    "message": "הנתונים טרם עובדו בשלמות. יש להריץ add_sentiment + tag_weapons.",
                    "counts": st.get("counts", {})
                }
            return mgr.query_two_or_more_weapons()

        @app.get("/clean-data")
        def clean_data(request: Request):
            limit_raw = request.query_params.get("limit")
            try:
                limit = int(limit_raw) if limit_raw is not None else 0
            except Exception:
                limit = 0
            return mgr.get_all_clean(limit=limit)
