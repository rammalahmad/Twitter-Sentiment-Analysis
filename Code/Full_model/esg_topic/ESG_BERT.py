'''
# Info
---
In this script we modified the esg_bert model by replacing the classificaiton layer 
in the model by a an identity thus extracting the embeddings produced by the model.
The main motivation to consider such a model in the first place was that the model had a 
good classification performance on esg topics, thus it was interesting to test the
embeddings it produced.
One main problem with this model is that it's not multiling making it unpractical unless 
we use a powerful translation tool...
'''

from transformers import BertForSequenceClassification, BertTokenizer
import torch

model = BertForSequenceClassification.from_pretrained(
    'nbroad/ESG-BERT', 
    num_labels = 26, #number of classifications
   output_attentions = False, # Whether the model returns attentions weights.
    output_hidden_states = False, # Whether the model returns all hidden-states.
)

tokenizer = BertTokenizer.from_pretrained('nbroad/ESG-BERT')

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model.to(device)

model.classifier = torch.nn.Identity()