# Baseline NER model koristeci Multinomial Naive Bayes
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


# ------------------------------
# Učitavanje i čišćenje fajla
# ------------------------------
def read_and_clean_excel(file_name):
    df = pd.read_excel(file_name, header=None)
    df = df[df[0].astype(str).str.isnumeric()]
    df.reset_index(drop=True, inplace=True)
    df = df[[1, 10]]
    df.columns = ["token", "label"]
    df['label'] = df['label'].fillna('O')
    df = df.dropna(subset=['token'])
    df["label"] = df["label"].astype(str).str.strip()
    return df


# ------------------------------
# Ekstrakcija karakteristika
# ------------------------------
def extract_features(tokens, index):
    punctuation_marks = {'.', '?', '!', ';', ':'}

    sentence_start = 0
    for i in range(index - 1, -1, -1):
        if tokens[i] in punctuation_marks:
            sentence_start = i + 1
            break

    position_in_sentence = index - sentence_start

    token = tokens[index]
    features = {
        'token_lower': token.lower(),
        'is_capitalized': token[0].isupper(),
        'is_capitalized_prev_token': tokens[index - 1][0].isupper() if index > 0 else False,
        'is_capitalized_prev2_token': tokens[index - 2][0].isupper() if index > 1 else False,
        'has_hyphen': '-' in token,
        'prefix_1': token[0].lower(),
        'suffix_1': token[-1].lower(),
        'position': position_in_sentence,
        'prev_token': tokens[index - 1].lower() if index > 0 else '<START>',
        'prev2_token': tokens[index - 2].lower() if index > 1 else '<START>',
    }

    return features

# ------------------------------
# Transformacija labela
# ------------------------------
def merge_labels(label):
    """Spaja B-/I- u jednu kategoriju, npr. B-LOC/I-LOC -> LOC"""
    label = label.strip()
    if label.startswith('B-') or label.startswith('I-'):
        return label[2:]
    return label


# ------------------------------
# Custom cross-validation sa kombinovanom konfuzionom matricom
# ------------------------------
def cross_validate_ner(tokens, labels, cv=5, plot_conf_matrix=True):
    X = [extract_features(tokens, i) for i in range(len(tokens))]
    y = labels

    vec = DictVectorizer(sparse=True)
    X_vectorized = vec.fit_transform(X)

    kf = KFold(n_splits=cv, shuffle=True, random_state=42)

    all_f1 = []
    all_acc = []

    y_true_all = []
    y_pred_all = []

    for fold, (train_idx, test_idx) in enumerate(kf.split(X_vectorized), start=1):
        print(f"\n===== Fold {fold}/{cv} =====")

        X_train, X_test = X_vectorized[train_idx], X_vectorized[test_idx]
        y_train, y_test = [y[i] for i in train_idx], [y[i] for i in test_idx]

        clf = MultinomialNB()
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)

        # Čuvanje svih predikcija za kombinovanu matricu
        y_true_all.extend(y_test)
        y_pred_all.extend(y_pred)

        acc = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average='macro')

        all_acc.append(acc)
        all_f1.append(macro_f1)

        print("Accuracy:", acc)
        print("Macro F1:", macro_f1)
        print("Classification report:")
        print(classification_report(y_test, y_pred, labels=[l for l in set(y_test)]))

    print("\n===== Finalni rezultati =====")
    print("Prosečna tačnost:", sum(all_acc) / cv)
    print("Prosečan macro F1:", sum(all_f1) / cv)

    # ------------------------------
    # Kombinovana konfuziona matrica
    # ------------------------------
    if plot_conf_matrix:
        unique_labels = sorted(set(y_true_all))
        cm = confusion_matrix(y_true_all, y_pred_all, labels=unique_labels)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=unique_labels,
                    yticklabels=unique_labels)
        plt.title("Kombinovana konfuziona matrica (svi fold-ovi)")
        plt.xlabel("Predicted label")
        plt.ylabel("True label")
        plt.tight_layout()
        plt.show()


# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    file_names = [
        "../tokenized_files/literature.xlsx",
        "../tokenized_files/administrative_texts.xlsx",
        "../tokenized_files/newspapers.xlsx",
        "../tokenized_files/twitter.xlsx"
    ]

    dfs = [read_and_clean_excel(f) for f in file_names]
    combined_df = pd.concat(dfs, ignore_index=True)

    tokens = combined_df['token'].tolist()

    # Splitovane label-e
    labels_split = combined_df['label'].tolist()
    cross_validate_ner(tokens, labels_split, cv=10, plot_conf_matrix=True)

    # Spojene label-e
    labels_merged = combined_df['label'].apply(merge_labels).tolist()
    cross_validate_ner(tokens, labels_merged, cv=10, plot_conf_matrix=True)
