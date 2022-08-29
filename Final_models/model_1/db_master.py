import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

path_data = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Passation\data"

class DB_Master:
    def __init__(self, name:str, lang:str = "en"):
            self.name = name
            self.lang = lang
            self.find_db()

    def find_db(self):
        try:
            db_name = self.name + "_" + self.lang
            self.db = pd.read_csv(path_data+ "\\" + db_name + ".csv")
            self.found_db = True
            print("Found existing DB")
        except:
            self.found_db = False
            print("No existing DB")

    def find_last_date(self):
        if self.found_db:
            return self.db.Date.to_list()[0]
        else:
            return "8/26/2005  10:15:56 AM"

    def date_interval(self):
        print("The DataBase we have is from: ", str(self.db.Date.to_list()[-1]), "to: ", str(self.db.Date.to_list()[0]))

    def save_df(self, db_name, df):
        try:
            old_db = pd.read_csv(path_data + "/" + db_name + ".csv")
            new_db = pd.concat([df, old_db], ignore_index=True)
            new_db.to_csv(path_data+ "/" + db_name + ".csv")
        except:
            df.to_csv(path_data+ "/" + db_name +".csv")

    def fit(self, sdate, edate):
        return self.db[(self.db.Date >= sdate) & (self.db.Date <= edate)]        
    

    def save_log(self, df, df_name):
        file_name = df_name + "_log"
        create_list = ["C" for i in range(len(df))]
        df["log"] = create_list
        df.to_csv(path_data + "\\" + file_name + ".csv")
        
    # def save_log(self, topicer):
    #     dir_name = path_logs + "\\" + self.name+"_"+self.lang
    #     if not os.path.exists(dir_name):
    #         os.mkdir(dir_name)
    #     now = datetime.now()
    #     now = now.strftime("%d_%m_%Y_%H_%M_%S")
    #     dir = dir_name+"\\"+now
    #     if not os.path.exists(dir):
    #         os.mkdir(dir)
    #     topicer.df.to_csv(dir+"\\"+"data.csv")
    #     self.save_dict(dir, topicer.topics_sentiment, "sentiment")
    #     self.save_dict(dir, topicer.topics_keywords, "keywords")
    #     self.save_dict(dir, topicer.topics_hashtags, "hashtags")
   
    # @staticmethod
    # def save_dict(dir, dict, name):
    #     my_json = json.dumps(dict)
    #     # open file for writing, "w" 
    #     f = open(dir+"\\"+name+".json","w")
    #     # write json object to file
    #     f.write(my_json)
    #     # close file
    #     f.close()