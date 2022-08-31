import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

path_data = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Final_models\model_1\data"

class DB_Master:
    def __init__(self, name:str):
            self.name = name
            self.find_db()

    def find_db(self):
        '''
        # Info
        ---
        Find existing database for the company
        '''
        try:
            db_name = self.name
            self.db = pd.read_csv(path_data+ "\\" + db_name + ".csv")
            self.found_db = True
            print("Found existing DB")
        except:
            self.found_db = False
            print("No existing DB")

    def find_last_date(self):
        '''
        # Info
        ---
        Find the date of the most recent extacted tweet
        '''
        if self.found_db:
            return self.db.Date.to_list()[0]
        else:
            return "8/26/2005  10:15:56 AM"

    def date_interval(self):
        '''
        # Info
        ---
        Print the scrapped db time period
        '''
        print("The DataBase we have is from: ", str(self.db.Date.to_list()[-1]), "to: ", str(self.db.Date.to_list()[0]))

    def fit(self, sdate, edate):
        '''
        # Info
        ---
        Takes a certain time interval from the database
        # Params:
        ---
        sdate: str, the starting date that is considered
        edate: str, the ending date
        # Returns:
        ---
        A pandas df containing the tweets in this timeframe
        '''
        return self.db[(self.db.Date >= sdate) & (self.db.Date <= edate)] 

    def update_df(self, db_name:str, df:pd.DataFrame):
        '''
        # Info
        ---
        Updates existing csv by adding df to it
        # Params:
        ---
        db_name: str, name of the file
        df: pandas df, the df to add
        '''
        try:
            old_db = pd.read_csv(path_data + "/" + db_name + ".csv")
            new_db = pd.concat([df, old_db], ignore_index=True)
            new_db.to_csv(path_data+ "/" + db_name + ".csv", index=False)
        except:
            df.to_csv(path_data+ "/" + db_name +".csv", index=False)
    
    def save_df(self, db_name, df):
        '''
        # Info
        ---
        Saves df as csv or overwrites it
        # Params:
        ---
        db_name: str, name of the file
        df: pandas df, the df to save
        '''
        df.to_csv(path_data+ "/" + db_name +".csv", index=False)       