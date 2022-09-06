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

from typing import List
import pandas as pd
import numpy as np
import re


class Update_DB:
    def __init__(self, name:str, lang:str = "en", last_date:str = "2007-08-23 10:23:00", 
                size:int = 200,
                full_archive:bool = False,
                embed_model:int = 1,
                filter_model:int = 2,
                sent_model:int = 1):
        '''
        # Info
        ---
        Initialize the scraper

        # Params 
        ---
        name: string, the name of the company
        lang: string, the langugage used for the company
        last_date: string, last date in the stored database
        size: int, size of the scrapped dataframe
        full_archive: boolean, wether we do a full_archive search or just a weekly search.
        embed_model: int, the embedding model 0=ESG_BERT 1=SBERT 2=xlm-RoBERTa-base
        filter_model: int, the esg_filter model 0=FinBERT 1=Mean_model 2=GS_model
        sent_model: int, the sentiment model 0=RoBERTa_Twitter 1=BERT_base_uncased
        '''

        print("Updating the db for", name, "in", lang)
        self.name = name
        self.lang = lang
        self.last_date = last_date
        self.size = size
        self.f_a = full_archive
        self.embed_model = embed_model
        self.filter_model = filter_model
        self.sent_model = sent_model

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
    
        # Get the Database
        df = self.scrap_df()
        
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
        return df, df_1

    def scrap_df(self):
        from update_db.scraper import Scraper
        scraper = Scraper(name=self.name, lang=self.lang, size = self.size, model=int(self.f_a))
        df = scraper.fit()
        return df

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
        from update_db.esg_filter.esg_filter import ESG_Filter
        filter = ESG_Filter(model=self.filter_model, lang=self.lang)
        df['ESG_class'] = filter.fit(documents=df.Prep_Tweet.to_list(), embeddings=embeddings)
        # from esg_filter.finbert_model import Finbert_model
        # filter = Finbert_model(self.lang)
        # df['ESG_class'] = filter.fit(df.Prep_Tweet.to_list())
        return df

    def extract_embeddings(self, df:pd.DataFrame)->pd.DataFrame:
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
        embedder = Embedder(self.embed_model)
        return embedder.embed(documents=df.Prep_Tweet.to_list(), b_size=32)

    def find_sentiment(self, df:pd.DataFrame)-> pd.DataFrame:
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
        from update_db.sentiment_analysis import Sent_model
        print("Analysing sentiment")
        sent = Sent_model(self.sent_model)
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
        cleaned_documents = [re.sub("RT", "", doc) for doc in cleaned_documents]

        return cleaned_documents