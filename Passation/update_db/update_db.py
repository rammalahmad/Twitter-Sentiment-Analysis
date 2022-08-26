'''
# Info
---
This is the main script for updating the database of certain company.
We recieve the name of the company, the language and the last update date.
The script will do the following steps:
    *Scrap tweets
    *Preprocess text
    *Filter the non-esg tweets by classifying the tweets into E, S, G or None
    *Find the sentiment per tweet
    *Extract the embeddings
    *Save everything in a dataframe
'''

import sys
sys.path.append(r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Passation")
sys.path.append(r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Passation\update_db")

from typing import List
import tweepy as tw
import pandas as pd
import numpy as np
import re
import requests

import scraping_constants as c
# Tweepy API
auth = tw.OAuthHandler(c.consumer_key, c.consumer_secret)
auth.set_access_token(c.access_token, c.access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
headers = {
    "Authorization": f"Bearer {c.BEARER_Token}",
    "content-type":"application/json"
}

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
        if self.f_a==False:
            df = self.remove_inters(df)

        #Preprocessed text:
        df["Prep_Tweet"] = self._preprocess_text(df.Tweet.to_list())

        #Extract embeddings
        extracted_embed = self.extract_embeddings(df)
        df["Embedding"] = extracted_embed.tolist()

        #Classify in ESG or not
        df = self.filter_esg(df, extracted_embed)

        #Save and remove non-esg tweets
        df_1 = df[df['ESG_class'] == -1]
        df_1 = df_1.reset_index(drop=True)

        df = df[df['ESG_class'] != -1]
        df = df.reset_index(drop=True)

        #Sentiment score
        df = self.find_sentiment(df)
    
        #Add the newly created dataframe to the old database
        self.save_db(df, df_1)
        
    def week_s(self)-> pd.DataFrame:
        '''
        # Info
        ---
        This function creates a dataframe of tweets on the short term (less than a week)

        # Parameters 
        ---
        The following params are hidden in self
        text: the name we'll be using for our search
        size: the size of the dataframe 
        lang: the langage of the tweets

        # Results
        ---
        We get in return a dataframe of the tweets and the dates
        '''
        print("Scraping new tweets")
        tweets = tw.Cursor(api.search ,q=self.name, lang=self.lang, tweet_mode="extended").items(self.size)
        tweet =[]
        date = []
        for i in tweets :
            date.append(i.created_at)
            tweet.append(i.full_text)
        return pd.DataFrame({'Tweet': tweet, 'Date': date})

    def full_as(self, maxResults: int = 100, fromDate:str = "200701010000", toDate:str = "202206260000") ->pd.DataFrame:
        '''
        # Info
        ---
        This function creates a dataframe of tweets on the long term (full archive)

        # Parameters
        ---
        maxResults: the size of the dataframe maximum 100 for now
        fromDate: the start date in the archive
        toDate: the end date in the archive

        # Results
        ---
        We get in return a dataframe of the tweets and the date
        '''
        # The query we'll be using for our search
        query = self.name +" lang:" + self.lang
        params = self.query_p(query, maxResults, fromDate, toDate)
        response = requests.request("GET", url = c.search_url, headers=headers, params = params)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        json_response = response.json()
        tweet = []
        date = []
        for i in range(len(json_response["results"])):
            date  += [json_response["results"][i]['created_at']]
            try:
                tweet += [json_response["results"][i]["extended_tweet"]["full_text"]]
            except Exception:
                tweet += [json_response["results"][i]["text"]]
        return pd.DataFrame({'Tweet': tweet, 'Date': date})

    def save_db(self, df, df_1): 
        db_name = self.name + "_" + self.lang
        df.to_csv(db_name+".csv")
        df_1.to_csv(db_name+"_"+"not_esg"+".csv")
        print("Saved the DB")

    def remove_inters(self, df:pd.DataFrame)->pd.DataFrame:
        '''
        # Info
        ---
        Removes overlapping from df by eliminating all the tweets that have a date
        before self.last_date

        # Parameters
        ---
        df: pandas dataframe containing the scrapped tweets

        # Results
        ---
        Non-overlapping df of tweets
        '''
        return df[df["Date"] > self.last_date]

    def filter_esg(self, df:pd.DataFrame, embeddings:np.ndarray=None)-> pd.DataFrame:
        '''
        # Info
        ---
        Classifies each tweet in df as
         0:Environment
         1:Social
         2:Governance
        -1:None

        # Parameters
        ---
        df: pandas dataframe containing the tweets

        # Results
        ---
        df with a column containing the esg_class
        '''
        from esg_filter.esg_filter import ESG_Filter
        filter = ESG_Filter(model=2, lang=self.lang)
        df['ESG_class'] = filter.fit(documents=df.Prep_Tweet.to_list(), embeddings=embeddings)
        # from esg_filter.finbert_model import Finbert_model
        # filter = Finbert_model(self.lang)
        # df['ESG_class'] = filter.fit(df.Prep_Tweet.to_list())
        return df

    @staticmethod
    def extract_embeddings(df:pd.DataFrame)->pd.DataFrame:
        '''
        # Info
        ---
        Extracts an embedding for each tweet in df

        # Parameters
        ---
        df: pandas dataframe containing the tweets

        # Results
        ---
        df with a column containing the embedding array
        '''
        from embedder.embedder import Embedder
        print("Extracting Embeddings")
        embedder = Embedder(1)
        return embedder.embed(documents=df.Prep_Tweet.to_list(), b_size=32)

    @staticmethod
    def find_sentiment(df:pd.DataFrame)-> pd.DataFrame:
        '''
        # Info
        ---
        Attributes a sentiment score between -1 and 1 for each tweet in df

        # Parameters
        ---
        df: pandas dataframe containing the tweets

        # Results
        ---
        df with a column containing the sentiment score
        '''
        from sentiment_analysis import Sent_model
        print("Analysing sentiment")
        sent = Sent_model(0)
        df['Sentiment'] = sent.doc_score(df.Prep_Tweet.to_list())
        return df

    @staticmethod
    def _preprocess_text(documents:List[str])->List[str]:
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