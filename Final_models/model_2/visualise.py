from db_master import DB_Master
import pandas as pd
import ast
import sys


def visualise(name, sdate:str = "2006-08-23 10:23:00", edate:str = "2023-08-23 10:24:00"):
    db_master = DB_Master(name=name)
    df = db_master.fit(sdate, edate)

    # Add cluster sentiment, keywords and hashtags
    df = visu_elements(df)

    # Remove irrelevant columns
    df = df.drop(columns=['Embedding', 'Keywords', 'Hashtags'])
    # Remove duplicate tweets
    df = df.drop_duplicates(subset=['Tweet'], keep="first")
    # Save the topicer work
    db_name = name
    db_master.save_df(df=df, db_name=db_name+"_"+str(sdate).replace(":", ".")+"_"+str(edate).replace(":", "."))


def visu_elements(df:pd.DataFrame):
    grouped = df.groupby('Cluster')
    topics_sentiment = {}
    topics_keywords = {}
    topics_hashtags = {}
    for topic, cluster in grouped:
        topics_sentiment[topic] = sum(cluster.Sentiment.to_list())/len(cluster.Sentiment.to_list())
        topics_keywords[topic] = list(set([j for sub in [ast.literal_eval(e) for e in cluster.Keywords.to_list()] for j in sub]))
        topics_hashtags[topic] = list(set([j for sub in [ast.literal_eval(e) for e in cluster.Hashtags.to_list()] for j in sub]))

    df['Cluster_sentiment'] = df.apply(lambda row : topics_sentiment[row['Cluster']], axis=1)
    df['Cluster_Keywords'] = df.apply(lambda row : topics_keywords[row['Cluster']], axis=1)
    df['Cluster_Hashtags'] = df.apply(lambda row : topics_hashtags[row['Cluster']], axis=1)
    return df

if __name__ == '__main__':
    try:
        visualise(str(sys.argv[1]))
    except:
        print('Execution interrupted')