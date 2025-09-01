import pandas as pd

class Loader:
    def __init__(self, csv_path, index):
        self.csv_path = csv_path
        self.index = index

    def load_df(self):
        df = pd.read_csv(self.csv_path)
        df["TweetID"] = df["TweetID"].astype("Int64").astype(str)
        raw = df["CreateDate"]
        try:
            dt = pd.to_datetime(raw, utc=True, format="mixed", errors="coerce")
        except TypeError:
            dt = pd.to_datetime(raw, utc=True, errors="coerce")

        ok = ~dt.isna()
        df = df.loc[ok].copy()
        dt = dt.loc[ok]

        df["CreateDate"] = dt.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        if "text" in df.columns:
            df["text"] = df["text"].fillna("").astype(str)
        else:
            df["text"] = ""

        return df

    def iter_bulk(self, df):
        for r in df.itertuples():
            yield {
              "_index": self.index,
              "_id": str(r.TweetID),
              "_source": {
                "tweet_id":   str(r.TweetID),
                "created_at": r.CreateDate,
                "text":       str(getattr(r, "text", "")),
                "antisemitic": bool(getattr(r, "Antisemitic", 0) == 1)
              }
            }
