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
        doc_score=0

        if self.model == 0:
            for t in l:
                txt_score = 0
                for e in t:
                  if e['label'] == 'Neutral':
                      txt_score += 0
                  if e['label'] == 'Positive':
                      txt_score += e['score']
                  if e['label'] == 'Negative':
                      txt_score += -e['score']
                doc_score += txt_score

        elif self.model == 1:
            for t in l:
                txt_score = 0
                for e in t:
                    nb_stars = int(e['label'][0])
                    txt_score += ((nb_stars - 3)/2)*(e['score'])
                doc_score += txt_score

        return doc_score / (len(documents))

    # def score(self, text):

    #     e = self.sentiment(text)

    #     if self.model == 0:
    #         if e['label'] == 'Neutral':
    #             return 0

    #         elif e['label'] == 'Positive':
    #             return e['score']

    #         elif e['label'] == 'Negative':
    #             return -e['score']
