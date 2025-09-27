# Baseline NER model koristeci Multinomial Naive Bayes

import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix

def read_and_populate_csv_files(file_name):
    df = pd.read_excel(file_name, header=None)
    df = df[df[0].astype(str).str.isnumeric()] #samo redovi sa recima
    df.reset_index(inplace=True)
    df = df[[1,10]]# prva i 10 kolona
    df.columns = ["token", "label"]
    df['label'] = df['label'].fillna('O')
    df = df.dropna(subset=['token'])
    return df

# ------------------------------
# Ekstrakcija karakteristika po tokenu
# ------------------------------
def extract_features(tokens, index):
    token = tokens[index]
    features = {
        'token_lower': token.lower(),
        'is_capitalized': token[0].isupper(),
        'position': index
    }
    # prethodna dva tokena
    features['prev_token'] = tokens[index - 1].lower() if index > 0 else '<START>'
    features['prev2_token'] = tokens[index - 2].lower() if index > 1 else '<START>'
    return features

if __name__ == "__main__":
    file_names = [
        "../tokenized_files/literature.xlsx",
        "../tokenized_files/administrative_texts.xlsx",
        "../tokenized_files/newspapers.xlsx",
        "../tokenized_files/twitter.xlsx"
    ]
    dfs = [read_and_populate_csv_files(f) for f in file_names]
    combined_df = pd.concat(dfs, ignore_index=True)

    print(combined_df.head())
    print(f"Ukupno redova: {len(combined_df)}")

    tokens = combined_df['token'].tolist()
    labels = combined_df['label'].tolist()
    X = [extract_features(tokens, i) for i in range(len(tokens))]
    y = labels

    vec = DictVectorizer(sparse=True)
    X_vectorized = vec.fit_transform(X)

    clf = MultinomialNB()
    scores = cross_val_score(clf, X_vectorized, y, cv=5, scoring='accuracy')
    print("5-fold CV accuracy za baseline NER model:", scores)
    print("Prosečna tačnost:", scores.mean())

    # --- Predikcija za novi podatak ---
    novi_tokeni = ["Beograd", "vlada", "Marko", "BGD"]
    novi_X_features = [extract_features(novi_tokeni, i) for i in range(len(novi_tokeni))]
    novi_X_vectorized = vec.transform(novi_X_features)
    clf.fit(X_vectorized, y)
    predikcije = clf.predict(novi_X_vectorized)

    for token, label in zip(novi_tokeni, predikcije):
        print(f"{token} -> {label}")

    # ------------------------------
    # Vizualizacija: matrica konfuzije i top feature-ovi
    # ------------------------------
    y_pred = clf.predict(X_vectorized)
    labels_unique = sorted(list(set(y)))
    cm = confusion_matrix(y, y_pred, labels=labels_unique)

    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels_unique, yticklabels=labels_unique, cmap="Blues")
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix for MultinomialNB NER Model')
    plt.show()

    # Top 10 feature-ova po klasi
    feature_names = vec.get_feature_names_out()
    for i, class_label in enumerate(clf.classes_):
        top10_idx = np.argsort(clf.feature_log_prob_[i])[-10:]
        top_features = feature_names[top10_idx]
        print(f"Top features for class {class_label}: {top_features}")
