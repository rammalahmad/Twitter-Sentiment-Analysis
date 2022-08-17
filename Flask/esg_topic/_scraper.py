'''
This file contains the script for scraping twitter
'''

import requests
import os
import json
import pandas as pd
import tweepy as tw
import constants as c

# Tweepy API
auth = tw.OAuthHandler(c.consumer_key, c.consumer_secret)
auth.set_access_token(c.access_token, c.access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

headers = {
    "Authorization": f"Bearer {c.BEARER_Token}",
    "content-type":"application/json"
}


class Scraper_df:
    def __init__(self, query:str, size:int, lang:str, sdate:str, edate: str):
        #Key elements of scraping
        self.query = query
        self.size = size
        self.lang = lang
        self.sdate = sdate
        self.edate = edate

        self.scrap_sdate = None
        self.scrap_edate = None

        #For authentication
        self.api = api
        self.auth = auth
        self.search_url = c.search_url
        self.headers = headers

        #The collected DataFrame
        self.existing_df = pd.DataFrame()
        self.scraped_df = pd.DataFrame()

    def fit(self):
        # Check if we already have a scrapped DataFrame
        self._check_existing_db() 


    def _check_existing_db(self):
        files_list = self._find_files_names(self)
        for file in files_list:
            file_sdate =  file[len(file) - 25: len(file) - 13]
            file_edate =  file[len(file) - 12:]
            if self.check_order(self.sdate, file_sdate):
                if self.check_order(self.edate, file_sdate):
                    print("No files in the database")
                    self.scrap_sdate = self.sdate
                    self.scrap_edate = self.edate
                else:
                    existing_df = pd.read_csv(file)
                    self.existing_df = 
            elif self.check_order(self.sdate, file_edate):
                if self.check_order(self.edate, file_edate):
                    print("This df exist already")
                    existing_df = pd.read_csv(file)
                    self.existing_df = self.df_interval(existing_df, self.sdate, self.edate)
                    self.scrap_sdate = None
                    self.scrap_edate = None
                else:
                    print("Part of this df exists already")
                    existing_df = pd.read_csv(file)
                    self.existing_df = self.df_interval(existing_df, self.sdate, file_edate)
                    self.scrap_sdate = file_edate
                    self.scrap_edate = self.edate
            else:
                print("No files in the database")
                self.scrap_sdate = self.sdate
                self.scrap_edate = self.edate
                    

    def _find_files_names(self):
        starting_name = self.query + "_" + self.lang
        files_list = []
        for file in os.listdir(r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Flask\esg_topic\Data"):
            if file.startswith(starting_name):
                files_list += [file]
        return files_list

    def _save_file(self):
        name = self.query + "_" + self.lang + "_" + self.sdate + "_" + self.edate
        self.df.to_csv(name+".csv")

    def week_s(self, text : str, size: int = 100 , lang: str = "en") -> pd.DataFrame:
        '''
        # Info
        ---
        This function creates a dataframe of tweets on the short term (less than a week)

        # Parameters
        ---
        text: the query we'll be using for our search
        size: the size of the dataframe 
        lang: the langage of the tweets

        # Results
        ---
        We get in return a dataframe of the users and their tweets
        '''
        tweets = tw.Cursor(self.api.search ,q= text, lang=lang , tweet_mode="extended").items(size)
        tweet =[]
        user = []
        for i in tweets :
            tweet.append(i.full_text)
            user.append(i.user.screen_name)
        return pd.DataFrame({'tweet': tweet})

    def full_as(self, query:str, maxResults: int = 100, fromDate:str = "200701010000", toDate:str = "202206260000") ->pd.DataFrame:
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
        params = self.query_p(query, maxResults, fromDate, toDate)
        response = requests.request("GET", url = self.search_url, headers=self.headers, params = params)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        json_response = response.json()
        tweet = []
        for i in range(len(json_response["results"])):
            try:
                tweet += [json_response["results"][i]["extended_tweet"]["full_text"]]
            except Exception:
                tweet += [json_response["results"][i]["text"]]
        return pd.DataFrame({'tweet': tweet})


    @staticmethod
    def query_p(text:str, maxResults: int = 100, fromDate:str = "200701010000", toDate:str = "202206260000") -> dict:
        '''
        # Info
        ---
        This function writes the query parameters in a proper
        way

        # Parameter
        ---
        text: corresponds to our query keyword
        maxResults: interger corresponding to the maximal number of tweets to scrap
        fromDate: starting date of scraping
        toDate: end date of scraping

        # Results
        ---
        We get in result a dictionary that will be used as a parameter
        to do the research.
        '''
        return {"query": text ,"maxResults": maxResults ,"fromDate":fromDate,"toDate":toDate}

    @staticmethod
    def date_order(date_1:str, date_2:str):
        year_1 = date_1[0:4]
        month_1 = date_1[5:7]
        day_1 = date_1[8:10]
        year_2 = date_2[0:4]
        month_2 = date_2[5:7]
        day_2 = date_2[8:10]
        if year_1!=year_2:
            if year_1 < year_2:
                return True
            else:
                return False
        elif month_1!=month_2:
            if month_1 < month_2:
                return True
            else:
                return False
        elif day_1!=day_2:
            if day_1 < day_2:
                return True
            else:
                return False
        return True

    @staticmethod
    def df_interval(df, sdate, edate):

