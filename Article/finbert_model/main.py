import pandas as pd
from finbert_model import Finbert_model

def env_finbert(df:pd.DataFrame):
    print('Testing FinBERT Model')
    fb = Finbert_model(df=df)
    return fb.fit()

# if __name__=="main":
#     df = pd.read_csv('data.csv')
#     env_finbert(df=df)