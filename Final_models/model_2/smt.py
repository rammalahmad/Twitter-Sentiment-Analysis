from update_db.update_db import Update_DB
from esg_topic.esg_topic import ESG_Topic
from db_master import DB_Master

class Surf_Mes_Tweets:
    def __init__(self, name:str, lang:str):
        self.name = name
        self.lang = lang
        self.db_master = DB_Master(name=name, lang=lang)

    def update(self):
        updater = Update_DB(name=self.name, lang=self.lang, last_date=self.db_master.find_last_date())
        df_esg, df_not_esg = updater.fit()

        # Save the newly acquired tweets
        db_name = self.name+"_"+self.lang
        self.db_master.save_df(df=df_esg, db_name=db_name)
        self.db_master.save_df(df=df_not_esg, db_name=db_name+"_not_esg")

        # Save the logs
        self.db_master.save_log(df=df_esg, df_name=db_name)
        self.db_master.save_log(df=df_not_esg, df_name=db_name+"_not_esg")

        # Refresh the found db in DB_Master
        self.db_master.find_db()

    def visualise(self, sdate:str = "2006-08-23 10:23:00", edate:str = "2023-08-23 10:23:00"):
        df = self.db_master.fit(sdate, edate)
        topicer = ESG_Topic()
        topicer.fit_transform(df)

        # Save the topicer work
        db_name = self.name+"_"+self.lang
        self.db_master.save_df(df=df, db_name=db_name+"_"+str(sdate).replace(":", ".")+"_"+str(edate).replace(":", "."))