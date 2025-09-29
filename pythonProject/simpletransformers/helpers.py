import os
import pandas as pd
import os
import sklearn.metrics
import seqeval.metrics
from seqeval.scheme import IOB2
import seaborn as sns
import matplotlib.pyplot as plt


domain_names = ["administrative_texts", "newspapers","twitter", "literature"]
excel_columns = ["anotiran token", "token za predikciju", "predikcija", "konvertovana predikcija", "anotacija"]
annotations = [ "O", "I-PER", "B-PER", "I-ORG", "B-ORG", "I-LOC", "B-LOC"]

input_folder = "tokenized_files"

class Domain:

    model_name = ""
    evaluation_folder = ""
    predictions_folder = ""
    output_folder = ""
    all_domains_output_file_seqeval = ""
    all_domains_output_file_sklearn = ""
    
    annotations = []
    converted_predictions = []

    all_domains = []

    def __init__(self, name):
        self.name = name
        self.input_file = os.path.join(input_folder, name + ".conllu") 

        self.predictions_file =  os.path.join(Domain.predictions_folder, name + ".xlsx") 
        self.sklearn_file = os.path.join(Domain.output_folder, name  + "_sklearn.txt")
        self.seqeval_file = os.path.join(Domain.output_folder, name + "_seqeval.txt")

        self.tokens = []
        self.annotations = []
        self.prediction_tokens = []
        self.predictions = []
        self.converted_predictions = []
    

    @staticmethod
    def instanitate(model_name):
        Domain.model_name = model_name
        Domain.evaluation_folder = os.path.join("evaluation", Domain.model_name)
        os.makedirs(Domain.evaluation_folder, exist_ok=True)

        Domain.predictions_folder = os.path.join(Domain.evaluation_folder, "predictions") 
        Domain.output_folder = os.path.join(Domain.evaluation_folder, "output") 
        os.makedirs(Domain.predictions_folder, exist_ok=True)
        os.makedirs(Domain.output_folder, exist_ok=True)

        Domain.all_domains_output_file_seqeval = os.path.join(Domain.output_folder, "all_domains_seqeval.txt")
        Domain.all_domains_output_file_sklearn = os.path.join(Domain.output_folder, "all_domains_sklearn.txt")

        Domain.all_domains = [Domain(domain_name) for domain_name in domain_names]
        return Domain.all_domains


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
                    print(f"Napomena u domenu {self.name} na liniji {line_number}: Nedostaje anotacija.")
                    continue

                token = cols[1]
                annotation = cols[10]

                if annotation not in annotations:
                    print(f"Napomena u domenu {self.name} na liniji {line_number}: Koriscena nepostojeca anotacija: {token} = {annotation}")
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

        df = pd.DataFrame(rows, columns=excel_columns) 
        df.to_excel(self.predictions_file, header=True, index=False)
        print("Kreiran Excel fajl za " + self.name)


    @staticmethod
    def flatten(y_true, y_pred):
        #flatten
        y_true = [label for seq in y_true for label in seq]
        y_pred = [label for seq in y_pred for label in seq]
        #without I- and B-
        y_true_NE = [label[2:] if label != 'O' else 'O' for label in y_true]
        y_pred_NE = [label[2:] if label != 'O' else 'O' for label in y_pred]

        return y_true, y_pred, y_true_NE, y_pred_NE


    @staticmethod
    def evaluate_sklearn(y_true, y_pred):
        y_true, y_pred, y_true_NE, y_pred_NE = Domain.flatten(y_true, y_pred)
        result = ""
        report = sklearn.metrics.classification_report(y_true, y_pred)
        result += f"{report}\n\n"
        report = sklearn.metrics.classification_report(y_true_NE, y_pred_NE)
        result += f"{report}\n\n"
        return result
    
    
    @staticmethod
    def evaluate_seqeval(y_true, y_pred):
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
        result += Domain.evaluate_seqeval(y_true, y_pred)
        with open(seqeval_file, "w", encoding="utf-8") as f:
            f.write(result)

        #sklearn
        result = ""
        result += Domain.evaluate_sklearn(y_true, y_pred)
        with open(sklearn_file, "w", encoding="utf-8") as f:
            f.write(result)     

    
    def evaluate(self):
        Domain.evaluate_arrays(self.annotations, self.converted_predictions, self.seqeval_file, self.sklearn_file)
        print("Gotova evaluacija domena " + self.name)

    
    
    @staticmethod
    def evaluate_all():
        y_true = [
            seq 
            for domain in Domain.all_domains 
            for seq in domain.annotations
        ]
        y_pred = [
            seq 
            for domain in Domain.all_domains 
            for seq in domain.converted_predictions
        ]

        Domain.evaluate_arrays(y_true, y_pred, Domain.all_domains_output_file_seqeval, Domain.all_domains_output_file_sklearn)
        print("Svi domeni evaluirani.")

        # draw confusion matrix
        y_true, y_pred, y_true_NE, y_pred_NE = Domain.flatten(y_true, y_pred)
        all_annnotations = ["O", "PER", "ORG", "LOC"]
        cm = sklearn.metrics.confusion_matrix(y_true_NE, y_pred_NE, labels=all_annnotations)
        plt.figure(figsize=(10,7))
        sns.heatmap(cm, annot=True, fmt='d', xticklabels=all_annnotations, yticklabels=all_annnotations, cmap="Blues")
        plt.ylabel('Expected')
        plt.xlabel('Predicted')
        plt.title(f'Confusion Matrix for {Domain.model_name}')
        plt.show()


    @staticmethod
    def read_from_predictions_no_IB():
        annotations = []
        predictions = []
        for domain in Domain.all_domains:
            df = pd.read_excel(domain.predictions_file)
            annotations.extend([label[2:] if label != 'O' else 'O' for label in df[df.columns[4]].tolist()])
            predictions.extend([label[2:] if label != 'O' else 'O' for  label in df[df.columns[3]].tolist()])
        return annotations, predictions


        
        


