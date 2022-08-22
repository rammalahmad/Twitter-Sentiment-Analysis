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
