from transformers import BertTokenizer, BertForSequenceClassification, pipeline
import pandas as pd

model = BertForSequenceClassification.from_pretrained('nbroad/ESG-BERT',
                                                      num_labels=26, 
                                                      output_attentions = False, # Whether the model returns attentions weights.
                                                      output_hidden_states = False, # Whether the model returns all hidden-states.
                                                      )
tokenizer = BertTokenizer.from_pretrained('nbroad/ESG-BERT')


esgbert = pipeline("text-classification", model = model, tokenizer=tokenizer)

def contend(df):
    df['Content'] = df['clean text english'].apply(lambda x: esgbert(x)[0]['label'])