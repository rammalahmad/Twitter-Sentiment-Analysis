import pandas as pd
import numpy as np

path_docs_db = ""
path_embed_db = ""

class DB_Master:
    def __init__(self, name:str, sdate, edate, lang:str = "en"):
            self.name = name
            self.lang = lang
            self.sdate = sdate
            self.edate = edate

    def fit(self):
        db = self.find_db()
        db_embed = self.find_embed()
        self.df = self.db_interval(db)
        self.embed = self.embed_interval(db_embed)
        
    def find_db(self):
        db_name = self.name + "_" + self.lang
        return pd.read_csv(path_docs_db + "/" + db_name)
    
    def db_interval(self, db):
        return db[db.Date >= self.sdate & db.Date <=self.edate]
    
    def find_embed(self):
        name = self.name + "_" + self.lang
        return np.load(path_embed_db +"/"+name)

    def embed_interval(self, db_embed):
        s_idx = int(self.df.index[0])
        e_idx = int(self.df.index[-1])
        self.df.reset_index()
        return db_embed[s_idx:e_idx+1]