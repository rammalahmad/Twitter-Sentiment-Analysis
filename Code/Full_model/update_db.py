import tweepy as tw
import pandas as pd
import numpy as np
import re
import constants as c

# Tweepy API
auth = tw.OAuthHandler(c.consumer_key, c.consumer_secret)
auth.set_access_token(c.access_token, c.access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

path_docs_db = ""
path_embed_db = ""

class Update_DB:
    def __init__(self, name:str, lang:str = "en", size:int = 10000):
        self.name = name
        self.lang = lang
        self.size = size

    def fit(self):
        #Scrap one week db:
        df = self.week_s()

        #Add it to old db without overlapping
        self.db = self.find_db()
        df = self.remove_inters(df)
        
        #Preprocessed text:
        self.prep_df = self._preprocess_text(df.Tweet.to_list())

        #Extract embeddings
        self.extracted_embed = self.extract_embeddings()
        self.save_embed()

        #Classify in ESG or not
        df = self.filter_esg(df)

        #Sentiment score
        df = self.find_sentiment(df)

        #Add the newly created dataframe to the old database
        self.save_db(df)
        
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

    def extract_embeddings(self):
        from _embedder import Embedder
        embedder = Embedder(1)
        return embedder.embed(documents=self.prep_df, b_size=32)

    def save_embed(self):
        name = self.name + "_" + self.lang
        if self.db:
            embed_db = np.load(path_embed_db +"/"+name)
            new_embed_db = np.concatenate(embed_db, self.extracted_embed)
            np.save(path_embed_db +"/"+name, new_embed_db)
        else:
            np.save(path_embed_db +"/"+name, self.extracted_embed)

    def filter_esg(self, df):
        from _esg_filter import Finbert_model
        filter = Finbert_model()
        df['ESG_class'] = filter.fit(self.prep_df)
        return df

    def find_sentiment(self, df):
        from sentiment_analysis import Sent_model
        sent = Sent_model(1)
        df['Sentiment'] = sent.doc_score(self.prep_df)
        return df

    def save_db(self, df): 
        db_name = self.name + "_" + self.lang
        if self.db:
            new_db = pd.concat([self.db, df], ignore_index=True)
            new_db.to_csv(path_docs_db + "/" + db_name +".csv")
        else:
            df.to_csv(path_docs_db + "/" + db_name +".csv")

    @staticmethod
    def _preprocess_text(documents):
        """ Basic preprocessing of text
        Steps:
            * Remove # sign 
            * Remove urls
        """
        cleaned_documents = [doc.replace("#", "") for doc in documents]
        cleaned_documents = [re.sub(r"http\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [re.sub(r"https\S+", "", doc) for doc in cleaned_documents]

        return cleaned_documents