import unittest
import pandas as pd
import ast
import numpy as np

class Test_Update_DB(unittest.TestCase):
    def setUp(self):
        from update_db.update_db import Update_DB
        self.company = "tesla"
        self.updater = Update_DB(name="tesla", lang="en", size=50)

    def test_scraping(self):
        df = self.updater.scrap_df()
        self.assertIsInstance(df, pd.DataFrame)

    def test_preprocessing(self):
        df = pd.read_csv("tesla_test.csv")
        df["Prep_Tweet"] = self.updater._preprocess_text(df.Tweet.to_list())

    def test_embedder(self):
        df = pd.read_csv("tesla_test.csv")
        extracted_embed = self.updater.extract_embeddings(df)
        df["Embedding"] = extracted_embed.tolist()

    def test_filter(self):
        df = pd.read_csv("tesla_test.csv")
        df = self.updater.filter_esg(df, np.vstack([ast.literal_eval(e) for e in df.Embedding]))

    def test_sentiment(self):
        df = pd.read_csv("tesla_test.csv")
        df = self.updater.find_sentiment(df)

if __name__ == '__main__':
    unittest.main()