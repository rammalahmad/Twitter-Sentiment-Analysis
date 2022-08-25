from typing import List
from deep_translator import GoogleTranslator
from transformers import pipeline, BertTokenizer, BertForSequenceClassification

class Finbert_model:

    def __init__(self, lang:str = "en"):

        self.lang = lang

        finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-esg',num_labels=4)
        tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-esg')
        self.filter = pipeline("text-classification", model=finbert, tokenizer=tokenizer)
        
    def fit(self, documents):
        documents = self.translate(documents)
        l = self.filter(documents)
        result = []
        for t in l:
            if t['label']=="Environmental":
                result += [0]
            elif t['label']=="Social":
                result += [1]
            elif t['label']=="Governance":
                result += [2]
            else:
                result += [-1]
        return result

    def translate(self, documents):
        if self.lang != "en":
            return [GoogleTranslator(source=self.lang, target="en").translate(text) for text in documents]
        else:
            return documents