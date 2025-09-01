class Config:
    def __init__(self):
        self.ES_URL = "http://localhost:9200"
        self.INDEX_NAME = "malicious_text"
        self.CSV_PATH = "../data/tweets.csv"
        self.WEAPON_LIST_PATH = "../data/weapon_list.txt"
