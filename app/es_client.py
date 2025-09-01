from elasticsearch import Elasticsearch, helpers

class ESClient:
    def __init__(self, es_url):
        self.client = Elasticsearch(es_url)

    def index_exists(self, index):
        return self.client.indices.exists(index=index)  # type: ignore

    def drop_index(self, index):
        self.client.indices.delete(index=index, ignore=[404])  # type: ignore

    def create_index(self, index, mapping):
        self.client.indices.create(index=index, body=mapping)  # type: ignore

    def refresh(self, index):
        self.client.indices.refresh(index=index)  # type: ignore

    def bulk_index(self, actions):
        helpers.bulk(self.client, actions)

    def update_by_query(self, index, body):
        return self.client.update_by_query(index=index, body=body, conflicts="proceed", refresh=True)  # type: ignore

    def delete_by_query(self, index, body):
        return self.client.delete_by_query(index=index, body=body, conflicts="proceed", refresh=True)  # type: ignore

    def search(self, index, body):
        return self.client.search(index=index, body=body)  # type: ignore

    def count(self, index, query=None):
        if query is None:
            res = self.client.count(index=index)  # type: ignore
        else:
            res = self.client.count(index=index, query=query)  # type: ignore
        return int(res.get("count", 0))
