import sys
sys.path.append(r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model")

import datetime
from db_master import DB_Master

class Surf_Mes_Tweets:
    def __init__(self, name:str, lang:str = "en"):
        self.name = name
        self.lang = lang
        self.db_master = DB_Master(name=self.name, lang=self.lang)

    #Scrap new tweets and add them to the database
    def update(self):
        from update_db.update_db import Update_DB
        updater = Update_DB(name=self.name, lang=self.lang, full_archive = False)
        updater.fit()
        # Re-Initialize the DB_Master
        self.db_master = DB_Master(name=self.name, lang=self.lang)

    def show_db_date(self):
        if self.db_master.found_db:
            self.db_master.date_interval()
        else:
            print("DB is empty")

    #Find the data that interests the client
    def find_db(self, sdate = "2007-08-23 10:23:00", edate = str(datetime.datetime.now())):
        self.db_master.fit(sdate, edate)

    #Apply the clustering and extract keywords per topic
    def find_topics(self):
        from esg_topic.esg_topic import ESG_Topic
        topicer = ESG_Topic()
        topicer.fit_transform(df=self.db_master.df, embeddings=self.db_master.embed)
        self.db_master.save_log(topicer)
