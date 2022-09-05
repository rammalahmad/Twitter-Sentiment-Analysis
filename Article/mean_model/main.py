import pandas as pd
from mean_model import Mean_Model
import operator

def env_mean(df:pd.DataFrame):
    df = df[:100]
    print('Testing Mean Model')
    from topic_dict import topic_dict, topic_name
    mean = Mean_Model(df=df, topic_dict=topic_dict, topic_name=topic_name)
    tested_df =  mean.fit()

    accuracy = {}
    for colname, _ in tested_df.drop(columns=['text', 'label']).iteritems():
        l = (tested_df.drop(columns=['text', 'label'])[colname] == df['label']).to_list()
        accuracy[float(colname.replace('predicted', ''))] = sum(l)/len(l)
    return max(accuracy.items(), key=operator.itemgetter(1))

# if __name__=="main":
#     df = pd.read_csv('data.csv')
#     env_mean(df=df)