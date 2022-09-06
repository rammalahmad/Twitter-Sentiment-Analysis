import unittest
import pandas as pd
import ast
import numpy as np

class Test_ESG_Topic(unittest.TestCase):
    def setUp(self):
        from esg_topic.esg_topic import ESG_Topic
        self.topicer = ESG_Topic()
        self.df = pd.read_csv('tesla_test.csv')

    def test_gobal(self):
        self.topicer.fit_transform(df=self.df).to_csv('tested_df.csv')

if __name__ == '__main__':
    unittest.main()