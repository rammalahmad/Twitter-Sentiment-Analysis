from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List
import numpy as np

class GS_Base:
    def __init__(self, topic_dict:List[str], topic_name:str):
        self.topic_dict = topic_dict
        self.topic_name = topic_name
    
    def fit(self):
        # Transform words to vectors
        embedded_dict = self.embed(self.topic_dict)
        # Orthogonalise the base
        orth_base = self.gs(embedded_dict)
        # Save the outcome
        np.save(self.topic_name+"_orth_base.npy", orth_base)

    @staticmethod
    def embed(documents:List[str])->np.ndarray:
        model = SentenceTransformer('all-mpnet-base-v2')
        return np.array(model.encode(documents, batch_size=32, show_progress_bar=True))

    @staticmethod
    def gs(X: np.ndarray) -> np.ndarray:
        Y = []
        for e in X:
            proj_e = np.zeros(len(e))
            for inY in Y :
                proj_e = np.add(proj_e, np.multiply((inY@e) ,inY ))
            e = np.subtract(e,proj_e)
            e = np.multiply(e, 1/(np.linalg.norm(e)))
            Y.append(e)
        return np.vstack(Y)