import re
import base64
import joblib
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

model = joblib.load("model/model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

st.set_page_config(
    page_title="CyberShield AI | Phishing Email Detection",
    page_icon="🛡️",
    layout="wide"
)

PHISHING_SAMPLE = """Dear Customer,

Your account has been suspended due to suspicious activity.

Click here immediately to verify your login details:
https://secure-bank-verification.com

Failure to update your password within 24 hours will permanently block your account.

Regards,
Security Team
"""

LEGITIMATE_SAMPLE = """Hello Team,

This is a reminder that our project review meeting is scheduled for tomorrow at 10:00 AM.

Please bring your progress updates and completed task list.

Regards,
Project Coordinator
"""

SUSPICIOUS_WORDS = [
    "urgent", "verify", "password", "login", "bank", "account",
    "click", "limited time", "winner", "free", "update",
    "security alert", "suspended", "confirm", "blocked",
    "immediately", "restricted", "expired", "prize", "reward"
]

def count_urls(text):
    return len(re.findall(r"https?://\S+|www\.\S+", text))

def find_urls(text):
    return re.findall(r"https?://\S+|www\.\S+", text)

def count_email_addresses(text):
    return len(re.findall(r"[\w\.-]+@[\w\.-]+", text))

def find_suspicious_words(text):
    return [word for word in SUSPICIOUS_WORDS if word.lower() in text.lower()]

def get_risk_level(phishing_confidence):
    if phishing_confidence >= 80:
        return "High Risk", "🔴", "risk-high"
    elif phishing_confidence >= 50:
        return "Medium Risk", "🟠", "risk-medium"
    return "Low Risk", "🟢", "risk-low"

def create_reasons(phishing_confidence, urls, suspicious_words):
    reasons = []
    if phishing_confidence >= 80:
        reasons.append("High phishing probability detected by the machine learning model.")
    elif phishing_confidence >= 50:
        reasons.append("Moderate phishing probability detected by the machine learning model.")
    else:
        reasons.append("Low phishing probability detected by the machine learning model.")

    if urls:
        reasons.append("The email contains one or more links, which may lead to unsafe websites.")
    if suspicious_words:
        reasons.append("The email contains phishing-related keywords.")
    if len(suspicious_words) >= 5:
        reasons.append("Multiple suspicious keywords were found, increasing the risk level.")
    if "password" in [w.lower() for w in suspicious_words]:
        reasons.append("The email asks about password-related action.")
    if "verify" in [w.lower() for w in suspicious_words]:
        reasons.append("The email uses account verification language.")
    return reasons

def create_pdf_report(result, confidence, risk_level, word_count, url_count, email_count, suspicious_words, urls):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "CyberShield AI - Phishing Email Analysis Report")

    y -= 35
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Result")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Classification: {result}")
    y -= 18
    pdf.drawString(70, y, f"Confidence: {confidence:.2f}%")
    y -= 18
    pdf.drawString(70, y, f"Risk Level: {risk_level}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Email Summary")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Word Count: {word_count}")
    y -= 18
    pdf.drawString(70, y, f"URL Count: {url_count}")
    y -= 18
    pdf.drawString(70, y, f"Email Address Count: {email_count}")
    y -= 18
    pdf.drawString(70, y, f"Suspicious Keywords: {len(suspicious_words)}")

    y -= 35
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Suspicious Keywords")
    y -= 20
    pdf.setFont("Helvetica", 11)
    keywords = ", ".join(suspicious_words) if suspicious_words else "None"
    pdf.drawString(70, y, keywords[:90])

    y -= 35
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Detected URLs")
    y -= 20
    pdf.setFont("Helvetica", 10)
    if urls:
        for url in urls[:6]:
            pdf.drawString(70, y, url[:90])
            y -= 16
    else:
        pdf.drawString(70, y, "None")

    y -= 30
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, "Tech Stack")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, "Python, Streamlit, Scikit-learn, Pandas, TF-IDF, Logistic Regression")

    pdf.save()
    buffer.seek(0)
    return buffer

def cyber_logo_svg():
    svg = """
    <svg width="90" height="90" viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g" x1="0" x2="1">
          <stop offset="0%" stop-color="#38bdf8"/>
          <stop offset="100%" stop-color="#2563eb"/>
        </linearGradient>
      </defs>
      <path d="M45 6 L78 19 V40 C78 61 64 78 45 85 C26 78 12 61 12 40 V19 Z" fill="url(#g)" stroke="#e0f2fe" stroke-width="3"/>
      <path d="M45 18 V72" stroke="#e0f2fe" stroke-width="4" opacity="0.75"/>
      <path d="M29 44 L39 54 L62 31" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """
    return base64.b64encode(svg.encode()).decode()

if "history" not in st.session_state:
    st.session_state.history = []

if "email_text" not in st.session_state:
    st.session_state.email_text = ""

