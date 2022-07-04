# PreProcessing Tweets
import pandas as pd
import numpy as np
import json
import preprocessor as p
import matplotlib.pyplot as plt
import re, string, unicodedata
import nltk
import seaborn as sns
import nltk
import textwrap

from collections import Counter
from wordcloud import WordCloud
from ekphrasis.classes.segmenter import Segmenter
from nltk import word_tokenize, sent_tokenize, FreqDist
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from spellchecker import SpellChecker

nltk.download
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('omw-1.4')


lemmatizer = nltk.stem.WordNetLemmatizer()
w_tokenizer =  TweetTokenizer()

class preprocess:  
      def collect_mentions(text):
        return re.findall("@([a-zA-Z0-9_]{1,50})", text)

      def collect_hash(text):
        return re.findall(r"#(\w+)", x)

      def collect_stocks(text):
        return re.findall("\$([a-zA-Z0-9_]{1,50})", x)

      def collect_urls(text):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet)
        result =[]
        for url in urls:
          try:
            res = urllib2.urlopen(url)
            actual_url = res.geturl()
            result += [actual_url]
          except:
            result += [url]
        return result

      def clean_text_c(text):
        return p.clean(text)

      def remove_numbers(text):
        p_text = re.sub(r'#\S+|\d+',' ',text)

      def remove_hash(text):
        return text.replace("#", "")

      def remove_dollar(text):
        return re.sub("\$[A-Za-z0-9_]+"," ", text)
        
      def remove_punctuation(text):
        return re.sub(r'[^\w\s]', '', text)

      def lower(text):
        return text.lower()

      def lemmatize_text(text):
        L = w_tokenizer.tokenize((text))
        return [(lemmatizer.lemmatize(w)) for w in w_tokenizer.tokenize((text))] 
        
      def remove_stop_words(words):
        stop_words = set(stopwords.words('english'))
        dic = {'ha','via', 'yet', 'af', 'youre'}
        stop_words = stop_words.union(dic)
        return [item for item in words if item not in (stop_words)]

      def remove_misspelled(words):
        spell = SpellChecker(language = 'en')
        misspelled = spell.unknown(words)
        for word in misspelled:
          words.remove(word)




      
  