import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

path_logs = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model\topics_logs"
path_embed_db = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model\db\embeddings"
path_docs_db = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model\db\tweets"

class DB_Master:
    def __init__(self, name:str, lang:str = "en"):
            self.name = name
            self.lang = lang
            self.find_db()

    def find_db(self):
        try:
            db_name = self.name + "_" + self.lang
            self.db = pd.read_csv(path_docs_db + "/" + db_name + ".csv")
            self.found_db = True
            print("Found existing DB")
        except:
            self.found_db = False
            print("No existing DB")

    def fit(self, sdate, edate):
        self.df = self.db_interval(sdate, edate)
        db_embed = self.find_embed()
        self.embed = self.embed_interval(db_embed)
    
    def date_interval(self):
        print("The DataBase we have is from: ", str(self.db.Date.to_list()[-1]), "to: ", str(self.db.Date.to_list()[0]))

    def db_interval(self, sdate, edate):
        return self.db[(self.db.Date >= sdate) & (self.db.Date <= edate)]
    
    def find_embed(self):
        name = self.name + "_" + self.lang
        return np.load(path_embed_db +"/"+name+".npy")

    def embed_interval(self, db_embed):
        s_idx = int(self.df.index[0])
        e_idx = int(self.df.index[-1])
        self.df = self.df.reset_index(drop=True)
        return db_embed[s_idx:e_idx+1]

    def save_log(self, topicer):
        dir_name = path_logs + "\\" + self.name+"_"+self.lang
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        now = datetime.now()
        now = now.strftime("%d_%m_%Y_%H_%M_%S")
        dir = dir_name+"\\"+now
        if not os.path.exists(dir):
            os.mkdir(dir)
        topicer.df.to_csv(dir+"\\"+"data.csv")
        self.save_dict(dir, topicer.topics_sentiment, "sentiment")
        self.save_dict(dir, topicer.topics_keywords, "keywords")
        self.save_dict(dir, topicer.topics_hashtags, "hashtags")
   
    @staticmethod
    def save_dict(dir, dict, name):
        my_json = json.dumps(dict)
        # open file for writing, "w" 
        f = open(dir+"\\"+name+".json","w")
        # write json object to file
        f.write(my_json)
        # close file
        f.close()