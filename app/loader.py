import pandas as pd

class Loader:
    def __init__(self, csv_path, index):
        self.csv_path = csv_path
        self.index = index

    def load_df(self):
        df = pd.read_csv(self.csv_path)
        df["TweetID"] = df["TweetID"].astype("Int64").astype(str)
        df["CreateDate"] = pd.to_datetime(df["CreateDate"]).dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        df["text"] = df["text"].fillna("")
        return df

    def generate_actions(self, df):
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
