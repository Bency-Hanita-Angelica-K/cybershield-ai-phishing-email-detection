import os
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


DATASET_PATH = "phishing_email.csv"
MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")


df = pd.read_csv(DATASET_PATH)

df = df[["Email Text", "Email Type"]]
df = df.dropna()

df["Email Type"] = df["Email Type"].str.strip().str.lower()
df["label"] = df["Email Type"].apply(lambda x: 1 if "phishing" in x else 0)

X = df["Email Text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_vectorized, y_train)

predictions = model.predict(X_test_vectorized)
accuracy = accuracy_score(y_test, predictions)

os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

print("Model trained successfully!")
print(f"Accuracy: {accuracy * 100:.2f}%")
print(classification_report(y_test, predictions))