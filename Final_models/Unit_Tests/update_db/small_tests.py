import unittest
import pandas as pd
import ast
import numpy as np

class Test_Update_DB_1(unittest.TestCase):
    def setUp(self):
        from update_db.update_db import Update_DB
        self.company = "tesla"
        self.updater = Update_DB(name="tesla", lang="en", size=10)

    def test_preprocessing(self):
        tweets = ['RT Sélection de produits de santé et massage \n\n👉#Réduction de 24% sur ces articles !\n 🔗https://t.co/Jpgc5L8Krz https://t.co/1NFcyua1aQ']
        prep_tweets = self.updater._preprocess_text(tweets)
        for e in prep_tweets:
            self.assertFalse('RT' in e)
            self.assertFalse('#' in e)
            self.assertFalse('https' in e)

    def test_embedder(self):
        df = pd.read_csv("test_data.csv")
        extracted_embed = self.updater.extract_embeddings(df)
        df["Embedding"] = extracted_embed.tolist()

    def test_filter(self):
        df = pd.read_csv("test_data.csv")
        df = self.updater.filter_esg(df, np.vstack([ast.literal_eval(e) for e in df.Embedding]))
        self.assertTrue(df['ESG_class'][0] == 0)
        self.assertTrue(df['ESG_class'][1] != 0)

    def test_sentiment(self):
        df = pd.read_csv("test_data.csv")
        df = self.updater.find_sentiment(df)
        self.assertTrue(df['Sentiment'][0] > df['Sentiment'][2])


if __name__ == '__main__':
    unittest.main()