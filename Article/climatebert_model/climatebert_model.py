from typing import List
from transformers import pipeline, AutoTokenizer, BertForSequenceClassification

class Climate_BERT_model:

    def __init__(self):

        model = BertForSequenceClassification.from_pretrained('climatebert/environmental-claims',num_labels=2)
        tokenizer = AutoTokenizer.from_pretrained('climatebert/environmental-claims')
        self.filter = pipeline("text-classification", model=model, tokenizer=tokenizer)
        
    def fit(self, documents:List[str])->List[int]:
        l = self.filter(documents)
        result = []
        for t in l:
            if t['label']=="yes":
                result.append(1)
            else:
                result.append(0)
        return result