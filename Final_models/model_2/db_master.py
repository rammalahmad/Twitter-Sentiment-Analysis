import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

path_data = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Final_models\model_2\data"

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

    def update_df(self, db_name, df):
        try:
            old_db = pd.read_csv(path_data + "/" + db_name + ".csv")
            new_db = pd.concat([df, old_db], ignore_index=True)
            new_db.to_csv(path_data+ "/" + db_name + ".csv", index=False)
        except:
            df.to_csv(path_data+ "/" + db_name +".csv", index=False)
    
    def save_df(self, db_name, df):
        df.to_csv(path_data+ "/" + db_name +".csv", index=False)

    def fit(self, sdate, edate):
        return self.db[(self.db.Date >= sdate) & (self.db.Date <= edate)]        

    def save_log(self, df, df_name):
        file_name = df_name + "_log"
        create_list = ["C" for i in range(len(df))]
        df["log"] = create_list
        df.to_csv(path_data + "\\" + file_name + ".csv", index=False)