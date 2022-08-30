from update_db.update_db import Update_DB
from esg_topic.esg_topic import ESG_Topic
from db_master import DB_Master
import pandas as pd
import ast
 
class Surf_Mes_Tweets:
    def __init__(self, name:str, lang:str):
        self.name = name
        self.lang = lang
        self.db_master = DB_Master(name=name, lang=lang)

    def update(self):
        updater = Update_DB(name=self.name, lang=self.lang, last_date=self.db_master.find_last_date())
        df_esg, df_not_esg = updater.fit()
        
        # Put together the new database
        df_not_esg['log'] = 'C'
        df_esg['log'] = 'C'
        if self.db_master.found_db:
            old_db = self.db_master.db[['Tweet', 'Date', 'Embedding', 'ESG_class', 'Sentiment']]
            old_db['Embedding'] = old_db['Embedding'].apply(lambda x: ast.literal_eval(x))
            old_db['log'] = 'U'

            new_db = pd.concat([df_esg, old_db], ignore_index=True)
        else:
            new_db = df_esg

        # Cluster the outcome
        topicer = ESG_Topic()
        new_db = topicer.fit_transform(new_db)

        new_db = new_db.rename(columns={"Topic": "Cluster"})
        new_db = new_db.drop(columns=['Prep_Tweet'])

        db_name = self.name+"_"+self.lang

        # Save the logs
        self.db_master.update_df(df=df_not_esg, db_name=db_name+"_not_esg_log")
        self.db_master.update_df(df=new_db, db_name=db_name+"_log")

        # Save the newly acquired tweets
        self.db_master.update_df(df=df_not_esg.drop(columns=['log']), db_name=db_name+"_not_esg")
        self.db_master.save_df(df=new_db.drop(columns=['log']), db_name=db_name)

        # Refresh the found db in DB_Master
        self.db_master.find_db()

    def visualise(self, sdate:str = "2006-08-23 10:23:00", edate:str = "2023-08-23 10:24:00"):
        df = self.db_master.fit(sdate, edate)
        df = self.visu_elements(df)
        # Save the topicer work
        db_name = self.name+"_"+self.lang
        self.db_master.save_df(df=df, db_name=db_name+"_"+str(sdate).replace(":", ".")+"_"+str(edate).replace(":", "."))

    @staticmethod
    def visu_elements(df:pd.DataFrame):
        grouped = df.groupby('Cluster')
        topics_sentiment = {}
        topics_keywords = {}
        topics_hashtags = {}
        for topic, cluster in grouped:
            topics_sentiment[topic] = sum(cluster.Sentiment.to_list())/len(cluster.Sentiment.to_list())
            topics_keywords[topic] = list(set([j for sub in [ast.literal_eval(e) for e in cluster.Keywords.to_list()] for j in sub]))
            topics_hashtags[topic] = list(set([j for sub in [ast.literal_eval(e) for e in cluster.Hashtags.to_list()] for j in sub]))

        df['Topic_sentiment'] = df.apply(lambda row : topics_sentiment[row['Cluster']], axis=1)
        df['Topic_Keywords'] = df.apply(lambda row : topics_keywords[row['Cluster']], axis=1)
        df['Topic_Hashtags'] = df.apply(lambda row : topics_hashtags[row['Cluster']], axis=1)
        return df