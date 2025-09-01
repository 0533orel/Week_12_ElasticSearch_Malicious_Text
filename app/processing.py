from elasticsearch import helpers
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


try:
    nltk.data.find("sentiment/vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")


class Processing:
    """Implements enrichment and cleanup steps executed via Elasticsearch."""

    def __init__(self, es, index):
        """Keep ES client wrapper and target index name."""
        self.es = es
        self.index = index

    def add_sentiment(self, batch_size=500):
        """Compute VADER sentiment (compound) and label each doc."""
        sia = SentimentIntensityAnalyzer()

        query = {"query": {"bool": {"must_not": [{"exists": {"field": "sentiment"}}]}}}
        scan = helpers.scan(self.es.client, index=self.index, query=query, _source=["text"])

        actions = []
        updated = 0

        for doc in scan:
            src = doc.get("_source", {}) or {}
            text = src.get("text", "")
            if not isinstance(text, str):
                text = str(text or "")

            compound = 0.0
            if text.strip():
                scores = sia.polarity_scores(text)
                compound = float(scores.get("compound", 0.0))


            label = "neutral"
            if compound >= 0.05:
                label = "positive"
            elif compound <= -0.05:
                label = "negative"

            actions.append({
                "_op_type": "update",
                "_index": self.index,
                "_id": doc["_id"],
                "doc": {"sentiment": label, "sentiment_score": compound}
            })

            if len(actions) >= batch_size:
                helpers.bulk(self.es.client, actions)
                updated += len(actions)
                actions = []

        if actions:
            helpers.bulk(self.es.client, actions)
            updated += len(actions)

        self.es.refresh(self.index)
        return {"updated": updated}

    def tag_weapons(self, weapons):
        """Mark weapons found in text and compute weapon_count via painless."""
        weapons_list = [w.strip().lower() for w in weapons if w.strip()]
        body = {
          "script": {
            "lang": "painless",
            "params": { "weps": weapons_list },
            "source": '''
              if (ctx._source.text == null) return;
              String t = ctx._source.text.toLowerCase();
              String[] toks = /[\\W_]+/.split(t);
              Set found = new HashSet();
              for (w in toks) { if (params.weps.contains(w)) { found.add(w); } }
              ctx._source.weapons = new ArrayList(found);
              ctx._source.weapon_count = ctx._source.weapons.size();
            '''
          },
          "query": { "bool": { "must_not": [ { "exists": { "field": "weapon_count" } } ] } }
        }
        return self.es.update_by_query(self.index, body)

    def prune_uninteresting(self):
        """Delete docs that are non-antisemitic, neutral/positive, and weaponless."""
        body = {
          "query": {
            "bool": {
              "must": [
                {"term": {"antisemitic": False}},
                {"terms": {"sentiment": ["neutral","positive"]}},
                {"bool": {
                  "should": [
                    {"term": {"weapon_count": 0}},
                    {"bool": {"must_not": {"exists": {"field": "weapon_count"}}}}
                  ]
                }}
              ]
            }
          }
        }
        return self.es.delete_by_query(self.index, body)
