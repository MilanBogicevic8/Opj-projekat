import spacy
from spacy.tokens import Doc
from helpers import *


MODEL_FOLDER = "ner_models"

switch = {
    "I-PERS" : "I-PER",
    "B-PERS" : "B-PER",
    "I-LOC" : "I-LOC",
    "B-LOC" : "B-LOC",
    "I-ORG" : "I-ORG",
    "B-ORG" : "B-ORG",
}


def predict(nlp, domain):
    # doc = nlp("Milica studira na Elektrotehnickom fakultetu u Beogradu.")

    for tokens in domain.tokens:
        #preskoci tokenizaciju
        doc = Doc(nlp.vocab, words=tokens)
        doc = nlp.get_pipe("tok2vec")(doc)
        doc = nlp.get_pipe("ner")(doc)

        domain.prediction_tokens.append([token.text for token in doc])
        p = [(token.ent_iob_ + "-" + token.ent_type_) if token.ent_type_ != "O" else "O" for token in doc]
        domain.predictions.append(p)
        p = [switch.get(word, "O") for word in p] #!
        domain.converted_predictions.append(p)

    print("Gotova predikcija za " + domain.name)




if __name__ == "__main__":
    """
    skinuti model sa linka
    https://live.european-language-grid.eu/catalogue/ld/9484/download/
    raspakovati i podesiti MODEL_FOLDER
    """
    nlp = spacy.load(os.path.join(MODEL_FOLDER, "SrpCNNER"))
    
    domains = Domain.instanitate("srpcnner")
    for domain in domains:
        domain.load_data()
        predict(nlp, domain)
        domain.write_predictions()
        domain.evaluate()
    Domain.evaluate_all()


