from elasticsearch import Elasticsearch, helpers

class ESClient:
    """Thin wrapper around the Elasticsearch Python client."""

    def __init__(self, es_url):
        """Create a sync Elasticsearch client for the given URL."""
        self.client = Elasticsearch(es_url)

    def index_exists(self, index):
        """Return True if the index exists."""
        return self.client.indices.exists(index=index)

    def drop_index(self, index):
        """Delete an index if it exists (ignore 404)."""
        self.client.indices.delete(index=index, ignore=[404])

    def create_index(self, index, mapping):
        """Create an index with the provided mapping/settings."""
        self.client.indices.create(index=index, body=mapping)

    def refresh(self, index):
        """Force a refresh so new docs are searchable."""
        self.client.indices.refresh(index=index)

    def bulk_index(self, actions):
        """Stream bulk indexing actions to Elasticsearch."""
        helpers.bulk(self.client, actions)

    def update_by_query(self, index, body):
        """Run update-by-query with the given request body."""
        return self.client.update_by_query(index=index, body=body, conflicts="proceed", refresh=True)

    def delete_by_query(self, index, body):
        """Run delete-by-query with the given request body."""
        return self.client.delete_by_query(index=index, body=body, conflicts="proceed", refresh=True)

    def search(self, index, body):
        """Run a search request and return raw ES response."""
        return self.client.search(index=index, body=body)

    def count(self, index, query=None):
        """Return count of documents (optionally using a query filter)."""
        if query is None:
            res = self.client.count(index=index)
        else:
            res = self.client.count(index=index, query=query)
        return int(res.get("count", 0))
