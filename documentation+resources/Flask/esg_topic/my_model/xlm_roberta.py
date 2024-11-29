from transformers import RobertaModel, RobertaConfig, AutoTokenizer

config = RobertaConfig.from_pretrained("xlm-roberta-base")
model = RobertaModel.from_pretrained("xlm-roberta-base", config=config)
tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")   