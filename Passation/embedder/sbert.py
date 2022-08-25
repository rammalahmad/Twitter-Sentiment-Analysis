'''
# Info
---
In this script we just import the sbert model, it's multiling
'''
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')