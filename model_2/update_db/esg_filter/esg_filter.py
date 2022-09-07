'''
Info
---
This is the main script for esg classification
In this script we have three possible models
    0: FinBert model
    1: Mean model
    2: GS (Gram-Schmidt) model
'''

import pandas as pd
import numpy as np
import ast
from typing import List

class ESG_Filter:
    def __init__(self, model:int, lang:str = "en"):
        '''
        # Info
        ---
        This is the main script for esg classification
        # Params
        ---
        model: int indicating which model to choose
            0: FinBert model
            1: Mean model
            2: GS (Gram-Schmidt) model
        lang: string indicating the language of the tweets
        '''
        self.model = model
        self.lang= lang
        print("Starting the filtering Task")
    
    def fit(self, documents:List[str], embeddings:np.ndarray)->List[int]:
        '''
        # Info
        ---
        Finds esg class for documents or embeddings
        If you're using model 0 you only need the documents
        If you're using model 1 or 2 you only need the embeddings
        # Params
        ---
        documents: List of tweets
        embeddings: Their embeddings
        # Returns
        ---
        It returns a List containing the class for each embedding or each tweet
        '''
        if self.model == 0:
            from model_2.update_db.esg_filter.finbert_model import Finbert_model
            print("Using FinBERT")
            model = Finbert_model(self.lang)
            return model.fit(documents)

        elif self.model == 1:
            from model_2.update_db.esg_filter.mean_model import Mean_model
            print("Using Mean Model")
            model = Mean_model(threshold = 0.15)
            return model.fit(embeddings)

        elif self.model == 2:
            from model_2.update_db.esg_filter.gs_model import GS_model
            print("Using GS Model")
            model = GS_model(threshold = 0.5)
            return model.fit(embeddings)