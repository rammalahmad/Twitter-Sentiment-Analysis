import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

class Label:
    def __init__(self, embeddings:np.ndarray, base:np.ndarray):
        self.embeddings = embeddings
        self.base = base

    def fit(self) -> List[int]:
        self.cos_sim = [cosine_similarity(a.reshape(1,-1), self.proj(a)) for a in self.embeddings]

    def label(self, threshold:float):
        return [1 if e>threshold else 0 for e in self.cos_sim]

    def proj(self, a: np.array) -> np.ndarray:
        a_F = np.zeros(len(a))
        for e in self.base:
            a_F = np.add(a_F, np.multiply((e@a),e))
        return a_F.reshape(1, -1)