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


    def fit(self, documents):
        l = self.sentiment(documents)
        esg_score=0

        if self.model == 0:
            for e in l:
                if e['label'] == 'Neutral':
                    esg_score+= 0
                if e['label'] == 'Positive':
                    esg_score+= e['score']
                if e['label'] == 'Negative':
                    esg_score+= -e['score']

        elif self.model == 1:
            for e in l:
                nb_stars = int(e['label'][0])
                esg_score += ((nb_stars - 3)/2)*(e['score'])

        return esg_score

    def score(self, text):

        e = self.sentiment(text)

        if self.model == 0:
            if e['label'] == 'Neutral':
                return 0

            elif e['label'] == 'Positive':
                return e['score']

            elif e['label'] == 'Negative':
                return -e['score'] 