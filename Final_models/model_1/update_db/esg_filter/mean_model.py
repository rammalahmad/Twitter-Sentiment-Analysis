import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

path = r"C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Final_models\model_1\update_db\esg_filter\data" + "\\"


class Mean_model:
    def __init__(self, threshold: float):
      '''
      # Info 
      -----
      Initialize Mean_model

      # Parameters
      -----
      threshhold: float, the threshhold above which the 
      similarity is relevant (if the cosine similarity 
      of two arrays is less than the threshhold, then the
      two arrays are not similar)
      '''
      self.threshold = threshold
      self.ref = np.vstack([np.load(path+ "e_embeddings.npy"), 
                            np.load(path + "s_embeddings.npy"), 
                            np.load(path + "g_embeddings.npy")])

    def fit(self, embeddings: np.ndarray) -> List[int]:
        '''
        # Info 
        -----
        This Function calculates the similarity
        between the embeddings and each one of the
        three ESG categories, than outputs the most
        probable category

        # Parameters
        -----
        embeddings: numpy array, the extracted embeddings from the tweet
        # Returns
        ----
        It returns a List containing the class for each embedding
        '''
        y = cosine_similarity(embeddings, self.ref)
        l = [np.argmax(e) if np.max(e)>self.threshold else -1 for e in y]
        return l