import sys
from xmlrpc.client import boolean
from typing import List
sys.path.append(r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model")
sys.path.append(r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model\update_db")

import tweepy as tw
import pandas as pd
import numpy as np
import re
import constants as c
import requests

# Tweepy API
auth = tw.OAuthHandler(c.consumer_key, c.consumer_secret)
auth.set_access_token(c.access_token, c.access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
headers = {
    "Authorization": f"Bearer {c.BEARER_Token}",
    "content-type":"application/json"
}


path_embed_db = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model\db\embeddings"
path_docs_db = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Code\Full_model\db\tweets"

class Update_DB:
    def __init__(self, name:str, lang:str = "en", last_date:str = "2007-08-23 10:23:00", size:int = 100, full_archive:bool = False):
        '''
        # Info
        ---
        Initialize the scraper

        # Params 
        ---
        name: string, the name of the company
        lang: string, the langugage used for the company
        last_date: string, last date in the stored database
        size: int, size of the scrapped db, we're limited to 500 per request otherwise the scraper will 
        sleep for some minutes before resuming
        full_archive: boolean, wether we do a full_archive search or just a weekly search.
        '''

        print("Launching the updater")
        self.name = name
        self.lang = lang
        self.last_date = last_date
        self.size = size
        self.f_a = full_archive

    def fit(self) -> pd.DataFrame:
        '''
        # Info
        ---
        It scraps the data, does the preprocessing, filters non-esg tweets, calculates the sentiment and 
        extracts the embeddings then it saves the outcome in a dataframe

        # Params 
        ---
        self attributes

        # Returns
        ---
        Dataframe with preprocessed tweets, esg_category, sentiment and embedding
        '''

        #Scrap one week db:
        if self.f_a:
            df = self.full_as()
        else:
            df = self.week_s()

        #Remove overlapping
        self.db = self.find_db()
        df = self.remove_inters(df)

        #Preprocessed text:
        df["Prep_Tweet"] = self._preprocess_text(df.Tweet.to_list())
        
        #Classify in ESG or not
        df = self.filter_esg(df)

        #Save and remove non-esg tweets

        self.save_non_esg(df)
        df = df[df['ESG_class'] != -1]
        df = df.reset_index(drop=True)

        #Sentiment score
        df = self.find_sentiment(df)

        #Extract embeddings
        extracted_embed = self.extract_embeddings(df)
    
        #Add the newly created dataframe to the old database
        df["Embedding"] = extracted_embed.tolist()
        self.save_db(df)
        # self.save_embed(extracted_embed)
        
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
        print("Scraping new tweets")
        tweets = tw.Cursor(api.search ,q=self.name, lang=self.lang, tweet_mode="extended").items(self.size)
        tweet =[]
        date = []
        for i in tweets :
            date.append(i.created_at)
            tweet.append(i.full_text)
        return pd.DataFrame({'Tweet': tweet, 'Date': date})

    
    def find_db(self):
        db_name = self.name + "_" + self.lang
        try:
            db = pd.read_csv(path_docs_db + "/" + db_name + ".csv")
            print("Found an existing DB")
            self.found_db = True
            return db
        except:
            print("No existing DB found")
            self.found_db = False
            return None

    def remove_inters(self, df):
        if self.found_db:
            return df[df["Date"] > self.last_date]
        else:
            return df

    def save_non_esg(self, df):
        db_name = self.name + "_" + self.lang + "_not_esg"
        try:
            db = pd.read_csv(path_docs_db + "/" + db_name + ".csv")
            new_db = pd.concat([db, df[df['ESG_class'] == -1]], ignore_index=True)
            new_db.to_csv(path_docs_db + "/" + db_name + ".csv")
        except:
            df[df['ESG_class'] == -1].reset_index(drop=True).to_csv(path_docs_db + "/" + db_name +".csv")

    def save_embed(self, extracted_embed):
        name = self.name + "_" + self.lang
        if self.found_db:
            embed_db = np.load(path_embed_db +"/"+name+".npy")
            new_embed_db = np.concatenate((extracted_embed, embed_db), axis=0)
            np.save(path_embed_db +"/"+name+".npy", new_embed_db)
        else:
            np.save(path_embed_db +"/"+name+".npy", extracted_embed)
        print("Saved the embeddings")

    def save_db(self, df): 
        db_name = self.name + "_" + self.lang
        if self.found_db:
            new_db = pd.concat([df, self.db], ignore_index=True)
            new_db.to_csv(path_docs_db + "/" + db_name +".csv")
        else:
            df.to_csv(path_docs_db + "/" + db_name +".csv")
        print("Saved the DB")

    def filter_esg(self, df)-> pd.DataFrame:
        from _esg_filter import Finbert_model
        print("Filtering ESG")
        filter = Finbert_model(self.lang)
        df['ESG_class'] = filter.fit(df.Prep_Tweet.to_list())
        return df

    def full_as(self, maxResults: int = 100, fromDate:str = "200701010000", toDate:str = "202206260000") ->pd.DataFrame:
        '''
        # Info
        ---
        This function creates a dataframe of tweets on the long term (full archive)

        # Parameters
        ---
        query: the query we'll be using for our search
        maxRsults: the size of the dataframe maximum 100 for now
        fromDate: the start date in the archive
        toDate: the end date in the archive

        # Results
        ---
        We get in return a dataframe of the tweets
        '''
        query = self.name +" lang:" + self.lang
        params = self.query_p(query, maxResults, fromDate, toDate)
        response = requests.request("GET", url = c.search_url, headers=headers, params = params)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        json_response = response.json()
        return json_response
        tweet = []
        date = []
        for i in range(len(json_response["results"])):
            try:
                tweet += [json_response["results"][i]["extended_tweet"]["full_text"]]
                date  += [json_response["results"][i]['created_at']]
            except Exception:
                tweet += [json_response["results"][i]["text"]]
        return pd.DataFrame({'Tweet': tweet, 'Date': date})

    @staticmethod
    def extract_embeddings(df):
        from esg_topic._embedder import Embedder
        print("Extracting Embeddings")
        embedder = Embedder(1)
        return embedder.embed(documents=df.Prep_Tweet.to_list(), b_size=32)

    @staticmethod
    def find_sentiment(df)-> pd.DataFrame:
        from sentiment_analysis import Sent_model
        print("Analysing sentiment")
        sent = Sent_model(1)
        df['Sentiment'] = sent.doc_score(df.Prep_Tweet.to_list())
        return df

    @staticmethod
    def _preprocess_text(documents:List)->List:
        """ Basic preprocessing of text
        Steps:
            * Remove # sign 
            * Remove urls
            * Remove @ tags
            * Remove RT (retweet)
        """
        cleaned_documents = [doc.replace("#", "") for doc in documents]
        cleaned_documents = [re.sub(r"http\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [re.sub(r"https\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [re.sub(r"@\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [doc.replace("RT", "") for doc in cleaned_documents]

        return cleaned_documents

    @staticmethod
    def query_p(text:str, maxResults: int = 100, fromDate:str = "200701010000", toDate:str = "202206260000") -> dict:
        '''
        # Info
        ---
        This function writes the query parameters in a proper
        way

        # Parameter
        ---
        A text that corresponds to our query keyword
        An interger corresponding to the maximal number of tweets 
        that we can capture
        Two strings corresponding to the starting date and the 
        ending date of our scraping

        # Results
        ---
        We get in result a dictionary that will be used as a parameter
        to do the research.
        '''
        return {"query": text ,"maxResults": maxResults ,"fromDate":fromDate,"toDate":toDate}