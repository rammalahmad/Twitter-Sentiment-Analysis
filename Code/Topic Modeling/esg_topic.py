"""
Implemented based on BERTopic https://github.com/MaartenGr/BERTopic
"""

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import re
import numpy as np
import pandas as pd
from tqdm import tqdm

from typing import List, Tuple

import hdbscan
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from constants import en_dic, fr_dic
# import torch
from tfidf_idfi import TFIDF_IDFi

from _utils import Embedder


class ESG_Topic:

    def __init__(self, embeddings: np.ndarray = None, lang: str = "en", top_n_words: int = 10, min_topic_size: int = 10, nr_topics: int = 10, model_number: int = 0, dim_size: int = 50):

        if lang == "fr":
            self.dic = fr_dic
        else:
            self.dic = en_dic

        self.topics = None
        self.topic_sizes = None
        self.top_n_words = top_n_words
        self.nr_topics = nr_topics
        self.embedder = Embedder(model_number)
        self.embeddings = embeddings
        self.min_topic_size = min_topic_size
        self.vectorizer_model = CountVectorizer()
    
        self.dim_size = dim_size
        self.umap = UMAP(n_neighbors=15, n_components=self.dim_size, min_dist=0.0, metric='cosine')

        # cluster
        self.hdbscan_model = hdbscan.HDBSCAN(min_cluster_size= self.min_topic_size,
                                                              metric='euclidean',
                                                              cluster_selection_method='eom',
                                                              prediction_data=True)

        
    def fit_transform(self, documents):
        
        documents = self._preprocess_text(documents)
        if self.embeddings is None:
            self.embeddings = self._extract_embeddings(documents)
        my_df = pd.DataFrame({"Document": documents,
                                  "ID": range(len(documents)),
                                  "ESG_label": None,
                                  "Topic": None})
        embeddings = self.embeddings
        my_df["ESG_label"], embeddings = self._semi_supervised_modeling(embeddings)

        embeddings = self._reduce_dimensionality(embeddings)
        documents = self._cluster_embeddings(embeddings, my_df)
        self._extract_topics(my_df)

        return my_df


    def _semi_supervised_modeling(self, embeddings: np.ndarray) -> Tuple[List[int], np.array]:
        """
        # Info
        ---
        Apply Guided Topic Modeling

        We transform the seeded topics to embeddings using the
        same embedder as used for generating document embeddings.

        Then, we apply cosine similarity between the embeddings
        and set labels for documents that are more similar to
        one of the topics, then the average document.

        If a document is more similar to the average document
        than any of the topics, it gets the -1 label and is
        thereby not included in UMAP.

        # Arguments
        ---
            embeddings: The document embeddings

        # Returns
        ---
            y: The labels for each seeded topic
            embeddings: Updated embeddings
        """

        # Create embeddings from the seeded topics
        seed_labels_list = [self._extract_embeddings(keywords).mean(axis=0) for keywords in self.dic]

        seed_labels_list = np.vstack([seed_labels_list, embeddings.mean(axis=0)])

        # Label documents that are most similar to one of the seeded topics
        sim_matrix = cosine_similarity(embeddings, seed_labels_list)
        y = [np.argmax(sim_matrix[index]) for index in range(sim_matrix.shape[0])]
        y = [val if val != (len(seed_labels_list)-1) else -1 for val in y]

        # Average the document embeddings related to the seeded topics with the
        # embedding of the seeded topic to force the documents in a cluster
        for seed_topic in range(len(seed_labels_list)):
            indices = [index for index, topic in enumerate(y) if topic == seed_topic]
            embeddings[indices] = np.average([embeddings[indices], seed_labels_list[seed_topic]], weights=[3, 1])
        return y, embeddings    


    def _extract_embeddings(self, documents):
        
        embeddings = self.embedder.embed(documents)

        return embeddings
    

    def _reduce_dimensionality(self, embeddings):

        self.umap.fit(embeddings)
        reduced_embeddings = self.umap.transform(embeddings)
        
        return np.nan_to_num(reduced_embeddings)

    def _cluster_embeddings(self, embeddings, documents):
        self.hdbscan_model.fit(embeddings)
        documents['Topic'] = self.hdbscan_model.labels_
        self._update_topic_size(documents)

        return documents


    def _extract_topics(self, documents):
        
        documents_per_topic = documents.groupby(['Topic'], as_index=False).agg({'Document': ' '.join})
        self.scores, words = self._weighting_words(documents_per_topic, documents)
        self.topics = self._extract_words_per_topic(words)



    def _weighting_words(self, documents_per_topic, all_documents):
        
        concatenated_documents = self._preprocess_text(documents_per_topic.Document.values)
        origin_documents = self._preprocess_text(all_documents.Document.values)
        
        # count the words in a cluster
        self.vectorizer_model.fit(concatenated_documents)
        words = self.vectorizer_model.get_feature_names()
        
        # k * vocab
        X_per_cluster = self.vectorizer_model.transform(concatenated_documents)
        # D * vocab
        X_origin = self.vectorizer_model.transform(origin_documents)
        
        socres = TFIDF_IDFi(X_per_cluster, X_origin, all_documents).socre()

        return socres, words
    

    def _extract_words_per_topic(self, words):
    
        labels = sorted(list(self.topic_sizes.keys()))

        indices = self._top_n_idx_sparse(self.scores, 30)
        scores = self._top_n_values_sparse(self.scores, indices)
        sorted_indices = np.argsort(scores, 1)
        indices = np.take_along_axis(indices, sorted_indices, axis=1)
        scores = np.take_along_axis(scores, sorted_indices, axis=1)

        topics = {label: [(words[word_index], score)
                          if word_index and score > 0
                          else ("", 0.00001)
                          for word_index, score in zip(indices[index][::-1], scores[index][::-1])
                          ]
                  for index, label in enumerate(labels)}

        topics = {label: values[:self.top_n_words] for label, values in topics.items()}

        return topics


    def get_topics(self):
        return self.topics
    

    def get_topic(self, topic_id):
        if topic_id in self.topics:
            return self.topics[topic_id]
        else:
            return False

    def _update_topic_size(self, documents):

        sizes = documents.groupby(['Topic']).count().sort_values("Document", ascending=False).reset_index()
        self.topic_sizes = dict(zip(sizes.Topic, sizes.Document))
        


    def _preprocess_text(self, documents):
        """ Basic preprocessing of text

        Steps:
            * Remove # sign
            * Remove urls
        """
        cleaned_documents = [doc.replace("#", "") for doc in documents]
        cleaned_documents = [re.sub(r'^https?:\/\/.*[\r\n]*', '', doc, flags=re.MULTILINE) for doc in cleaned_documents]

        return cleaned_documents
    

    @staticmethod
    def _top_n_idx_sparse(matrix, n):
        """ Return indices of top n values in each row of a sparse matrix

        Retrieved from:
            https://stackoverflow.com/questions/49207275/finding-the-top-n-values-in-a-row-of-a-scipy-sparse-matrix

        Args:
            matrix: The sparse matrix from which to get the top n indices per row
            n: The number of highest values to extract from each row

        Returns:
            indices: The top n indices per row
        """
        indices = []
        for le, ri in zip(matrix.indptr[:-1], matrix.indptr[1:]):
            n_row_pick = min(n, ri - le)
            values = matrix.indices[le + np.argpartition(matrix.data[le:ri], -n_row_pick)[-n_row_pick:]]
            values = [values[index] if len(values) >= index + 1 else None for index in range(n)]
            indices.append(values)
        return np.array(indices)
    

    @staticmethod
    def _top_n_values_sparse(matrix, indices):
        """ Return the top n values for each row in a sparse matrix

        Args:
            matrix: The sparse matrix from which to get the top n indices per row
            indices: The top n indices per row

        Returns:
            top_values: The top n scores per row
        """
        top_values = []
        for row, values in enumerate(indices):
            scores = np.array([matrix[row, value] if value is not None else 0 for value in values])
            top_values.append(scores)
        return np.array(top_values)

