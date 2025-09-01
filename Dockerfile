FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('vader_lexicon')"

COPY . .

ENV ES_URL=http://host.docker.internal:9200
ENV INDEX_NAME=malicious_text
ENV CSV_PATH=data/tweets.csv
ENV WEAPON_LIST_PATH=data/weapon_list.txt
ENV INIT_DATA=true
ENV FORCE_RECREATE=false

EXPOSE 8000

CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:8000"]
