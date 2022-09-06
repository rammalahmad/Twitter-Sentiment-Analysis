from update_db.update_db import Update_DB
from esg_topic.esg_topic import ESG_Topic
from db_master import DB_Master
import pandas as pd

class Surf_Mes_Tweets:
    def __init__(self, name:str):
        self.name = name
        self.db_master = DB_Master(name=name)

    def refresh(self):
        # Find english tweets
        updater = Update_DB(name=self.name, lang="en", last_date=self.db_master.find_last_date())
        df_esg_en, df_not_esg_en = updater.fit()

        # Find french tweets
        updater = Update_DB(name=self.name, lang="fr", last_date=self.db_master.find_last_date())
        df_esg_fr, df_not_esg_fr = updater.fit()

        # Merge the french with english
        df_esg = pd.concat([df_esg_en, df_esg_fr], ignore_index=True)
        df_not_esg = pd.concat([df_not_esg_en, df_not_esg_fr], ignore_index=True)

        # Sort them per date
        df_esg.sort_values(by='Date', ascending = False, inplace=True)
        df_not_esg.sort_values(by='Date', ascending = False, inplace=True)

        # Add log create
        df_not_esg['log'] = 'C'
        df_esg['log'] = 'C'

        # Save the logs
        db_name = self.name
        self.db_master.update_df(df=df_esg, db_name=db_name + "_log")
        self.db_master.update_df(df=df_not_esg, db_name=db_name+"_not_esg_log")

        # Save the newly acquired tweets to db
        self.db_master.update_df(df=df_esg.drop(columns=['log']), db_name=db_name)
        self.db_master.update_df(df=df_not_esg.drop(columns=['log']), db_name=db_name+"_not_esg")

        # Refresh the found db in DB_Master
        self.db_master.find_db()

    def visualise(self, sdate:str = "2006-08-23 10:23:00", edate:str = "2023-08-23 10:23:00"):
        # Find corresponding df
        df = self.db_master.fit(sdate, edate)

        # Do the clustering
        topicer = ESG_Topic()
        df = topicer.fit_transform(df)

        # Drop irrelevant columns
        df = df.rename(columns={"Topic": "Cluster"})
        df = df.drop(columns=['Embedding', 'Prep_Tweet'])
        
        # remove duplicates
        df = df.drop_duplicates(subset=['Tweet'], keep="first")
        # Save the topicer work
        db_name = self.name
        self.db_master.save_df(df=df, db_name=db_name+"_"+str(sdate).replace(":", ".")+"_"+str(edate).replace(":", "."))