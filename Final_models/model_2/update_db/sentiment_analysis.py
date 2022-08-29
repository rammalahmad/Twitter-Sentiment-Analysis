'''
# Info
---
This is the script for sentiment analysis
In this script we consider two multilingual models:
    *twitter-xlm-roberta-base
    *bert-base-multilingual
'''
from typing import List
from transformers import pipeline

class Sent_model:
    def __init__(self, model:int = 0):
        '''
        # Info
        ---
        Initialize Sentiment Analysis

        # Params 
        ---
        model: integer could be 0: Roberta or 1: Bert-base
        '''
        self.model = model

        if model == 0:
            model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
            top_k = 3
        elif model == 1:
            model_path = "nlptown/bert-base-multilingual-uncased-sentiment"
            top_k = 5

        self.sentiment = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path, top_k=top_k)

    def doc_score(self, documents:List[str])->List[float]:
        '''
        # Info
        ---
        Calculates the score of each text in the documents list

        # Params 
        ---
        documents: list of the texts we want to analyse

        # Returns
        ---
        list of floats representing the sentiment score for each text in documents
        '''
        sent_doc = self.sentiment(documents)
        return [self.txt_score(sent_txt) for sent_txt in sent_doc]

    def txt_score(self, sent_txt)->float:
        '''
        # Info
        ---
        Calculates the average sentiment score for a text based on the outcome of the model

        # Params 
        ---
        sent_txt: the outcome of the model applied on a text

        # Returns
        ---
        float representing the average sentiment score for the text
        '''
        txt_score = 0
        if self.model == 0:
            for e in sent_txt:
                if e['label'] == 'Neutral':
                    txt_score += 0
                if e['label'] == 'Positive':
                    txt_score += e['score']
                if e['label'] == 'Negative':
                    txt_score += -e['score']
        elif self.model == 1:
            for e in sent_txt:
                nb_stars = int(e['label'][0])
                txt_score += ((nb_stars - 3)/2)*(e['score'])
        return txt_score

    def fit(self,documents:List[str])->float:
        '''
        # Info
        ---
        Calculates the average sentiment score for all documents
        # Params 
        ---
        documents: list of the texts we want to analyse

        # Returns
        ---
        float representing the average sentiment score for the documents
        '''
        doc_score = self.doc_score(documents)
        return sum(doc_score)/len(doc_score)
