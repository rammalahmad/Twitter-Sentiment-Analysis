from db_master import DB_Master
import pandas as pd
from esg_topic.esg_topic import ESG_Topic
import sys

def visualise(name, sdate:str = "2006-08-23 10:23:00", edate:str = "2023-08-23 10:23:00"):

    db_master = DB_Master(name=name)
    # Find corresponding df
    df = db_master.fit(sdate, edate)

    # Do the clustering
    topicer = ESG_Topic()
    df = topicer.fit_transform(df)

    # Drop irrelevant columns
    df = df.rename(columns={"Topic": "Cluster"})
    df = df.drop(columns=['Embedding', 'Prep_Tweet'])
    
    # remove duplicates
    df = df.drop_duplicates(subset=['Tweet'], keep="first")
    # Save the topicer work
    db_name = name
    db_master.save_df(df=df, db_name=db_name+"_"+str(sdate).replace(":", ".")+"_"+str(edate).replace(":", "."))


if __name__ == '__main__':
    try:
        visualise(str(sys.argv[1]))
    except:
        print('Execution interrupted')