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
st.set_page_config(page_title=" Mediacl Insurance Price Detector ", layout="wide")

model = joblib.load("model.pkl")

# Dummy background data (IMPORTANT for SHAP)
background = pd.DataFrame({
    "age":[30,40,50],
    "bmi":[20,25,30],
    "children":[0,1,2],
    "smoker":[0,1,0],
    "sex":[0,1,0]
})

# ---------------- CSS ----------------
st.markdown("""
<style>
.header {
    text-align:center;
    font-size:42px;
    font-weight:bold;
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.card {
    background: linear-gradient(135deg,#1f4037,#2c5364);
    padding:20px;
    border-radius:15px;
    color:white;
}
.suggest {
    padding:10px;
    background: rgba(255,77,79,0.1);
    border-left:5px solid red;
    margin-bottom:8px;
}
.good {
    background: rgba(82,196,26,0.1);
    border-left:5px solid green;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="header"> Mediacl Insurance Price Detector</div>', unsafe_allow_html=True)

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

    with st.spinner("Analyzing..."):
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

    st.success(f"💰 Estimated Cost: ₹{prediction:,.0f}")

    # ---------------- SHAP EXPLANATION ----------------
    st.markdown("### 🧠 Why is this cost predicted?")

    try:
        explainer = shap.TreeExplainer(model)
    except:
        explainer = shap.KernelExplainer(model.predict, background)

    shap_values = explainer(X)

    # Plot SHAP
    fig, ax = plt.subplots()
    shap.plots.bar(shap_values[0], show=False)
    st.pyplot(fig)

    # ---------------- TEXT EXPLANATION ----------------
    st.markdown("### 🔍 Key Drivers")

    contributions = dict(zip(X.columns, shap_values.values[0]))

    sorted_features = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)

    for feature, value in sorted_features:
        if value > 0:
            st.write(f"🔺 {feature} is increasing cost")
        else:
            st.write(f"🔻 {feature} is reducing cost")

    # ---------------- SUGGESTIONS ----------------
    st.markdown("### 🧠 Suggestions")

    suggestions = []

    if smoker == "Yes":
        suggestions.append("Quit smoking")
    if bmi > 25:
        suggestions.append("Reduce BMI")
    if age > 50:
        suggestions.append("Health monitoring")

    if suggestions:
        for s in suggestions:
            st.markdown(f'<div class="suggest">{s}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="suggest good">No suggestions needed</div>', unsafe_allow_html=True)

    # ---------------- PDF ----------------
    st.markdown("### 📄 Download Report")

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Insurance AI Report", styles['Title']))
    content.append(Spacer(1,10))

    content.append(Paragraph(f"Cost: ₹{prediction:,.0f}", styles['Heading2']))

    content.append(Spacer(1,10))
    content.append(Paragraph("Key Drivers", styles['Heading2']))

    for feature, value in sorted_features:
        direction = "increase" if value > 0 else "reduce"
        content.append(Paragraph(f"{feature} {direction} cost", styles['Normal']))

    content.append(Spacer(1,10))
    content.append(Paragraph("Suggestions", styles['Heading2']))

    if suggestions:
        for s in suggestions:
            content.append(Paragraph(s, styles['Normal']))
    else:
        content.append(Paragraph("No suggestions required", styles['Normal']))

    doc.build(content)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button("Download PDF", f, "report.pdf")
