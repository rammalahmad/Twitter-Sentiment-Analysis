from typing import List
from transformers import pipeline, BertTokenizer, BertForSequenceClassification
import pandas as pd

class Finbert_model:
    def __init__(self, df:pd.DataFrame):
        finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-esg',num_labels=4)
        tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-esg')
        self.filter = pipeline("text-classification", model=finbert, tokenizer=tokenizer)
        self.df = df

    def fit(self):
        result = self.fit(self.df.text.to_list())
        self.df['finbert_prediction'] = result
        self.df.to_csv('tested_data.csv')
        return self.df

    def label(self, documents:List[str])->List[int]:
        l = self.filter(documents)
        result = []
        for t in l:
            if t['label']=="Environmental":
                result.append(1)
            else:
                result.append(0)
        return result