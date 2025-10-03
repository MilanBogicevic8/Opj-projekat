from simpletransformers.ner import NERModel
from helpers import Domain


switch = {
    "I-MISC" : "O",
    "B-MISC" : "O",
    "I-DERIV-PER" : "I-PER",
    "B-DERIV-PER" : "B-PER",
}


def predict(model, domain):
    preds_list, model_output = model.predict(domain.tokens, split_on_space=False)

    for pred in preds_list:
        domain.prediction_tokens.append([list(word.keys())[0] for word in pred])
        p = [list(word.values())[0] for word in pred]
        domain.predictions.append(p)
        p = [switch.get(word, word) for word in p]  #!
        domain.converted_predictions.append(p) 
    
    print("Gotova predikcija za " + domain.name)


if __name__ == "__main__":
    labels = ['B-LOC','B-MISC','B-ORG','B-PER','I-LOC','I-MISC','I-ORG','I-PER','O']
    model = NERModel( 
        'electra',  
        'classla/bcms-bertic-ner', 
        use_cuda=False, 
        ignore_mismatched_sizes=True, 
        labels=labels,
        args = {
                "train_batch_size": 8,
                "eval_batch_size": 8,
                "use_multiprocessing": False,
                "max_seq_length": 512
        }
    )

    domains = Domain.instanitate("bertic")
    for domain in domains:
        domain.load_data()
        predict(model, domain)
        domain.write_predictions()
        domain.evaluate()
    Domain.evaluate_all()
    






