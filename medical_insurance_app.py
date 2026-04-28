import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Insurance Dashboard", layout="wide")

model = joblib.load("model.pkl")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🏥 Insurance Cost Dashboard</h1>
<p style='text-align: center;'>💰 Predict • Analyze • Optimize</p>
""", unsafe_allow_html=True)

# ===================== MAIN =====================
st.subheader("📊 Enter Customer Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 18, 65, 30)
    bmi = st.number_input("BMI", 10.0, 50.0, 25.0)

with col2:
    children = st.number_input("Children", 0, 5, 1)
    smoker = st.selectbox("Smoker", ["Yes", "No"])

with col3:
    sex = st.selectbox("Gender", ["Male", "Female"])

# Encoding
smoker_val = 1 if smoker == "Yes" else 0
sex_val = 1 if sex == "Male" else 0

input_data = pd.DataFrame({
    "age":[age],
    "bmi":[bmi],
    "children":[children],
    "smoker":[smoker_val],
    "sex":[sex_val]
})

# ---------------- PREDICT ----------------
if st.button("💰 Predict Cost"):

    prediction = model.predict(input_data)[0]

    # ---------------- SHOW INPUT ----------------
    st.markdown("### 📋 Entered Details")

    st.write({
        "Age": age,
        "BMI": bmi,
        "Children": children,
        "Smoker": smoker,
        "Gender": sex
    })

    # ---------------- COST ----------------
    st.markdown("### 💰 Estimated Cost")
    st.success(f"₹{prediction:,.0f}")

    # ---------------- SUGGESTIONS ----------------
    st.markdown("### 📊 Suggestions")

    suggestions = []

    if smoker == "Yes":
        suggestions.append("Quit smoking to reduce premium significantly")

    if bmi > 25:
        suggestions.append("Reduce BMI through diet and exercise")

    if age > 50:
        suggestions.append("Maintain regular health checkups")

    if suggestions:
        for s in suggestions:
            st.write("•", s)
    else:
        st.success("Healthy profile — no major improvements needed")

    # ---------------- DASHBOARD ----------------
    st.markdown("---")
    st.markdown("## 📊 Live Analytics Dashboard")

    col4, col5 = st.columns(2)

    # BMI Gauge
    with col4:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            title={'text': "BMI Level"},
            gauge={'axis': {'range': [0, 50]}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Cost Chart
    with col5:
        fig_cost = px.bar(
            x=["Insurance Cost"],
            y=[prediction],
            labels={"x": "Category", "y": "Cost (₹)"},
            title="Estimated Insurance Cost"
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # ---------------- PDF REPORT ----------------
    st.markdown("### 📄 Download Report")

    fig, ax = plt.subplots()
    ax.bar(["Cost"], [prediction])
    ax.set_ylabel("₹ Cost")

    tmp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp_chart.name)
    plt.close()

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Insurance Report", styles['Title']))
    content.append(Spacer(1, 10))

    content.append(Paragraph("Customer Details:", styles['Heading2']))
    content.append(Paragraph(f"Age: {age}", styles['Normal']))
    content.append(Paragraph(f"BMI: {bmi}", styles['Normal']))
    content.append(Paragraph(f"Children: {children}", styles['Normal']))
    content.append(Paragraph(f"Smoker: {smoker}", styles['Normal']))
    content.append(Paragraph(f"Gender: {sex}", styles['Normal']))

    content.append(Spacer(1, 10))
    content.append(Paragraph(f"Predicted Cost: ₹{prediction:,.0f}", styles['Heading2']))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Suggestions:", styles['Heading2']))

    if suggestions:
        for s in suggestions:
            content.append(Paragraph(f"• {s}", styles['Normal']))
    else:
        content.append(Paragraph("No improvements needed", styles['Normal']))

    content.append(Spacer(1, 15))
    content.append(Image(tmp_chart.name, width=400, height=250))

    doc.build(content)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button("📥 Download PDF", f, "insurance_report.pdf")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built using Machine Learning & Streamlit")
