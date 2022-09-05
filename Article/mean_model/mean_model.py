import numpy as np
import pandas as pd
from typing import List
from tqdm import tqdm

class Mean_Model:
    def __init__(self, df:pd.DataFrame, topic_dict:List[str], topic_name:str):
        # Adding it to the class
        self.df = df
        self.topic_dict = topic_dict
        self.topic_name = topic_name
        self.data = self.df['text'].to_list()

    def fit(self):
        # Get the texts embeddings
        try:
            self.embeddings = self.get_embeddings()
        except:
            self.generate_embeddings()
            self.embeddings = self.get_embeddings()
        # Get the topic mean embedding
        try:
            self.top_embed = self.get_top_embed()
        except:
            self.generate_topic_embedding()
            self.top_embed = self.get_top_embed()
        
        # find the label according to the cosine similarity
        from label import Label
        labeliser = Label(embeddings=self.embeddings, topic_embedding=self.top_embed)
        labeliser.fit()

        # test for many thresholds
        thresholds = [i/100 for i in range(1,95)]
        for threshold in tqdm(thresholds, 'Progress:'):
            self.df['predicted'+str(threshold)] = labeliser.label(threshold=threshold)
        self.df.to_csv('tested_data.csv')
        return self.df
        
    def generate_topic_embedding(self):
        from generate_topic_embedding import Gen_Top
        generator = Gen_Top(topic_dict=self.topic_dict, topic_name=self.topic_name)
        generator.fit()

    def generate_embeddings(self):
        from generate_embeddings import Gen_Embed
        generator = Gen_Embed(topic_name=self.topic_name, data=self.data)
        generator.fit()

    def get_top_embed(self):
        return np.load(self.topic_name+"_embedding.npy")

    def get_embeddings(self):
        return np.load(self.topic_name+'_data_embeddings.npy')