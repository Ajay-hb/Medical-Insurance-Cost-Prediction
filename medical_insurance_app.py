import streamlit as st
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import tempfile
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Insurance AI Dashboard", layout="wide")

model = joblib.load("model.pkl")

# Background for SHAP
background = pd.DataFrame({
    "age":[30,40,50],
    "bmi":[20,25,30],
    "children":[0,1,2],
    "smoker":[0,1,0],
    "sex":[0,1,0]
})

# ---------------- PREMIUM CSS ----------------
st.markdown("""
<style>

/* HEADER */
.header {
    text-align:center;
    font-size:40px;
    font-weight:bold;
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation: glow 2s infinite alternate;
}
@keyframes glow {
    from {text-shadow:0 0 10px #00c6ff;}
    to {text-shadow:0 0 25px #0072ff;}
}

/* CARD */
.card {
    background: linear-gradient(135deg,#1f4037,#2c5364);
    padding:20px;
    border-radius:15px;
    color:white;
    margin-bottom:15px;
    transition:0.4s;
}
.card:hover {
    transform: translateY(-8px);
    box-shadow:0 0 25px rgba(0,200,255,0.6);
}

/* FADE */
.fade {
    animation: fadeIn 0.8s ease-in;
}
@keyframes fadeIn {
    from {opacity:0; transform:translateY(10px);}
    to {opacity:1;}
}

/* SUGGESTION */
.suggest {
    padding:12px;
    border-radius:8px;
    margin-bottom:10px;
    background: rgba(255,77,79,0.1);
    border-left:5px solid #ff4d4f;
}
.good {
    background: rgba(82,196,26,0.1);
    border-left:5px solid #52c41a;
}

/* SHAP BOX */
.shap-box {
    background:#111;
    padding:15px;
    border-radius:12px;
    margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="header">🧠 Insurance AI Dashboard</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Explainable AI • Insights • Optimization</p>", unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.subheader("📊 Enter Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 18, 65, 30)
    bmi = st.number_input("BMI", 10.0, 50.0, 25.0)

with col2:
    children = st.number_input("Children", 0, 5, 1)
    smoker = st.selectbox("Smoker", ["Yes", "No"])

with col3:
    sex = st.selectbox("Gender", ["Male", "Female"])

if st.button("🚀 Predict"):

    with st.spinner("Running AI analysis..."):
        time.sleep(1)

    smoker_val = 1 if smoker == "Yes" else 0
    sex_val = 1 if sex == "Male" else 0

    X = pd.DataFrame({
        "age":[age],
        "bmi":[bmi],
        "children":[children],
        "smoker":[smoker_val],
        "sex":[sex_val]
    })

    prediction = model.predict(X)[0]

    # ---------------- PROFILE ----------------
    st.markdown("### 📋 Customer Profile")
    st.markdown(f"""
    <div class="card fade">
    👤 Age: {age} | ⚖️ BMI: {bmi} | 👨‍👩‍👧 Children: {children} | 🚬 Smoker: {smoker} | 🧑 Gender: {sex}
    </div>
    """, unsafe_allow_html=True)

    # ---------------- COST ----------------
    st.markdown(f"""
    <div class="card fade">
    💰 Estimated Cost: <h2>₹{prediction:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- SHAP ----------------
    st.markdown("### 🧠 Why is the cost high?")

    try:
        explainer = shap.TreeExplainer(model)
    except:
        explainer = shap.KernelExplainer(model.predict, background)

    shap_values = explainer(X)

    st.markdown('<div class="shap-box fade">', unsafe_allow_html=True)

    fig, ax = plt.subplots()
    shap.plots.bar(shap_values[0], show=False)
    st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TEXT EXPLANATION ----------------
    st.markdown("### 🔍 Key Drivers")

    contributions = dict(zip(X.columns, shap_values.values[0]))
    sorted_features = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)

    explanations = []

    for f, v in sorted_features:
        if v > 0:
            text = f"{f} is increasing cost"
        else:
            text = f"{f} is reducing cost"
        explanations.append(text)
        st.write("•", text)

    # ---------------- SUGGESTIONS ----------------
    st.markdown("### 🧠 Suggestions")

    suggestions = []

    if smoker == "Yes":
        suggestions.append("Quit smoking to reduce cost")
    if bmi > 25:
        suggestions.append("Reduce BMI")
    if age > 50:
        suggestions.append("Regular health checkups")

    if suggestions:
        for s in suggestions:
            st.markdown(f'<div class="suggest fade">{s}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="suggest good fade">No suggestions required</div>', unsafe_allow_html=True)

    # ---------------- PDF ----------------
    st.markdown("### 📄 Download Report")

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Insurance AI Report", styles['Title']))
    content.append(Spacer(1,10))

    content.append(Paragraph("Customer Profile", styles['Heading2']))
    content.append(Paragraph(str(X.to_dict()), styles['Normal']))

    content.append(Spacer(1,10))
    content.append(Paragraph(f"Estimated Cost: ₹{prediction:,.0f}", styles['Heading2']))

    content.append(Spacer(1,10))
    content.append(Paragraph("Key Drivers", styles['Heading2']))

    for e in explanations:
        content.append(Paragraph(e, styles['Normal']))

    content.append(Spacer(1,10))
    content.append(Paragraph("Suggestions", styles['Heading2']))

    if suggestions:
        for s in suggestions:
            content.append(Paragraph(s, styles['Normal']))
    else:
        content.append(Paragraph("No suggestions required", styles['Normal']))

    doc.build(content)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button("Download Report", f, "report.pdf")
