import os
import pandas as pd
import os
import sklearn.metrics
import seqeval.metrics
from seqeval.scheme import IOB2


domain_names = ["administrative_texts", "newspapers","twitter", "literature"]

this_folder = "simpletransformers"
input_folder = "tokenized_files"
predictions_folder = "predictions"
output_folder = "output"

annotations = [ "O", "I-PER", "B-PER", "I-ORG", "B-ORG", "I-LOC", "B-LOC"]

class Domain:
    def __init__(self, name, model_name):
        self.name = name
        self.input_file = os.path.join(input_folder, name + ".conllu") 
        
        model_folder = os.path.join(this_folder, model_name)
        os.makedirs(model_folder, exist_ok=True)

        self.predictions_folder = os.path.join(model_folder, predictions_folder) 
        self.output_folder = os.path.join(model_folder, output_folder) 
        
        os.makedirs(self.predictions_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

        self.predictions_file =  os.path.join(self.predictions_folder, name + ".xlsx") 
        self.sklearn_file = os.path.join(self.output_folder, name  + "_sklearn.txt")
        self.seqeval_file = os.path.join(self.output_folder, name + "_seqeval.txt")

        self.tokens = []
        self.annotations = []
        self.prediction_tokens = []
        self.predictions = []
        self.converted_predictions = []
    

    @staticmethod
    def instancijraj(model_name):
        return [Domain(domain_name, model_name) for domain_name in domain_names]


    def load_data(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            sentence_tokens = []
            sentence_annotations = []
            for line_number, line in enumerate(f, start=1):
                line = line.strip() 
                if line.startswith("# text") and sentence_tokens:
                    self.tokens.append(sentence_tokens)
                    self.annotations.append(sentence_annotations)
                    sentence_tokens = []
                    sentence_annotations = []
                    continue
                if not line or line.startswith("#"):
                    continue
                cols = line.split("\t")
                
                if len(cols) < 11:
                    print(f"Greska u domenu {self.name} na liniji {line_number}: Nedostaje anotacija.")
                    continue

                token = cols[1]
                annotation = cols[10]

                if annotation not in annotations:
                    print(f"Greska u domenu {self.name} na liniji {line_number}. Koriscena nepostojeca anotacija: {token} = {annotation}")
                    continue
                
                sentence_tokens.append(token)
                sentence_annotations.append(annotation)
            if sentence_tokens:
                self.tokens.append(sentence_tokens)
                self.annotations.append(sentence_annotations)
            
        print("Ucitani podaci za " + self.name)


    def write_predictions(self):
        if os.path.exists(self.predictions_file):
            os.remove(self.predictions_file)

        rows = [
            row 
            for t, pt, p, cp, a in zip(self.tokens, self.prediction_tokens, self.predictions, self.converted_predictions, self.annotations)
            for row in zip(t, pt, p, cp, a)
        ]

        df = pd.DataFrame(rows, columns=["anotiran token", "token za predikciju", "predikcija", "konvertovana predikcija", "anotacija"]) 
        df.to_excel(self.predictions_file, header=True, index=False)
        print("Kreiran Excel fajl za " + self.name)


    @staticmethod
    def evaluate_arrays_sklearn(y_true, y_pred):
        #flatten
        y_true = [label for seq in y_true for label in seq]
        y_pred = [label for seq in y_pred for label in seq]
        #without I- and B-
        y_true_NE = [label[2:] if label != 'O' else 'O' for label in y_true]
        y_pred_NE = [label[2:] if label != 'O' else 'O' for label in y_pred]

        result = ""
        report = sklearn.metrics.classification_report(y_true, y_pred)
        result += f"{report}\n\n"
        report = sklearn.metrics.classification_report(y_true_NE, y_pred_NE)
        result += f"{report}\n\n"
        return result
    
    
    @staticmethod
    def evaluate_arrays_seqeval(y_true, y_pred):
        result = ""
        report = seqeval.metrics.classification_report(y_true, y_pred, mode="strict", scheme=IOB2)
        result += f"STRICT\n{report}\n\n"

        report = seqeval.metrics.classification_report(y_true, y_pred)
        result += f"DEFAULT\n{report}\n\n"
        
        accuracy = seqeval.metrics.accuracy_score(y_true, y_pred)
        f1 = seqeval.metrics.f1_score(y_true, y_pred)
        precision = seqeval.metrics.precision_score(y_true, y_pred)
        recall = seqeval.metrics.recall_score(y_true, y_pred)
        result += f"Accuracy: {accuracy:.2f}\n"
        result += f"F1: {f1:.2f}\n"
        result += f"Precision: {precision:.2f}\n"
        result += f"Recall: {recall:.2f}\n"
        
        return result
        
    
    
    @staticmethod
    def evaluate_arrays(y_true, y_pred, seqeval_file, sklearn_file):
        #seqeval
        result = ""
        result += Domain.evaluate_arrays_seqeval(y_true, y_pred)
        with open(seqeval_file, "w", encoding="utf-8") as f:
            f.write(result)

        #sklearn
        result = ""
        result += Domain.evaluate_arrays_sklearn(y_true, y_pred)
        with open(sklearn_file, "w", encoding="utf-8") as f:
            f.write(result) 


    def evaluate(self):
        Domain.evaluate_arrays(self.annotations, self.converted_predictions, self.seqeval_file, self.sklearn_file)    
        print("Gotova evaluacija domena " + self.name)

    
    
    @staticmethod
    def evaluate_all(domains):
        annotations = []
        converted_predictions = []
        for domain in domains:
            annotations.extend(domain.annotations)
            converted_predictions.extend(domain.converted_predictions)

        Domain.evaluate_arrays(annotations, converted_predictions, os.path.join(domains[0].output_folder, "all_domains_seqeval.txt"),os.path.join(domains[0].output_folder, "all_domains_sklearn.txt") )
        print("All domains evaluated.")






