from transformers import AutoTokenizer, AutoConfig, RobertaForSequenceClassification
from transformers import pipeline

model_path = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
sentiment = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)

def score(tweet):
    l = sentiment(tweet)

    if l[0]['label'] == 'Neutral':
        return 0

    if l[0]['label'] == 'Positive':
        return l[0]['score']

    if l[0]['label'] == 'Negative':
        return (-1)*l[0]['score']

def sentm(df):
    df['Sentiment'] = df['clean text'].apply(lambda x: score(x))

