
import constants as c

##Embedder
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModel, BertTokenizer
import torch
import typing as t
import pandas as pd


MODEL_NAME = 'paraphrase-multilingual-mpnet-base-v2'
labels = ['E','S','G']
embedder = SentenceTransformer(MODEL_NAME)

def vect(text:str) -> torch.tensor:
  ''' 
  # Info
  ---
  This function transforms text to tensors

  # Parameters
  ---
  Only text

  # Results
  Tensor dim = 0

  '''
  return embedder.encode(text, convert_to_tensor=True)


def dics(lang):
  if lang == "fr":
    return c.fr_dic
  else:
    return c.en_dic


class Mean_model:
    def __init__(self, lang: str, threshold: float):
      self.lang = lang
      self.threshold = threshold
      self.Dics = dics(lang)
      self.E_vector = torch.mean(vect(self.Dics[0]), axis = 0)
      self.S_vector = torch.mean(vect(self.Dics[1]), axis = 0)
      self.G_vector = torch.mean(vect(self.Dics[2]), axis = 0)

    def esg_similarity(self, text: str) -> torch.tensor:
      '''
      # Info 
      -----
      This Function calculates the similarity 
      between the text and each one of the
      three ESG categories

      # Parameters
      -----
      It only take a text parameter
      # Returns
      ----
      It returns a torch vector containing the 
      cosine similarity for earch of the three 
      categories
      '''
      a = vect(text)
      output = []
      output.append(util.cos_sim(a, self.E_vector))
      output.append(util.cos_sim(a, self.S_vector))
      output.append(util.cos_sim(a, self.G_vector))
      return torch.cat(output, dim=1)[0]

    def esg_class(self,text:str) -> str:
      '''
      # Info 
      -----
      This Function finds the ESG class of
      the text

      # Parameters
      -----
      It only takes a text parameter
      # Returns
      ----
      It returns the ESG class as a string
      '''
      x = self.esg_similarity(text)
      k = torch.argmax(x)
      if x[k] > self.threshold:
        return labels[k]
      else:
        return 'None'
  
    def esg_filter(self,df : pd.DataFrame) -> pd.DataFrame:
      '''
      # Info
      ----
      This function removes the None-ESG tweets from
      the dataframe and adds the ESG label of each 
      tweet to the dataframe

      # Parameters
      ----
      Pandas dataframe

      # Returns
      ---
      the new modified dataframe
      '''

      df['ESG class'] = df['clean text'].apply(lambda x: self.esg_class(self,x))
      df = df[~df['ESG class'].str.contains("None")]
      df= df.reset_index(drop=True)
      return  df