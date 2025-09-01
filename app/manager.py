from config import Config
from es_client import ESClient
from loader import Loader
from processing import Processing

MAPPING = {
  "settings": {
    "analysis": {
      "analyzer": {
        "english_lc": { "type": "standard", "stopwords": "_english_" }
      }
    }
  },
  "mappings": {
    "properties": {
      "tweet_id":        {"type": "keyword"},
      "created_at":      {"type": "date"},
      "text": {
        "type": "text",
        "analyzer": "english_lc",
        "fields": {
          "raw": {"type": "keyword", "ignore_above": 256}
        }
      },
      "antisemitic":     {"type": "boolean"},
      "sentiment":       {"type": "keyword"},
      "sentiment_score": {"type": "float"},
      "weapons":         {"type": "keyword"},
      "weapon_count":    {"type": "integer"}
    }
  }
}

class Manager:
    def __init__(self, config=None):
        self.cfg = config or Config()
        self.es = ESClient(self.cfg.es_url)
        self.loader = Loader(self.cfg.csv_path, self.cfg.index_name)
        self.proc = Processing(self.es, self.cfg.index_name)

    def bootstrap(self):
        if self.es.index_exists(self.cfg.index_name):
            self.es.drop_index(self.cfg.index_name)
        self.es.create_index(self.cfg.index_name, MAPPING)

    def load_csv(self):
        df = self.loader.load_df()
        self.es.bulk_index(self.loader.generate_actions(df))
        self.es.refresh(self.cfg.index_name)

    def add_sentiment(self):
        self.proc.add_sentiment()

    def tag_weapons(self):
        weapons = self._read_weapon_list(self.cfg.weapon_list_path)
        self.proc.tag_weapons(weapons)

    def cleanup(self):
        self.proc.prune_uninteresting()

    def status(self):
        missing_sent = self.es.count(self.cfg.index_name, {"bool": {"must_not": [ {"exists": {"field": "sentiment"}} ]}})
        missing_weps = self.es.count(self.cfg.index_name, {"bool": {"must_not": [ {"exists": {"field": "weapon_count"}} ]}})
        total = self.es.count(self.cfg.index_name)
        return {
            "processed": (missing_sent == 0 and missing_weps == 0),
            "counts": {"missing_sentiment": missing_sent, "missing_weapon_count": missing_weps},
            "total": total
        }

    def query_antisemitic_with_weapons(self, size=200):
        body = {
          "query": {
            "bool": {
              "must": [
                {"term": {"antisemitic": True}},
                {"range": {"weapon_count": {"gte": 1}}}
              ]
            }
          },
          "_source": ["tweet_id","created_at","text","antisemitic","sentiment","sentiment_score","weapons","weapon_count"],
          "size": size
        }
        res = self.es.search(self.cfg.index_name, body)
        return [h["_source"] for h in res.get("hits", {}).get("hits", [])]

    def query_two_or_more_weapons(self, size=200):
        body = {
          "query": {"range": {"weapon_count": {"gte": 2}}},
          "_source": ["tweet_id","created_at","text","antisemitic","sentiment","sentiment_score","weapons","weapon_count"],
          "size": size
        }
        res = self.es.search(self.cfg.index_name, body)
        return [h["_source"] for h in res.get("hits", {}).get("hits", [])]

    def _read_weapon_list(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
