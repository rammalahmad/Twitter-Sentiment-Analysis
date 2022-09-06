#!/usr/bin/python
from db_master import DB_Master
import pandas as pd
from update_db.update_db import Update_DB

import sys



def refresh(name:str):
    # Find english tweets
    db_master = DB_Master(name=name)
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

    # Add log create
    df_not_esg['log'] = 'C'
    df_esg['log'] = 'C'

    # Save the logs
    db_name = name
    db_master.update_df(df=df_esg, db_name=db_name + "_log")
    db_master.update_df(df=df_not_esg, db_name=db_name+"_not_esg_log")

    # Save the newly acquired tweets to db
    db_master.update_df(df=df_esg.drop(columns=['log']), db_name=db_name)
    db_master.update_df(df=df_not_esg.drop(columns=['log']), db_name=db_name+"_not_esg")

    # # Refresh the found db in DB_Master
    # db_master.find_db()

if __name__ == '__main__':
    try:
        refresh(str(sys.argv[1]))
    except:
        print('Execution interrupted')