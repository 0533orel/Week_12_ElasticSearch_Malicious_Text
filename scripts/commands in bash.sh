#!/bin/bash

# Cleanup leftovers (optional, just prevents name collisions):
docker rm -f mt-api es8 2>/dev/null || true
docker network rm esnet 2>/dev/null || true

# Building the API image:
docker build -t malicious-text-api:latest .

# Creating a shared network:
docker network create esnet 2>/dev/null || true

# Elasticsearch (8.15.0) on the same network:
docker run -d --name es8 --network esnet \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "xpack.license.self_generated.type=trial" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  -p 9200:9200 -p 9300:9300 \
  docker.elastic.co/elasticsearch/elasticsearch:8.15.0

# Wait for it to be ready (health check from the same network):
docker run --rm --network esnet curlimages/curl:8.7.1 -sS --retry 30 --retry-delay 2 http://es8:9200

# The API (talks to http://es8:9200):
docker run -d --name mt-api --network esnet -p 8000:8000 \
  --restart unless-stopped \
  -e ES_URL=http://es8:9200 \
  -e INDEX_NAME=malicious_text \
  -e CSV_PATH="data/tweets.csv" \
  -e WEAPON_LIST_PATH="data/weapon_list.txt" \
  -e INIT_DATA=true \
  -e FORCE_RECREATE=false \
  malicious-text-api:latest


# Tests:
curl http://localhost:8000/status
curl "http://localhost:8000/clean-data?limit=50"
curl http://localhost:8000/antisemitic-with-weapons
curl http://localhost:8000/two-or-more-weapons
