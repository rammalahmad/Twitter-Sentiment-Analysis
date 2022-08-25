'''
# Info
---
In this script we modified the xlm-roberta model by replacing the classificaiton layer 
in the model by a an identity thus extracting the embeddings produced by the model.
We considered this model since it's multilingual with a large network, convenient 
for finetuning and capable of producing good result.
The main problem with the model is its substantial size which may lead to substantial
delays in it's running time.
'''

from transformers import RobertaModel, RobertaConfig, AutoTokenizer

config = RobertaConfig.from_pretrained("xlm-roberta-base")
model = RobertaModel.from_pretrained("xlm-roberta-base", config=config)
tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")   