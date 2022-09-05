from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class Gen_Embed:
    def __init__(self, topic_name:str, data:List[str]):
        self.topic_name = topic_name
        self.data = data
    
    def fit(self):
        embeddings = self.embed(self.data)
        np.save(self.topic_name+'_data_embeddings.npy', embeddings)

    @staticmethod
    def embed(documents:List[str])->np.ndarray:
        model = SentenceTransformer('all-mpnet-base-v2')
        return np.array(model.encode(documents, batch_size=32, show_progress_bar=True))