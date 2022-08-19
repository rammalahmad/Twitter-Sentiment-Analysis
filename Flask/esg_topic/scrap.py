'''
This file contains the script for scraping twitter
'''
import tweepy as tw
import pandas as pd
import numpy as np
import constants as c
from _embedder import Embedder

# Tweepy API
auth = tw.OAuthHandler(c.consumer_key, c.consumer_secret)
auth.set_access_token(c.access_token, c.access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

path_docs_db = ""
path_embed_db = ""

class Scraper_df:
    def __init__(self, name:str, lang:str = "en", size:int = 10000):
        self.name = name
        self.lang = lang
        self.size = size

    def fit(self):
        df = self.week_s()
        self.db = self.find_db()
        self.df = self.remove_inters(df)
        self.save_db()
        self.extracted_embed = self.extract_embeddings()
        self.save_embed()
        
    def week_s(self)-> pd.DataFrame:
        '''
        # Info
        ---
        This function creates a dataframe of tweets on the short term (less than a week)

        # Parameters
        ---
        text: the name we'll be using for our search
        size: the size of the dataframe 
        lang: the langage of the tweets

        # Results
        ---
        We get in return a dataframe of the users and their tweets
        '''
        tweets = tw.Cursor(api.search ,q= self.name, lang=self.lang, tweet_mode="extended").items(self.size)
        tweet =[]
        user = []
        date = []
        for i in tweets :
            date.append(i.created_at)
            tweet.append(i.full_text)
            user.append(i.user.screen_name)
        return pd.DataFrame({'Tweet': tweet, 'Date': date})

    def find_db(self):
        db_name = self.name + "_" + self.lang
        try:
            return pd.read_csv(path_docs_db + "/" + db_name)
        except:
            return None

    def remove_inters(self, df):
            if self.db:
                date_db = self.db.Date[0]
                return df[~df['Date'] > date_db]
            else:
                return df

    def save_db(self): 
            db_name = self.query + "_" + self.lang
            new_db = pd.concat([self.db, self.df])
            new_db.to_csv(path_docs_db + "/" + db_name +".csv")

    def extract_embeddings(self):
        embedder = Embedder(1)
        return self.embedder.embed(documents = self.df.Tweets, b_size=32)

    def save_embed(self):
        name = self.query + "_" + self.lang
        if self.db_name:
            np.save(path_embed_db +"/"+name, self.extracted_embed)
        else:
            embed_db = np.load(path_embed_db +"/"+name)
            new_embed_db = np.concatenate(embed_db, self.extracted_embed)
            np.save(path_embed_db +"/"+name, new_embed_db)