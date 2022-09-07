'''
# Info
---
In this script we define the Embedder whose primary role is to extract the embeddings from
the texts.
The embedder has three possible models.
0: ESG_BERT
1: SBERT
2: xlm-roBERTa-base
'''


from typing import List # , Tuple, Union, Mapping, Any, Callable, Iterable
import numpy as np
from tqdm import tqdm


class Embedder:

    def __init__(self, index:int = 0):
        '''
        # Info
        ---
        Calculates the embeddings array for documents

        # Params
        ---
        index:int represents the model
        0: ESG_Bert
        1: SBERT
        2: xlm-roBERTa-base
        '''
        self.index=index
        if index == 0:
            from model_1.embedder.ESG_BERT import model, tokenizer
            self.model = model
            self.tokenizer = tokenizer
        elif index == 1:
            from model_1.embedder.sbert import model
            self.model = model
        elif index == 2:
            from model_1.embedder.xlm_roberta import model, tokenizer
            self.model = model
            self.tokenizer = tokenizer
        

    def embed(self, documents:List[str], b_size:int = 1) -> np.ndarray:
        '''
        # Info
        ---
        Calculates the embeddings array for documents

        # Params
        ---
        documents: List[str], the list of text
        b_size: int, the batch size

        # Result
        ---
        np.ndarray the embeddings array
        '''
        if self.index == 0:
            l = []
            for document in tqdm(documents, "Progress"):
                tokens = self.tokenizer(document, return_tensors='pt')
                output = self.model(**tokens)
                l += [output.logits.detach().numpy()]
            return np.vstack(l)
            
        elif self.index == 1:
            return np.array(self.model.encode(documents, batch_size=b_size, show_progress_bar=True))

        elif self.index == 2:
            l = []
            for document in tqdm(documents, "Progress"):
                tokens = self.tokenizer(document, return_tensors='pt', padding=True)
                output = self.model(**tokens)
                l += [output["pooler_output"].detach().numpy()]
            return np.vstack(l)
