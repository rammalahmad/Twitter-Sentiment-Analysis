import re

def extract_hash_tags(documents):
    x = set()
    for text in documents:
        y = set(part[1:] for part in text.split() if (part.startswith('#') & (("tesla" in part or "Tesla" in part or "TESLA" in part or "elon" in part) == False)) )
        x = x.union(y)
    return x
