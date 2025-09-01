from fastapi import FastAPI, Request

class ApiServer:
    """Wraps the FastAPI app and wires routes to the Manager."""

    def __init__(self, manager):
        """Keep a Manager instance, build the FastAPI app, register routes."""
        self.mgr = manager
        self.app = FastAPI(title="Malicious Text API")
        self._register_routes()

    def _register_routes(self):
        """Register all HTTP endpoints on the FastAPI app."""
        app = self.app
        mgr = self.mgr

        @app.get("/status")
        def status():
            """Return processing status and counters."""
            return mgr.status()

        @app.get("/antisemitic-with-weapons")
        def antisemitic_with_weapons():
            """Return antisemitic docs that mention at least one weapon."""
            st = mgr.status()
            if not st.get("processed"):
                return {
                    "message": "The data has not yet been fully processed. You must run add_sentiment + tag_weapons.",
                    "counts": st.get("counts", {})
                }
            return mgr.query_antisemitic_with_weapons()

        @app.get("/two-or-more-weapons")
        def two_or_more_weapons():
            """Return docs that mention two or more weapons."""
            st = mgr.status()
            if not st.get("processed"):
                return {
                    "message": "The data has not yet been fully processed. You must run add_sentiment + tag_weapons.",
                    "counts": st.get("counts", {})
                }
            return mgr.query_two_or_more_weapons()

        @app.get("/clean-data")
        def clean_data(request: Request):
            """Return cleaned/kept documents (optionally limited via ?limit=N)."""
            limit_raw = request.query_params.get("limit")
            try:
                limit = int(limit_raw) if limit_raw is not None else 0
            except Exception:
                limit = 0
            return mgr.get_all_clean(limit=limit)
