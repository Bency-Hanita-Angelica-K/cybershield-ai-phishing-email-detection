# 🛡️ CyberShield AI - Phishing Email Detection System

CyberShield AI is a professional machine learning web application that detects whether an email is **phishing** or **legitimate** using Natural Language Processing.

## 🚀 Features

- Phishing and legitimate email classification
- Confidence score
- Risk badge: Low, Medium, High
- Probability chart
- URL detection
- Suspicious keyword detection
- Email summary dashboard
- Explanation of classification result
- PDF analysis report download
- Analysis history
- Sample phishing and legitimate emails

## 🛠️ Tech Stack

- Python
- Streamlit
- Scikit-learn
- Pandas
- Altair
- ReportLab
- TF-IDF Vectorizer
- Logistic Regression
- Joblib

## 📂 Project Structure

```text
phishing-email-detection/
│
├── app.py
├── train_model.py
├── phishing_email.csv
├── requirements.txt
├── README.md
├── .gitignore
│
└── model/
    ├── model.pkl
    └── vectorizer.pkl
```

## ⚙️ How to Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

## 📊 Machine Learning Model

- Text Processing: TF-IDF Vectorizer
- Algorithm: Logistic Regression
- Accuracy: Around 96%

## 📌 Resume Description

**CyberShield AI – Phishing Email Detection System**  
Built a machine learning web application to classify emails as phishing or legitimate using TF-IDF and Logistic Regression. The system provides confidence score, risk level, suspicious keyword detection, URL detection, analysis history, and downloadable PDF reports.

## 👩‍💻 Developer

**Bency Hanita Angelica K**
