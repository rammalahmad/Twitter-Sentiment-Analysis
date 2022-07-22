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

class scraper:
    def __init__(self):
        self.api = api
        self.auth = auth
        self.search_url = c.search_url
        self.headers = headers

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
        return pd.DataFrame({'user': user, 'tweet': tweet})

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
        params = query_p(query, maxResults, fromDate, toDate)
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