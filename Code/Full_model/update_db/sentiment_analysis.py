from transformers import pipeline

class Sent_model:
    def __init__(self, model:int = 0):
        self.model = model

        if model == 0:
            model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
            top_k = 3
        elif model == 1:
            model_path = "nlptown/bert-base-multilingual-uncased-sentiment"
            top_k = 5

        self.sentiment = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path, top_k=top_k)

    def fit(self,documents):
        doc_score = self.doc_score(documents)
        return sum(doc_score)/len(doc_score)

    def doc_score(self, documents):
        sent_doc = self.sentiment(documents)
        return [self.txt_score(sent_txt) for sent_txt in sent_doc]

    def txt_score(self, sent_txt):
        txt_score = 0
        if self.model == 0:
            for e in sent_txt:
                if e['label'] == 'Neutral':
                    txt_score += 0
                if e['label'] == 'Positive':
                    txt_score += e['score']
                if e['label'] == 'Negative':
                    txt_score += -e['score']
        elif self.model == 1:
            for e in sent_txt:
                nb_stars = int(e['label'][0])
                txt_score += ((nb_stars - 3)/2)*(e['score'])
        return txt_score
