'''
# Info
---
In this script we just implement the TFIDF method manually, it will only be used
if you decide to insert the parameter keywords_model = 0 in the esg_topic class.
As for the code it applies the TFIDF calculation formula provided in the resources
'''

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.preprocessing import normalize
import numpy as np
import pandas as pd
import scipy.sparse as sp


class TFIDF_IDFi(TfidfTransformer):

    def __init__(self, X_per_cluster, X_origin, all_documents, *args, **kwargs):
        print('====== Using TFIDF_IDFi ======')
        super().__init__(*args, **kwargs)
        self.X_per_cluster = X_per_cluster
        self.X_origin = X_origin
        self.all_documents = all_documents
        
    
    def socre(self)->sp.csr_matrix:
        '''
        # Info
        ---
        The main funciton of the class
        It calculates the score of the words in each class
        # Params
        ---
        self

        # Returns
        ---
        a 2d matrix of the word score per topic
        '''
        self._global_tfidf = self.fit_transform(self.X_origin)
        
        global_df = pd.DataFrame(self._global_tfidf.toarray())
        global_df['Topic'] = self.all_documents.Topic
        
        avg_global_df = global_df.groupby(['Topic'], as_index=False).mean()
        avg_global_df = avg_global_df.drop('Topic', 1)
        self._avg_global_tfidf = avg_global_df.values
        
        local_tfidf_transformer = TfidfTransformer()
        local_tfidf_transformer.fit_transform(self.X_per_cluster)
        self._idfi = local_tfidf_transformer.idf_
        
        scores = self._avg_global_tfidf * self._idfi
        scores = normalize(scores, axis=1, norm='l1', copy=False)
        scores = sp.csr_matrix(scores)

        return scores 
