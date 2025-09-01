# Malicious Text API (Elasticsearch + FastAPI)

A small, OOP-style Python service that ingests a tweets CSV, enriches each row (sentiment + weapon keywords), stores the data in **Elasticsearch**, and exposes a simple **FastAPI** for querying.

## What it does
- **Load** `data/tweets.csv` (with mixed date formats handled) and index into Elasticsearch.
- **Enrich**: sentiment (NLTK VADER) → `sentiment`, `sentiment_score`; weapon tagging (list from `data/weapon_list.txt`) → `weapons`, `weapon_count`.
- **Cleanup**: remove uninteresting docs (non-antisemitic **and** neutral/positive **and** no weapons).
- **Serve**: simple HTTP endpoints for status and queries.

## Project layout
```
app/
  api_server.py     # FastAPI wrapped in ApiServer class (routes)
  config.py         # environment-based settings
  es_client.py      # thin wrapper over Elasticsearch client
  loader.py         # CSV loading + date parsing (mixed formats -> ISO8601 UTC)
  main.py           # create Manager, optional init_data(), and build app
  manager.py        # pipeline orchestration + ES index mapping + queries
  processing.py     # VADER sentiment, weapons tagging (Painless), cleanup
data/
  tweets.csv
  weapon_list.txt
```

## API Endpoints
- `GET /status` — processing progress and totals.
- `GET /clean-data?limit=N` — all docs currently in the index (after cleanup). Add `?limit=` to cap results.
- `GET /antisemitic-with-weapons` — antisemitic docs that mention ≥1 weapon.
- `GET /two-or-more-weapons` — docs that mention ≥2 different weapons.

## Elasticsearch index mapping (summary)
Fields: `tweet_id (keyword)`, `created_at (date)`, `text (text, analyzer=english_lc + .raw)`, `antisemitic (boolean)`, `sentiment (keyword)`, `sentiment_score (float)`, `weapons (keyword)`, `weapon_count (integer)`.

## Quick start (Docker)
Build the image and run both services on the same Docker network.

```bash
# build
docker build -t malicious-text-api:latest .

# network
docker network create esnet 2>/dev/null || true

# Elasticsearch
docker run -d --name es8 --network esnet   -e "discovery.type=single-node"   -e "xpack.security.enabled=false"   -e "xpack.license.self_generated.type=trial"   -e "ES_JAVA_OPTS=-Xms1g -Xmx1g"   -p 9200:9200 -p 9300:9300   docker.elastic.co/elasticsearch/elasticsearch:8.15.0

# (optional) wait for ES
docker run --rm --network esnet curlimages/curl:8.7.1 -sS --retry 30 --retry-delay 2 http://es8:9200

# API (talks to http://es8:9200)
docker run -d --name mt-api --network esnet -p 8000:8000   --restart unless-stopped   -e ES_URL=http://es8:9200   -e INDEX_NAME=malicious_text   -e CSV_PATH="data/tweets.csv"   -e WEAPON_LIST_PATH="data/weapon_list.txt"   -e INIT_DATA=true   -e FORCE_RECREATE=false   malicious-text-api:latest
```

Now visit:
```
http://localhost:8000/status
http://localhost:8000/clean-data?limit=50
http://localhost:8000/antisemitic-with-weapons
http://localhost:8000/two-or-more-weapons
```

## Local development (no Docker)
```bash
pip install -r requirements.txt
hypercorn app.main:app --bind 0.0.0.0:8000
```

## Configuration
All settings can be provided via env vars (defaults in parentheses):
- `ES_URL` (`http://localhost:9200`)
- `INDEX_NAME` (`malicious_text`)
- `CSV_PATH` (`data/tweets.csv`)
- `WEAPON_LIST_PATH` (`data/weapon_list.txt`)
- `INIT_DATA` (`true`) — run pipeline on startup
- `FORCE_RECREATE` (`false`) — drop & rebuild the index on startup

## Notes
- On startup (when `INIT_DATA=true`) the app may take a short time to load and enrich data.
- The cleanup step removes only “non-interesting” items: non-antisemitic + neutral/positive + no weapons.
- Dates are parsed from mixed formats and normalized to ISO8601 UTC.
