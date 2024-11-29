from transformers import AutoTokenizer, AutoConfig, RobertaForSequenceClassification
from transformers import pipeline

model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
sentiment = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path, top_k=3)

def rob_score(tweet):
    l = sentiment(tweet)
    s=0
    for e in l:
        if e['label'] == 'Neutral':
            s+= 0

        if e['label'] == 'Positive':
            s+= e['score']

        if e['label'] == 'Negative':
            s+= -e['score']
    return s

model_1 = "nlptown/bert-base-multilingual-uncased-sentiment"
sentiment_1 = pipeline("sentiment-analysis", model=model_1, tokenizer=model_1, top_k=5)

def uncased_score(tweet):
    l = sentiment_1(tweet)
    s = 0
    for e in l:
        nb_stars = int(e['label'][0])
        s += ((nb_stars - 3)/2)*(e['score'])
    return s


# def sentm(df):
#     df['Sentiment'] = df['clean text'].apply(lambda x: score(x))

