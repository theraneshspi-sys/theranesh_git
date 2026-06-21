import numpy as np
from scipy.sparse import hstack, csr_matrix

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dataset import build_dataset
from features import extract_feature_matrix, FEATURE_NAMES

STRUCT_FEATURE_WEIGHT = 4.0


def build_pipeline_inputs(texts, vectorizer, fit=False):
    if fit:
        tfidf = vectorizer.fit_transform(texts)
    else:
        tfidf = vectorizer.transform(texts)

    struct = extract_feature_matrix(texts)
    col_max = struct.max(axis=0)
    col_max[col_max == 0] = 1.0
    struct_scaled = (struct / col_max) * STRUCT_FEATURE_WEIGHT

    combined = hstack([tfidf, csr_matrix(struct_scaled)])
    return combined, col_max


def main():
    print("Building dataset...")
    texts, labels = build_dataset(n_per_class=400)
    labels = np.array(labels)

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    print(f"Train size: {len(X_train_text)}  Test size: {len(X_test_text)}")

    vectorizer = TfidfVectorizer(
        lowercase=True, stop_words="english", ngram_range=(1, 2),
        max_features=2000, min_df=2,
    )

    X_train, col_max = build_pipeline_inputs(X_train_text, vectorizer, fit=True)

    struct_test = extract_feature_matrix(X_test_text)
    struct_test_scaled = (struct_test / col_max) * STRUCT_FEATURE_WEIGHT
    tfidf_test = vectorizer.transform(X_test_text)
    X_test = hstack([tfidf_test, csr_matrix(struct_test_scaled)])

    print("Training LogisticRegression...")
    clf = LogisticRegression(
        max_iter=2000, C=1.0, class_weight="balanced", random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}\n")
    print("Classification report:")
    print(classification_report(y_test, y_pred, target_names=["Safe", "Phishing"]))

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion matrix (rows=true, cols=predicted):")
    print("              Pred Safe  Pred Phishing")
    print(f"True Safe        {cm[0][0]:>5}        {cm[0][1]:>5}")
    print(f"True Phishing    {cm[1][0]:>5}        {cm[1][1]:>5}")

    plot_confusion_matrix(cm, ["Safe", "Phishing"], "confusion_matrix.png")
    print("\nSaved confusion_matrix.png")

    n_struct = len(FEATURE_NAMES)
    struct_coefs = clf.coef_[0][-n_struct:]
    print("\nStructural feature coefficients:")
    for name, score in sorted(zip(FEATURE_NAMES, struct_coefs),
                               key=lambda x: -x[1]):
        print(f"  {name:<22} {score:+.4f}")

    demo_examples(clf, vectorizer, col_max)


def plot_confusion_matrix(cm, class_names, out_path):
    fig, ax = plt.subplots(figsize=(4.5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title("Confusion Matrix")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def demo_examples(clf, vectorizer, col_max):
    print("\n--- Example predictions on new, unseen emails ---")
    examples = [
        ("Subject: Account Suspension Warning\n\nDear Customer, your account "
         "will be suspended within 24 hours! Click here to verify now: "
         "http://paypa1-secure.com/login", "Phishing"),
        ("Subject: Team lunch Friday\n\nHi everyone, let's grab lunch Friday "
         "at noon to celebrate the launch. Let me know if you can make it.",
         "Safe"),
        ("Subject: Congratulations! You've won a gift card\n\nClaim your free "
         "prize now before it expires! Visit http://192.168.0.14/claim",
         "Phishing"),
        ("Subject: Invoice #4521 attached\n\nHi Maria, attached is the invoice "
         "for last month's consulting hours. Let me know if anything looks off.",
         "Safe"),
    ]
    texts = [e[0] for e in examples]
    truth = [e[1] for e in examples]

    tfidf = vectorizer.transform(texts)
    struct = extract_feature_matrix(texts) / col_max * STRUCT_FEATURE_WEIGHT
    X = hstack([tfidf, csr_matrix(struct)])
    preds = clf.predict(X)
    probs = clf.predict_proba(X)

    for text, true_label, pred, prob in zip(texts, truth, preds, probs):
        pred_label = "Phishing" if pred == 1 else "Safe"
        confidence = prob[pred]
        subject = text.split("\n")[0].replace("Subject: ", "")
        print(f"  [{pred_label:8}] (true: {true_label:8}, conf: {confidence:.2f}) "
              f"{subject}")


if __name__ == "__main__":
    main()
