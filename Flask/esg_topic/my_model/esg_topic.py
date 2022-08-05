import re
import numpy as np
import pandas as pd
from tqdm import tqdm

from typing import List, Tuple

import hdbscan
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from constants import en_dic, fr_dic
from sklearn.cluster import KMeans
from tfidf_idfi import TFIDF_IDFi
from _utils import Embedder
from tomaster import tomato
from yellowbrick.cluster.elbow import kelbow_visualizer
from sentiment_analysis import Sent_model
import sys

path = r'C:\Users\User\Desktop\Ahmad\Stages\SurfMetrics\Git\Flask\esg_topic\Data'


class ESG_Topic:

    def __init__(self, 
                embed_model: int = 0,
                esg_model:int = 0,
                cluster_model: int = 1, 
                keywords_model: int = 1,
                sent_model: int = 0,
                dim: int = 50, 
                min_topic_size: int = 20,
                top_n_words: int = 10, 
                embeddings: np.ndarray = None):

        self.embed_model = embed_model
        self.esg_model = esg_model
        self.cluster_model = cluster_model
        self.keywords_model = keywords_model
        self.sent_model = sent_model
        self.dim = dim
        self.min_topic_size = min_topic_size
        self.top_n_words = top_n_words
        self.embeddings = embeddings
        

        self.topics = None
        self.topic_sizes = None
        print("Model loaded successfully")
        
    def fit_transform(self, documents, documents_name:str):
        
        #Preprocessing:
        documents = self._preprocess_text(documents)

        #Extract Embeddings:
        if self.embeddings is None:
            try:
                name = str(self.embed_model) + documents_name + ".npy"
                self.embeddings = np.load(path+"/"+name)
                print("The embeddings are already extracted")
            except Exception:
                self.embeddings = self._extract_embeddings(documents, documents_name)

        #Initialize return DataFrame
        my_df = pd.DataFrame({"Document": documents,
                                  "ID": range(len(documents)),
                                  "Topic": None})
        embeddings = self.embeddings

        #Classify the tweets into E, S & G & Remove the None ESG tweets
        my_df = self._filter_esg(df=my_df)
        my_df = my_df[~my_df['ESG_class'] == -1]
        my_df= my_df.reset_index(drop=True)

        #Reduce Dimension
        embeddings = self._reduce_dimensionality(embeddings)

        #Cluster the outcome
        documents = self._cluster_embeddings(embeddings, my_df)

        #Extract the topics keywords
        self._extract_keywords(my_df)

        # #Extract the topics'hashtags
        self._extract_hashtags(my_df)

        # #Sentiment analysis
        self._extract_sentiment(my_df)

        self.df = my_df
        return my_df

 
    def _extract_embeddings(self, documents, documents_name="", method="documents"):
        self.embedder = Embedder(self.embed_model)
        if method == "documents":
            embeddings = self.embedder.embed(documents)
            name = str(self.embed_model) + documents_name
            np.save(path+"/"+name, embeddings)
            print("Extracted the embeddings successfully")
            return embeddings
        elif method == "MMR":
            embeddings = self.embedder.embed(documents)
            return embeddings
        
    def _filter_esg(self, df) -> pd.DataFrame:

        if self.esg_model == 0:
            from  _esg_filter import GS_model
            filter = GS_model(threshold = 0.5)

        elif self.esg_model == 1:
            from _esg_filter import Mean_model
            filter = Mean_model(threshold = 0.15)

        df['ESG_class'] = filter.fit(self.embeddings)
        print("ESG_filtered the tweets successfully")

        return df


    def _reduce_dimensionality(self, embeddings):
        umap = UMAP(n_neighbors=15, n_components = self.dim, min_dist=0.0, metric='cosine')
        umap.fit(embeddings)
        reduced_embeddings = umap.transform(embeddings)
        print("Reduced dimension successfully")
        
        return np.nan_to_num(reduced_embeddings)

    def _cluster_embeddings(self, embeddings, documents):

        if self.cluster_model == 0:
            print("Clustering with DBScan")
            hdbscan_model = hdbscan.HDBSCAN(min_cluster_size= self.min_topic_size,
                                                              metric='euclidean',
                                                              cluster_selection_method='eom',
                                                              prediction_data=True)
            hdbscan_model.fit(embeddings)
            documents['Topic'] = hdbscan_model.labels_
            self._update_topic_size(documents)

        elif self.cluster_model == 1:
            print("Clustering with KMeans")
            kmeans = KMeans(random_state=42)
            l = []
            x1 = kelbow_visualizer(kmeans, embeddings, metric='silhouette', k=(2,15)).elbow_value_
            l.append(x1)
            x2 = kelbow_visualizer(kmeans, embeddings, metric='calinski_harabasz', k=(2,15)).elbow_value_
            l.append(x2)
            x3 = kelbow_visualizer(kmeans, embeddings, metric='distortion', k=(2,15)).elbow_value_
            l.append(x3)

            self.nr_topics = max(l)
            print("Number of clusters = ", self.nr_topics)
            kmeans = KMeans(self.nr_topics, random_state=42)
            kmeans.fit(embeddings)
            documents['Topic'] = kmeans.labels_
            self._update_topic_size(documents)
            documents['dist_centroid'] = kmeans.inertia_
            documents = documents.sort_values('dist_centroid')

        elif self.cluster_model == 2:
            print("Clustering with ToMATo")
            clusters = tomato(points=embeddings, k=15)
            documents['Topic'] = list(clusters)
            self._update_topic_size(documents)
        print("Clustered embeddings successfully")

        return documents


    def _extract_keywords(self, documents):
        documents_per_topic = documents.groupby(['Topic'], as_index=False).agg({'Document': ' '.join})
        if self.keywords_model == 0:
            self.vectorizer_model = CountVectorizer()
            self.scores, words = self._weighting_words(documents_per_topic, documents)
            self.topics = self._extract_words_per_topic(words)

        elif self.keywords_model == 1:
            
            vectorizer = TfidfVectorizer()

            # Creating a sparse matrix containing the TFIDF score for each word
            vectors = vectorizer.fit_transform(documents_per_topic.Document.to_list())

            # Getting the list of words
            words = vectorizer.get_feature_names()

            # Findind the top 30 indices in the sparse matrix
            indices = self._top_n_idx_sparse(vectors, 60)

            # Create keywords dictionary
            topics = {topic: [words[int(word_index)] for word_index in indices[i]] for i,topic in enumerate(documents_per_topic.Topic.to_list())}

            print("Running MMR")
            for topic, words in topics.items():
                topic_words = self._apply_mmr(words)
                topics[topic] = [[word] for word in topics[topic] if word in topic_words]
            self.topics = {label: values[:self.top_n_words] for label, values in topics.items()}

        elif self.keywords_model == 2:
            topics = {}
            from keybert import KeyBERT
            kw_model = KeyBERT()
            for i, doc in enumerate(documents_per_topic.Document.to_list()):
                topics[i] = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 1), stop_words='english',
                                        use_mmr=True, diversity=0.2, nr_candidates=30, top_n=10)
            self.topics = topics

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
        
        print("Running MMR")
        for topic, topic_words in topics.items():
            words = [word[0] for word in topic_words]
            topic_words = self._apply_mmr(words)
            topics[topic] = [(word, value) for word, value in topics[topic] if word in topic_words]
        topics = {label: values[:self.top_n_words] for label, values in topics.items()}

        return topics

    def _apply_mmr(self, words, diversity:float = 0.5):
        from mmr import mmr
        word_embeddings = self._extract_embeddings(words,
                                                    method="MMR")
        topic_embedding = self._extract_embeddings(" ".join(words),
                                                    method="MMR").reshape(1, -1)
        topic_words = mmr(topic_embedding, word_embeddings, words,
                            top_n=self.top_n_words, diversity=diversity)
        return topic_words

    def _extract_hashtags(self, df):
        grouped = df.groupby('Topic')
        self.topics_hashtags = {}
        for topic, cluster in grouped:
            words = list(self._hashtags(cluster.Document))
            hashtags = self._apply_mmr(words)
            self.topics_hashtags[topic] = hashtags
        print("Extracted hashtags successfully")

    def _extract_sentiment(self, df):
        sent_analyst = Sent_model(self.sent_model)
        grouped = df.groupby('Topic')
        self.topics_sentiment = {}
        for topic, cluster in grouped:
            self.topics_sentiment[topic] = sent_analyst.fit(cluster.Document.to_list())
        print("Analysed Sentiment successfully")

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

    @staticmethod
    def _hashtags(cluster):
        x = set()
        for text in cluster:
            y = set(part[1:] for part in text.split() if (part.startswith('#') & (("tesla" in part or "Tesla" in part or "TESLA" in part or "elon" in part) == False)) )
            x = x.union(y)
        return x 

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