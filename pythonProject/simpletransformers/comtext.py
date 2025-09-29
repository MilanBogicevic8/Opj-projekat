from simpletransformers.ner import NERModel
from helpers import *



switch = {
    "I-ADR" : "I-LOC",
    "B-ADR" : "B-LOC",
    "I-TOP" : "I-LOC",
    "B-TOP" : "B-LOC",
    "I-COURT" : "I-ORG",
    "B-COURT" : "B-ORG",
    "I-INST" : "I-ORG",
    "B-INST" : "B-ORG",
    "I-COM" : "I-ORG",
    "B-COM" : "B-ORG",
    "I-ORGOTH" : "I-ORG",
    "B-ORGOTH" : "B-ORG",
    "I-PER" : "I-PER",
    "B-PER" : "B-PER",
}


def predict(model, domain):
    preds_list, model_output = model.predict(domain.tokens, split_on_space=False)

    for pred in preds_list:
        domain.prediction_tokens.append([list(word.keys())[0] for word in pred])
        p = [list(word.values())[0] for word in pred]
        domain.predictions.append(p)
        p = [switch.get(word, "O") for word in p] #!
        domain.converted_predictions.append(p)

    print("Gotova predikcija za " + domain.name)


if __name__ == "__main__":
    labels = ["B-COM", "I-COM", "B-ADR", "I-ADR", "O", "B-REF", "B-LAW", "I-LAW", "B-PER","I-PER", "B-TOP", "I-TOP", "I-REF", "B-MONEY", "I-MONEY", "B-DATE", "I-DATE", "B-INST", "I-INST", "B-IDCOM", "B-IDOTH", "B-NUMDOC", "B-MISC", "I-MISC", "B-CONTACT", "B-IDPER", "B-NUMPLOT", "B-IDTAX", "B-COURT", "I-COURT", "B-NUMCAR", "B-ORGOTH", "I-ORGOTH", "I-NUMCAR", "B-NUMACC"]
    model = NERModel( 
        'electra',  
        'ICEF-NLP/bcms-bertic-comtext-sr-legal-ner-ekavica', 
        use_cuda=False, 
        ignore_mismatched_sizes=True, 
        labels=labels,
        args = {
                "train_batch_size": 4,
                "eval_batch_size": 4,
                "use_multiprocessing": False,
                "max_seq_length": 512
        }
    )

    domains = Domain.instanitate("comtext")
    for domain in domains:
        domain.load_data()
        predict(model, domain)
        domain.write_predictions()
        domain.evaluate()
    Domain.evaluate_all()





