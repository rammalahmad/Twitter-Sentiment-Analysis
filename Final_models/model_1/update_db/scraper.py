import update_db.scraping_constants as c
import tweepy as tw
import pandas as pd
import requests

# Tweepy API
auth = tw.OAuthHandler(c.consumer_key, c.consumer_secret)
auth.set_access_token(c.access_token, c.access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
headers = {
    "Authorization": f"Bearer {c.BEARER_Token}",
    "content-type":"application/json"
}

class Scraper:
    def __init__(self, name:str, lang:str = "en", size:int = 200, model:int = 0):
        '''
        # Info
        ---
        This is the tool used for scraping twitter

        # Params 
        ---
        name: string, the name of the company
        lang: string, the langugage used for the company
        size: int, size of the scrapped db, we're limited to 500 per request otherwise the scraper will 
        sleep for some minutes before resuming
        model: boolean, wether we do a full_archive search or just a weekly search.
        '''
        self.name = name
        self.lang = lang
        self.size = size
        self.model = model
    
    def fit(self):
        if self.model==1:
            df = self.full_as()
        else:
            df = self.week_s()
        return df

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
        df = pd.DataFrame({'Tweet': tweet, 'Date': date})
        df['Language'] = self.lang
        return df

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
        df = pd.DataFrame({'Tweet': tweet, 'Date': date})
        df['Language'] = self.lang
        return df

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