# Baseline NER model koristeci Multinomial Naive Bayes

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report, f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score
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
    df = df[[1,10]]
    df.columns = ["token", "label"]
    df['label'] = df['label'].fillna('O')
    df = df.dropna(subset=['token'])
    df["label"] = df["label"].astype(str).str.strip()
    return df

# ------------------------------
# Ekstrakcija karakteristika po tokenu
# ------------------------------
def extract_features(tokens, index):
    token = tokens[index]
    features = {
        'token_lower': token.lower(),
        'is_capitalized': token[0].isupper(),
        'has_hyphen': '-' in token,
        'prefix_1': token[0].lower(),
        'suffix_1': token[-1].lower(),
        'position': index,
        'prev_token': tokens[index - 1].lower() if index > 0 else '<START>',
        'prev2_token': tokens[index - 2].lower() if index > 1 else '<START>',
        #'token_length': len(token),
        #'future_token': tokens[index + 1].lower() if index < len(tokens) - 1 else '<END>',
        #'future2_token': tokens[index + 2].lower() if index < len(tokens) - 2 else '<END>',
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
# Treniranje i evaluacija modela
# ------------------------------
def train_evaluate_ner(tokens, labels, test_size=0.2, cv=10):
    X = [extract_features(tokens, i) for i in range(len(tokens))]
    y = labels

    # Podela na trening i test skup
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)

    vec = DictVectorizer(sparse=True)
    X_train = vec.fit_transform(X_train_raw)
    X_test = vec.transform(X_test_raw)

    clf = MultinomialNB()

    # Cross-validation na trening skupu
    scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring='accuracy')
    print(f"{cv}-fold CV accuracy (train set):", scores)
    print("Prosečna tačnost (train set):", scores.mean())

    clf.fit(X_train, y_train)

    # Evaluacija na test skupu
    y_pred = clf.predict(X_test)
    print("\nClassification report (test set):")
    print(classification_report(y_test, y_pred, labels=[l for l in set(y_test) if l != 'O']))  # O opcionalno izbaciti
    macro_f1 = f1_score(y_test, y_pred, average='macro')
    print("Macro F1-score (test set):", macro_f1)

    return clf, vec, X_train, y_train, X_test, y_test

# ------------------------------
# Vizualizacija
# ------------------------------
def plot_confusion(y_true, y_pred):
    labels_unique = sorted(list(set(y_true)))
    cm = confusion_matrix(y_true, y_pred, labels=labels_unique)
    plt.figure(figsize=(10,7))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels_unique, yticklabels=labels_unique, cmap="Blues")
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix for MultinomialNB NER Model')
    plt.show()

# ------------------------------
# Predikcija novih tokena
# ------------------------------
def predict_tokens(clf, vec, tokens):
    X_new = [extract_features(tokens, i) for i in range(len(tokens))]
    X_new_vectorized = vec.transform(X_new)
    predictions = clf.predict(X_new_vectorized)
    for token, label in zip(tokens, predictions):
        print(f"{token} -> {label}")


if __name__ == "__main__":
    file_names = [
        "../tokenized_files/literature.xlsx",
        "../tokenized_files/administrative_texts.xlsx",
        "../tokenized_files/newspapers.xlsx",
        "../tokenized_files/twitter.xlsx"
    ]
    dfs = [read_and_clean_excel(f) for f in file_names]
    combined_df = pd.concat(dfs, ignore_index=True)
    #print(len(combined_df))
    # Splitovane label-e
    tokens = combined_df['token'].tolist()

    # -------------------
    # Splitovane label-e
    # -------------------
    labels_split = combined_df['label'].tolist()
    clf_split, vec_split, X_train_split, y_train_split, X_test_split, y_test_split = train_evaluate_ner(tokens,
                                                                                                        labels_split,
                                                                                                        cv=10)

    # Evaluacija na test skupu
    y_pred_split = clf_split.predict(X_test_split)
    plot_confusion(y_test_split, y_pred_split)
    predict_tokens(clf_split, vec_split, ["Beograd", "vlada", "Marko", "ETF"])

    # -------------------
    # Spojene label-e
    # -------------------
    labels_merged = combined_df['label'].apply(merge_labels).tolist()
    clf_merged, vec_merged, X_train_merged, y_train_merged, X_test_merged, y_test_merged = train_evaluate_ner(tokens,
                                                                                                              labels_merged,
                                                                                                              cv=10)

    # Evaluacija na test skupu
    y_pred_merged = clf_merged.predict(X_test_merged)
    plot_confusion(y_test_merged, y_pred_merged)
    predict_tokens(clf_merged, vec_merged, ["Beograd", "vlada", "Marko", "ETF"])
