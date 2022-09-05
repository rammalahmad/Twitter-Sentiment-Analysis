import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class Label:
    def __init__(self, embeddings:np.ndarray, topic_embedding:np.ndarray):
        self.embeddings = embeddings
        self.top_embed = topic_embedding

    def fit(self) -> List[int]:
        self.cos_sim = [cosine_similarity(a.reshape(1,-1), self.top_embed.reshape(1,-1)) for a in self.embeddings]

    def label(self, threshold:float):
        return [1 if e>threshold else 0 for e in self.cos_sim]