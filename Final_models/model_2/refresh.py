from update_db.update_db import Update_DB
from esg_topic.esg_topic import ESG_Topic
from db_master import DB_Master
import pandas as pd
import ast
import sys


def refresh(name):
    db_master = DB_Master(name=name)
    # Find english tweets
    updater = Update_DB(name=name, lang="en", last_date=db_master.find_last_date())
    df_esg_en, df_not_esg_en = updater.fit()

    # Find french tweets
    updater = Update_DB(name=name, lang="fr", last_date=db_master.find_last_date())
    df_esg_fr, df_not_esg_fr = updater.fit()

    # Merge the french with english
    df_esg = pd.concat([df_esg_en, df_esg_fr], ignore_index=True)
    df_not_esg = pd.concat([df_not_esg_en, df_not_esg_fr], ignore_index=True)

    # Sort them per date
    df_esg.sort_values(by='Date', ascending = False, inplace=True)
    df_not_esg.sort_values(by='Date', ascending = False, inplace=True)
    
    # Put together the new database
    df_not_esg['log'] = 'C'
    df_esg['log'] = 'C'
    if db_master.found_db:
        old_db = db_master.db[['Tweet', 'Date', 'Language', 'Embedding', 'ESG_class', 'Sentiment']]
        old_db['Embedding'] = old_db['Embedding'].apply(lambda x: ast.literal_eval(x))
        old_db['log'] = 'U'

        new_db = pd.concat([df_esg, old_db], ignore_index=True)
    else:
        new_db = df_esg

    # Cluster the outcome
    topicer = ESG_Topic()
    new_db = topicer.fit_transform(new_db)

    new_db = new_db.rename(columns={"Topic": "Cluster"})
    new_db = new_db.drop(columns=['Prep_Tweet'])

    db_name = name

    # Save the logs
    db_master.update_df(df=df_not_esg, db_name=db_name+"_not_esg_log")
    db_master.update_df(df=new_db, db_name=db_name+"_log")

    # Save the newly acquired tweets
    db_master.update_df(df=df_not_esg.drop(columns=['log']), db_name=db_name+"_not_esg")
    db_master.save_df(df=new_db.drop(columns=['log']), db_name=db_name)

    # Refresh the found db in DB_Master
    # db_master.find_db()


if __name__ == '__main__':
    try:
        refresh(str(sys.argv[1]))
    except:
        print('Execution interrupted')