st.markdown("""
<style>
.block-container { padding-top: 1.5rem; }

.hero {
    padding: 30px;
    border-radius: 24px;
    background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #1e3a8a 100%);
    border: 1px solid #334155;
    margin-bottom: 26px;
}

.hero-flex {
    display: flex;
    align-items: center;
    gap: 24px;
}

.hero-title {
    color: white;
    font-size: 52px;
    font-weight: 900;
    margin: 0;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 20px;
    margin-top: 8px;
}

.badge {
    display: inline-block;
    padding: 10px 16px;
    border-radius: 999px;
    font-weight: 800;
    margin-top: 8px;
}

.risk-high { background-color: #7f1d1d; color: #fecaca; }
.risk-medium { background-color: #78350f; color: #fde68a; }
.risk-low { background-color: #064e3b; color: #bbf7d0; }

.reason-box {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 10px;
}

.footer {
    text-align: center;
    color: #94a3b8;
    padding: 24px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🛡️ CyberShield AI")
st.sidebar.write("Professional phishing email detection dashboard.")

st.sidebar.markdown("### Model Details")
st.sidebar.write("Algorithm: Logistic Regression")
st.sidebar.write("Feature Extraction: TF-IDF")
st.sidebar.write("Accuracy: 96%")
st.sidebar.write("Version: 2.0")

st.sidebar.markdown("### Quick Samples")
if st.sidebar.button("Load Phishing Sample"):
    st.session_state.email_text = PHISHING_SAMPLE
    st.rerun()

if st.sidebar.button("Load Legitimate Sample"):
    st.session_state.email_text = LEGITIMATE_SAMPLE
    st.rerun()

if st.sidebar.button("Clear Email"):
    st.session_state.email_text = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("Developer: Bency Hanita Angelica K")
st.sidebar.write("Project Type: Machine Learning + Cybersecurity")

logo = cyber_logo_svg()
st.markdown(f"""
<div class="hero">
  <div class="hero-flex">
    <img src="data:image/svg+xml;base64,{logo}" width="92"/>
    <div>
      <h1 class="hero-title">CyberShield AI</h1>
      <div class="hero-subtitle">
        Phishing Email Detection System using Machine Learning and Natural Language Processing
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

email_text = st.text_area(
    "Paste Email Content",
    value=st.session_state.email_text,
    height=260,
    placeholder="Paste the email content here..."
)
st.session_state.email_text = email_text

word_count = len(email_text.split())
url_count = count_urls(email_text)
email_count = count_email_addresses(email_text)
suspicious_found = find_suspicious_words(email_text)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Words", word_count)
c2.metric("URLs", url_count)
c3.metric("Email Addresses", email_count)
c4.metric("Suspicious Keywords", len(suspicious_found))

st.markdown("---")

if st.button("Analyze Email", type="primary", use_container_width=True):
    if email_text.strip() == "":
        st.warning("Please enter email content.")
    else:
        vectorized_text = vectorizer.transform([email_text])
        prediction = model.predict(vectorized_text)[0]
        probability = model.predict_proba(vectorized_text)[0]

        phishing_confidence = probability[1] * 100
        legitimate_confidence = probability[0] * 100

        urls = find_urls(email_text)
        suspicious_found = find_suspicious_words(email_text)

        result = "Phishing Email" if prediction == 1 else "Legitimate Email"
        confidence = phishing_confidence if prediction == 1 else legitimate_confidence
        risk_level, risk_icon, risk_class = get_risk_level(phishing_confidence)

        if prediction == 1:
            st.error(f"🚨 Result: {result}")
        else:
            st.success(f"✅ Result: {result}")

        r1, r2, r3 = st.columns([1.2, 1, 1])

        with r1:
            st.subheader("Confidence Score")
            st.progress(int(confidence))
            st.write(f"Model Confidence: **{confidence:.2f}%**")

        with r2:
            st.subheader("Risk Badge")
            st.markdown(
                f"<span class='badge {risk_class}'>{risk_icon} {risk_level}</span>",
                unsafe_allow_html=True
            )

        with r3:
            st.subheader("Probability")
            prob_df = pd.DataFrame({
                "Class": ["Phishing", "Legitimate"],
                "Probability": [phishing_confidence, legitimate_confidence]
            })
            chart = alt.Chart(prob_df).mark_arc(innerRadius=45).encode(
                theta="Probability",
                color="Class",
                tooltip=["Class", "Probability"]
            )
            st.altair_chart(chart, use_container_width=True)

        st.markdown("---")

        left, right = st.columns(2)

        with left:
            st.subheader("Why this result?")
            for reason in create_reasons(phishing_confidence, urls, suspicious_found):
                st.markdown(f"<div class='reason-box'>✅ {reason}</div>", unsafe_allow_html=True)

            st.subheader("Suspicious Keywords")
            if suspicious_found:
                st.write(", ".join(suspicious_found))
            else:
                st.write("No suspicious keywords found.")

        with right:
            st.subheader("Detected URLs")
            if urls:
                for url in urls:
                    st.write(f"🔗 {url}")
            else:
                st.write("No URLs detected.")

            st.subheader("Email Summary")
            summary_df = pd.DataFrame({
                "Metric": ["Words", "URLs", "Email Addresses", "Suspicious Keywords"],
                "Value": [word_count, url_count, email_count, len(suspicious_found)]
            })
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

        pdf_report = create_pdf_report(
            result, confidence, risk_level, word_count, url_count,
            email_count, suspicious_found, urls
        )

        st.download_button(
            label="📄 Download PDF Analysis Report",
            data=pdf_report,
            file_name="cybershield_ai_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.session_state.history.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Result": result,
            "Confidence": f"{confidence:.2f}%",
            "Risk": risk_level,
            "URLs": url_count,
            "Suspicious Words": len(suspicious_found)
        })

st.markdown("---")
st.subheader("📊 Analysis History")

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history[-5:])
    st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.info("No analysis performed yet.")

st.markdown("""
<div class="footer">
    Version 2.0 | Built by Bency | CyberShield AI | 2026
</div>
""", unsafe_allow_html=True)
