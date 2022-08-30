'''
# Info
---
This is the main script for finding the topics.
The class ESG-Topic will extract the esg_topics from a twitter dataframe.
Steps:
        *Reduce dimension
        *Cluster embeddings
        *Extract sentiment per topic
        *Extract keywords
        *Extract hashtags
'''

import re
import numpy as np
import pandas as pd
from tqdm import tqdm
import ast
from typing import List, Tuple

import hdbscan
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans
from esg_topic.tfidf_idfi import TFIDF_IDFi
from embedder.embedder import Embedder
from tomaster import tomato
from yellowbrick.cluster.elbow import KElbowVisualizer



class ESG_Topic:

    def __init__(self, 
                cluster_model: int = 1, 
                keywords_model: int = 0,
                use_umap: int = 1, 
                dim: int = 50, 
                min_topic_size: int = 20,
                top_n_words: int = 10):
        '''
        # Info
        ---
        This is the topicer, it's goal is to put the embeddings of the database in consistent clusters
        each cluster representing a topic. From each topic we extract the average sentiment and the most
        relevant keywords and hashtags.

        # Params
        ---
        cluster_model: int, 0:HDBScan, 1:Kmeans, 2:ToMato
        keywords_model: int, 0:TF_IDF manual implementation , 1:TF_IDF with scikit-learn, 2:KeyBERT
        use_umap: int, 0: Don't use umap, 1: use umap to reduce dimension
        dim: int, goal dimension of using umap (should be less than 768)
        min_topic_szie: int, minimal tweets in a topic, relevant if you use cluster_model 0 (HDBScan)
        top_n_words: int, how many keywords and hashtags to show.

        '''

        self.cluster_model = cluster_model
        self.keywords_model = keywords_model
        self.use_umap = use_umap
        self.dim = dim
        self.min_topic_size = min_topic_size
        self.top_n_words = top_n_words
        
        self.topics = None
        self.topic_sizes = None
        print("Model loaded successfully")
        
    def fit_transform(self, df: pd.DataFrame):
        '''
        # Info
        ---
        The main funciton of the class
        Steps:
            *Reduce dimension
            *Cluster embeddings
            *Extract sentiment per topic
            *Extract keywords
            *Extract hashtags

        # Params
        ---
        df: pandas dataframe,  the dataframe we're modifying

        # Returns
        ---
        Adds the hashtags, keywords, sentiment as attributes + assigns each tweet to a topic in the dataframe
        '''

        #Preprocessed text:
        df["Prep_Tweet"] = self._preprocess_text(df.Tweet.to_list())

        #Reduce Dimension
        embeddings = np.vstack([ast.literal_eval(e) for e in df.Embedding])
        if self.use_umap == 1:
            embeddings = self._reduce_dimensionality(embeddings)
            
        #Cluster 
        df = self._cluster_embeddings(embeddings, df)

        #Extract sentiment per topic
        self.topics_sentiment = self._extract_sentiment(df)

        #Extract the topics keywords
        self.topics_keywords = self._extract_keywords(df)

        #Extract the topics'hashtags
        self.topics_hashtags =  self._extract_hashtags(df)

        df = self.add_rest(df)

        return df    

    def _reduce_dimensionality(self, embeddings:np.ndarray)->np.ndarray:
        '''
        # Info
        ---
        The function that reduces the dimension of embeddings

        # Params
        ---
        embeddings: numpy array, the array whose dimension is reduced

        # Returns
        ---
        The numpy array with reduced dimension
        '''
        print("Reducing dimension")
        umap = UMAP(n_neighbors=15, n_components = self.dim, min_dist=0.0, metric='cosine')
        try:
            umap.fit(embeddings)
            reduced_embeddings = umap.transform(embeddings)
            return np.nan_to_num(reduced_embeddings)
        except:
            return embeddings

    def _cluster_embeddings(self, embeddings, df):
        '''
        # Info
        ---
        The function that clusters embeddings

        # Params
        ---
        embeddings: numpy array, the arrays we're clustering
        df: pandas dataframe, we modify it by adding a Topic column to the dataframe

        # Returns
        ---
        The dataframe is modified and we how many topics we have
        '''
        if self.cluster_model == 0:
            print("Clustering with DBScan")
            hdbscan_model = hdbscan.HDBSCAN(min_cluster_size= self.min_topic_size,
                                                              metric='euclidean',
                                                              cluster_selection_method='eom',
                                                              prediction_data=True)
            hdbscan_model.fit(embeddings)
            df['Topic'] = hdbscan_model.labels_
            self._update_topic_size(df)

        elif self.cluster_model == 1:
            print("Clustering with KMeans")
            kmeans = KMeans(random_state=42)
            model = KElbowVisualizer(kmeans, metric='distortion', k=(1,15))
            model.fit(embeddings)
            self.nr_topics = model.elbow_value_
            print("Number of clusters = ", self.nr_topics)
            kmeans = KMeans(self.nr_topics, random_state=42)
            kmeans.fit(embeddings)
            df['Topic'] = kmeans.labels_
            self._update_topic_size(df)
            #df['dist_centroid'] = kmeans.inertia_
            #df = df.sort_values('dist_centroid')

        elif self.cluster_model == 2:
            print("Clustering with ToMATo")
            clusters = tomato(points=embeddings, k=15)
            df['Topic'] = list(clusters)
            self._update_topic_size(df)
        print("Clustered embeddings successfully")

        return df

    def _extract_sentiment(self, df:pd.DataFrame)->dict:
        '''
        # Info
        ---
        The function that finds the sentiment per topic
        It calculates the average of all tweets sentiment per topic

        # Params
        ---
        df: pandas dataframe, we use it to get the sentiment per tweet

        # Returns
        ---
        dictionnary with the topic number as key and the sentiment as value
        '''
        print("Starting sentiment analysis")
        grouped = df.groupby('Topic')
        topics_sentiment = {}
        for topic, cluster in grouped:
            topics_sentiment[topic] = sum(cluster.Sentiment.to_list())/len(cluster.Sentiment.to_list())
            print("Topic ", topic, " has a sentiment score of ", topics_sentiment[topic])
        print("Analysed Sentiment successfully")
        return topics_sentiment

    def _extract_hashtags(self, df:pd.DataFrame)->dict:
        '''
        # Info
        ---
        The function that finds hashtags per topic

        # Params
        ---
        df: pandas dataframe, we use it to get the tweets per topic to extract the hashtags

        # Returns
        ---
        dictionnary with the topic number as key and the hashtags as value
        '''
        print("Starting Hashtags extraction")
        grouped = df.groupby('Topic')
        topics_hashtags = {}
        for topic, cluster in grouped:
            words = list(self._hashtags(cluster.Tweet.to_list()))
            hashtags = self._apply_mmr(words)
            topics_hashtags[topic] = hashtags
        print("Extracted hashtags successfully")
        return topics_hashtags
        
    def _extract_keywords(self, df)->dict:
        '''
        # Info
        ---
        The function that finds keywords per topic

        # Params
        ---
        df: pandas dataframe, we use it to get the tweets per topic to extract the keywords

        # Returns
        ---
        dictionnary with the topic number as key and the keywords as value
        '''
        documents_per_topic = df.groupby(['Topic'], as_index=False).agg({'Prep_Tweet': ' '.join})
        if self.keywords_model == 0:
            self.vectorizer_model = CountVectorizer()
            self.scores, words = self._weighting_words(documents_per_topic, df)
            return self._extract_words_per_topic(words)

        elif self.keywords_model == 1:
            
            vectorizer = TfidfVectorizer()

            # Creating a sparse matrix containing the TFIDF score for each word
            vectors = vectorizer.fit_transform(documents_per_topic.Tweet.to_list())

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
            
            return {label: values[:self.top_n_words] for label, values in topics.items()}

        elif self.keywords_model == 2:
            topics = {}
            from keybert import KeyBERT
            kw_model = KeyBERT()
            for i, doc in enumerate(documents_per_topic.Tweet.to_list()):
                topics[i] = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 1), stop_words='english',
                                        use_mmr=True, diversity=0.2, nr_candidates=30, top_n=10)
            return topics

    def _weighting_words(self, documents_per_topic:pd.DataFrame, all_documents:pd.DataFrame):
        '''
        # Info
        ---
        In the continuation of the process of TFIDf manually (keywords_model=0)
        It assigns a weight to each word in topic

        # Params
        ---
        documents_per_topic: pandas dataframe of tweets per topic
        all_documents: pandas dataframe of all tweets

        # Returns
        ---
        scores: sp.csr_matrix containing the weight of words in each topic
        words: the words in the all the documents
        '''
        concatenated_documents = documents_per_topic.Prep_Tweet.values
        origin_documents = all_documents.Prep_Tweet.values
        
        # count the words in a cluster
        self.vectorizer_model.fit(concatenated_documents)
        words = self.vectorizer_model.get_feature_names()
        
        # k * vocab
        X_per_cluster = self.vectorizer_model.transform(concatenated_documents)
        # D * vocab
        X_origin = self.vectorizer_model.transform(origin_documents)
        
        socres = TFIDF_IDFi(X_per_cluster, X_origin, all_documents).socre()

        return socres, words
    

    def _extract_words_per_topic(self, words)->dict:
        '''
        # Info
        ---
        In the continuation of the process of TFIDf manually (keywords_model=0)
        It runs mmr on the top 30 words in term of weight than returns the top
        10 words

        # Params
        ---
        words: all the mentioned words in the documents

        # Returns
        ---
        dictionnary with the topic number as key and the keywords as value
        '''
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
            topics[topic] = [word for word, value in topics[topic] if word in topic_words]
        topics = {label: values[:self.top_n_words] for label, values in topics.items()}
        # topics = {label: [e[0] for e in values] for label, values in topics.items()}

        return topics


    def _apply_mmr(self, words:List[str], diversity:float = 0.5)->List[str]:
        '''
        # Info
        ---
        Applies mmr method on a list of words

        # Params
        ---
        words: all the mentioned words in the documents
        diversity: float representing the diversity of results

        # Returns
        ---
        returns a list containing the top 10 words according to the mmr
        '''
        if len(words) == 0:
            return []
        from esg_topic.mmr import mmr
        word_embeddings = self._extract_embeddings(words)
        topic_embedding = self._extract_embeddings(" ".join(words)).reshape(1, -1)
        topic_words = mmr(topic_embedding, word_embeddings, words,
                            top_n=self.top_n_words, diversity=diversity)
        return topic_words

    def add_rest(self, df):
        df['Cluster_Sentiment'] = df.apply(lambda row : self.topics_sentiment[row['Topic']], axis=1)
        df['Cluster_Keywords'] = df.apply(lambda row : self.topics_keywords[row['Topic']], axis=1)
        df['Cluster_Hashtags'] = df.apply(lambda row : self.topics_hashtags[row['Topic']], axis=1)
        return df

    def get_topics(self)->dict:
        '''
        # Info
        ---
        get the topics keywords dictionnary

        # Params
        ---
        self

        # Returns
        ---
        the topics keywords dictionnary
        '''
        return self.topics
    
    def get_topic(self, topic_id:int)->List[str]:
        '''
        # Info
        ---
        get a specific topic keywords dictionnary

        # Params
        ---
        topic_id: integer representing the topic you want

        # Returns
        ---
        The topic keywords dictionnary
        '''
        if topic_id in self.topics:
            return self.topics[topic_id]
        else:
            return False

    def _update_topic_size(self, df):
        sizes = df.groupby(['Topic']).count().sort_values("Tweet", ascending=False).reset_index()
        self.topic_sizes = dict(zip(sizes.Topic, sizes.Tweet))    

    @staticmethod
    def _extract_embeddings(documents: List[str])->np.ndarray:
        '''
        # Info
        ---
        extracts embeddings from text

        # Params
        ---
        documents: list of text

        # Returns
        ---
        The embeddings of the text
        '''
        embedder = Embedder(1)
        embeddings = embedder.embed(documents)
        return embeddings

    @staticmethod
    def _hashtags(cluster:List[str])->set:
        '''
        # Info
        ---
        It finds the hashtags in the List of tweets

        # Params
        ---
        cluster: list of tweets in a cluster

        # Returns
        ---
        A set containing all the hashtags that are menitonned
        '''
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


    @staticmethod
    def _preprocess_text(documents:List[str])->List[str]:
        """ Basic preprocessing of text
        Steps:
            * Remove # sign 
            * Remove urls
            * Remove @ tags
            * Remove RT (retweet)
        """
        cleaned_documents = [doc.replace("#", "") for doc in documents]
        cleaned_documents = [re.sub(r"http\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [re.sub(r"https\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [re.sub(r"@\S+", "", doc) for doc in cleaned_documents]
        cleaned_documents = [doc.replace("RT", "") for doc in cleaned_documents]

        return cleaned_documents