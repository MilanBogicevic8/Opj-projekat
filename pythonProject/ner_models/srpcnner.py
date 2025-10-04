import spacy
from spacy.tokens import Doc
from helpers import *


MODEL_FOLDER = "."

switch = {
    "I-PERS" : "I-PER",
    "B-PERS" : "B-PER",
    "I-LOC" : "I-LOC",
    "B-LOC" : "B-LOC",
    "I-ORG" : "I-ORG",
    "B-ORG" : "B-ORG",
}


def predict(nlp, tokens):
    prediction_tokens = []
    predictions = []
    converted_predictions = []

    for t in tokens:
        # tokens = [token if token != "" else "NA" for token in tokens] # rec "NA"
        #skip tokenization
        doc = Doc(nlp.vocab, words=t) # spaces dont make a difference
        # nlp.pipeline
        doc = nlp.get_pipe("tok2vec")(doc)
        doc = nlp.get_pipe("ner")(doc)

        prediction_tokens.append([token.text for token in doc])
        p = [(token.ent_iob_ + "-" + token.ent_type_) if token.ent_type_ != "O" else "O" for token in doc]
        predictions.append(p)
        p = [switch.get(word, "O") for word in p] #!
        converted_predictions.append(p)

    return prediction_tokens, predictions, converted_predictions




if __name__ == "__main__":
    """
    preuzeti model sa linka
    https://live.european-language-grid.eu/catalogue/ld/9484/download/
    raspakovati i podesiti MODEL_FOLDER
    """
    nlp = spacy.load(os.path.join(MODEL_FOLDER, "SrpCNNER"))
    
    domains = Domain.run("srpcnner", predict, nlp)



