import pandas as pd
df = pd.read_csv('data.csv')
from climatebert_model import Climate_BERT_model

if __name__=="main":
    print('Testing ClimateBERT Model')
    ecm = Climate_BERT_model()
    result = ecm.fit(df.text.to_list())
    df['ecm_prediction'] = result
    df.to_csv('tested_data.csv')