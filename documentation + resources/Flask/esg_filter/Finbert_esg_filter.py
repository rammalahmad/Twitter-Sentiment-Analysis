from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from deep_translator import GoogleTranslator


finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-esg',num_labels=4)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-esg')
nlp = pipeline("text-classification", model=finbert, tokenizer=tokenizer)

def finbert_english(text:str) -> str:
    if nlp(text)[0]['label']=="Environmental":
        return 0
    if nlp(text)[0]['label']=="Social":
        return 1
    if nlp(text)[0]['label']=="Governance":
        return 2
    return -1



def finbert_esg(text:str, lang:str) -> str:
    if lang=="en":
        return finbert_english(text)
    else:
        text_en = GoogleTranslator(source=lang, target="en").translate(text)
        return finbert_english(text_en)
