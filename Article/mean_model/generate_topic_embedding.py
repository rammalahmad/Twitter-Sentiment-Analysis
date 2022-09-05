from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class Gen_Top:
    def __init__(self, topic_dict:List[str], topic_name:str):
        self.topic_dict = topic_dict
        self.topic_name = topic_name
    
    def fit(self):
        # Transform words to vectors
        embedded_dict = self.embed(self.topic_dict)
        # Find the mean of all vectors
        mean = np.mean(embedded_dict, axis=0)
        # Save the outcome
        np.save(self.topic_name+"_embedding.npy", mean)

    @staticmethod
    def embed(documents:List[str])->np.ndarray:
        model = SentenceTransformer('all-mpnet-base-v2')
        return np.array(model.encode(documents, batch_size=32, show_progress_bar=True))