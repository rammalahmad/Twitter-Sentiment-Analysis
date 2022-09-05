# Importing the data
import pandas as pd
from gs_model import GS_Model
import operator

def env_gs(df:pd.DataFrame):
    df = df[:100]
    print('Testing Gram-Schmidt Model')
    from topic_dict import topic_dict, topic_name
    gs = GS_Model(df=df, topic_dict=topic_dict, topic_name=topic_name)
    tested_df = gs.fit()

    accuracy = {}
    for colname, _ in tested_df.drop(columns=['text', 'label']).iteritems():
        l = (tested_df.drop(columns=['text', 'label'])[colname] == df['label']).to_list()
        accuracy[float(colname.replace('predicted', ''))] = sum(l)/len(l)
    return max(accuracy.items(), key=operator.itemgetter(1))

# if __name__=="main":
#     df = pd.read_csv('data.csv')
#     env_gs(df=df)