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
from sklearn.cluster import KMeans
from tfidf_idfi import TFIDF_IDFi
from _utils import Embedder
from tomaster import tomato
from yellowbrick.cluster.elbow import kelbow_visualizer

import sys

path = r'C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Flask\esg_topic\Data'


class ESG_Topic:

    def __init__(self, embeddings: np.ndarray = None,
                model_number: int = 0,
                semi_sup: int = 0,
                lang: str = "en",  
                top_n_words: int = 10, 
                cluster_model: int = 0,
                min_topic_size: int = 20,
                dim: int = 50,
                do_mmr: bool = False):

        if semi_sup == 1:
            if lang == "fr":
                self.dic = fr_dic
            else:
                self.dic = en_dic

        self.semi_sup = semi_sup
        self.model_number = model_number
        self.embeddings = embeddings
        self.min_topic_size = min_topic_size
        self.cluster_model = cluster_model
        self.do_mmr = do_mmr
    
        self.umap = UMAP(n_neighbors=15, n_components = dim, min_dist=0.0, metric='cosine')

        if self.cluster_model == 0:
            self.hdbscan_model = hdbscan.HDBSCAN(min_cluster_size= self.min_topic_size,
                                                              metric='euclidean',
                                                              cluster_selection_method='eom',
                                                              prediction_data=True)
        elif self.cluster_model == 1:
            self.kmeans = KMeans(random_state=42)
        
        self.embedder = Embedder(self.model_number)
        self.df = None                      
        self.top_n_words = top_n_words
        self.vectorizer_model = CountVectorizer()
        self.topics = None
        self.topic_sizes = None

        print("Model loaded successfully")
        
    def fit_transform(self, documents, documents_name:str):
        
        documents = self._preprocess_text(documents)
        if self.embeddings is None:
            try:
                name = str(self.model_number) + documents_name + ".npy"
                self.embeddings = np.load(path+"/"+name)
                print("The embeddings are already extracted")
            except Exception:
                self.embeddings = self._extract_embeddings(documents, documents_name)

        my_df = pd.DataFrame({"Document": documents,
                                  "ID": range(len(documents)),
                                  "Topic": None})
        embeddings = self.embeddings

        if self.semi_sup == 1:
            my_df["ESG_label"], embeddings = self._semi_supervised_modeling(embeddings)

        embeddings = self._reduce_dimensionality(embeddings)

        documents = self._cluster_embeddings(embeddings, my_df)
        self._extract_topics(my_df)
        self.df = my_df
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
        print("Modified embeddings with Gram-Schmidt successfully")
        return y, embeddings    


    def _extract_embeddings(self, documents, documents_name="", method="documents"):
        if method == "documents":
            embeddings = self.embedder.embed(documents)
            name = str(self.model_number) + documents_name
            np.save(path+"/"+name, embeddings)
            print("Extracted the embeddings successfully")
            return embeddings
        elif method == "MMR":
            embeddings = self.embedder.embed(documents)
            return embeddings
        
    

    def _reduce_dimensionality(self, embeddings):

        self.umap.fit(embeddings)
        reduced_embeddings = self.umap.transform(embeddings)
        print("Reduced dimension successfully")
        
        return np.nan_to_num(reduced_embeddings)

    def _cluster_embeddings(self, embeddings, documents):

        if self.cluster_model == 0:
            print("Clustering with DBScan")
            self.hdbscan_model.fit(embeddings)
            documents['Topic'] = self.hdbscan_model.labels_
            self._update_topic_size(documents)

        elif self.cluster_model == 1:
            print("Clustering with KMeans")

            l = []
            elbow = kelbow_visualizer(self.kmeans, embeddings, metric='silhouette', k=(2,15))
            l.append(elbow.elbow_value_)
            elbow = kelbow_visualizer(self.kmeans, embeddings, metric='calinski_harabasz', k=(2,15))
            l.append(elbow.elbow_value_)
            elbow = kelbow_visualizer(self.kmeans, embeddings, metric='distortion', k=(2,15))
            l.append(elbow.elbow_value_)

            self.nr_topics = max(l)
            print("Number of clusters = ", self.nr_topics)
            self.kmeans = KMeans(self.nr_topics, random_state=42)
            self.kmeans.fit(embeddings)
            documents['Topic'] = self.kmeans.labels_
            self._update_topic_size(documents)
            documents['dist_centroid'] = self.kmeans.inertia_

        elif self.cluster_model == 2:
            print("Clustering with ToMATo")
            clusters = tomato(points=embeddings, k=15)
            documents['Topic'] = list(clusters)
            self._update_topic_size(documents)


        print("Clustered embeddings successfully")

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
        
        if self.do_mmr == True :
            from mmr import mmr
            print("Running MMR")
            for topic, topic_words in topics.items():
                words = [word[0] for word in topic_words]
                word_embeddings = self._extract_embeddings(words,
                                                            method="MMR")
                topic_embedding = self._extract_embeddings(" ".join(words),
                                                            method="MMR").reshape(1, -1)
                topic_words = mmr(topic_embedding, word_embeddings, words,
                                    top_n=self.top_n_words, diversity=0.2)
                topics[topic] = [(word, value) for word, value in topics[topic] if word in topic_words]

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

    def _extract_hashtags(self, cluster):
        from mmr import mmr
        from _preprocess import extract_hash_tags

        words = list(extract_hash_tags(cluster.Document))
        if len(words) == 0:
            return words
        word_embeddings = self._extract_embeddings(words,
                                                    method="MMR")
        topic_embedding = self._extract_embeddings(" ".join(words),
                                                    method="MMR").reshape(1, -1)
        topic_words = mmr(topic_embedding, word_embeddings, words,
                            top_n=self.top_n_words, diversity=0.2)

        return topic_words

    def _preprocess_text(self,documents):
        """ Basic preprocessing of text

        Steps:
            * Remove # sign 
            * Remove urls
        """
        # cleaned_documents = [doc.replace("#", "") for doc in documents]
        cleaned_documents = [re.sub(r"http\S+", "", doc) for doc in documents]
        cleaned_documents = [re.sub(r"https\S+", "", doc) for doc in cleaned_documents]

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
