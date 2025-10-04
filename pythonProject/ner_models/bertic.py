from simpletransformers.ner import NERModel
from helpers import Domain


switch = {
    "I-MISC" : "O",
    "B-MISC" : "O",
}


def predict(model, tokens):
    prediction_tokens = []
    predictions = []
    converted_predictions = []
    preds_list, model_output = model.predict(tokens, split_on_space=False)

    for pred in preds_list:
        prediction_tokens.append([list(word.keys())[0] for word in pred])
        p = [list(word.values())[0] for word in pred]
        predictions.append(p)
        p = [switch.get(word, word) for word in p]  #!
        converted_predictions.append(p)
    return prediction_tokens, predictions, converted_predictions


if __name__ == "__main__":
    labels = ['B-LOC','B-MISC','B-ORG','B-PER','I-LOC','I-MISC','I-ORG','I-PER','O']
    model = NERModel( 
        'electra',  
        'classla/bcms-bertic-ner', 
        use_cuda=False, 
        ignore_mismatched_sizes=True, 
        labels=labels,
        args = {
                "train_batch_size": 16,
                "eval_batch_size": 16,
                "use_multiprocessing": False,
                "max_seq_length": 512
        }
    )

    domains = Domain.run("bertic", predict, model)
    






