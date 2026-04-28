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

# ---------------- LOAD MODEL ----------------
model = joblib.load("model.pkl")

# ---------------- CSS (ANIMATED CARDS) ----------------
st.markdown("""
<style>
.card {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 20px;
    border-radius: 15px;
    color: white;
    transition: all 0.4s ease;
    box-shadow: 0 0 10px rgba(0,0,0,0.4);
}
.card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 0 25px rgba(0, 183, 255, 0.6);
}
.card-title {
    font-size: 14px;
    opacity: 0.7;
}
.card-value {
    font-size: 24px;
    font-weight: bold;
}
.fade-in {
    animation: fadeIn 1s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🏥 Insurance Cost Intelligence Dashboard</h1>
<p style='text-align: center;'>💰 Predict • Analyze • Optimize</p>
""", unsafe_allow_html=True)

# ---------------- INPUTS ----------------
st.markdown("### 📊 Enter Customer Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 18, 65, 30)
    bmi = st.number_input("BMI", 10.0, 50.0, 25.0)

with col2:
    children = st.number_input("Children", 0, 5, 1)
    smoker = st.selectbox("Smoker", ["Yes", "No"])

with col3:
    sex = st.selectbox("Gender", ["Male", "Female"])

# Encode
smoker_val = 1 if smoker == "Yes" else 0
sex_val = 1 if sex == "Male" else 0

input_data = pd.DataFrame({
    "age":[age],
    "bmi":[bmi],
    "children":[children],
    "smoker":[smoker_val],
    "sex":[sex_val]
})

# ---------------- BUTTON ----------------
predict = st.button("🚀 Predict Insurance Cost")

if predict:

    prediction = model.predict(input_data)[0]

    # ---------------- PREMIUM PROFILE CARD ----------------
    st.markdown("### 📋 Customer Profile")

    if smoker == "Yes" or bmi > 30:
        risk = "High Risk"
        color = "#ff4d4f"
    elif bmi > 25:
        risk = "Medium Risk"
        color = "#faad14"
    else:
        risk = "Low Risk"
        color = "#52c41a"

    st.markdown(f"""
    <div class="card fade-in">
    <b>👤 Age:</b> {age} &nbsp;&nbsp; | 
    <b>⚖️ BMI:</b> {bmi} &nbsp;&nbsp; | 
    <b>👨‍👩‍👧 Children:</b> {children} &nbsp;&nbsp; | 
    <b>🚬 Smoker:</b> {smoker} &nbsp;&nbsp; | 
    <b>🧑 Gender:</b> {sex}
    <hr>
    <b>⚠️ Risk Level:</b> <span style="color:{color}">{risk}</span>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- ANIMATED KPI CARDS ----------------
    st.markdown("### 💼 Key Insights")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="card fade-in">
            <div class="card-title">💰 Estimated Cost</div>
            <div class="card-value">₹{prediction:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card fade-in">
            <div class="card-title">⚠️ Risk Level</div>
            <div class="card-value" style="color:{color};">{risk}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        health = "Good" if bmi < 25 else "Needs Attention"
        st.markdown(f"""
        <div class="card fade-in">
            <div class="card-title">🏃 Health Status</div>
            <div class="card-value">{health}</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- SUGGESTIONS ----------------
    st.markdown("### 🧠 Suggestions")

    if smoker == "Yes":
        st.write("• Quit smoking to reduce insurance cost")
    if bmi > 25:
        st.write("• Reduce BMI through exercise and diet")
    if age > 50:
        st.write("• Maintain regular health checkups")

    # ---------------- GRAPHS ----------------
    st.markdown("### 📊 Analytics")

    col4, col5 = st.columns(2)

    with col4:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            title={'text': "BMI Level"},
            gauge={'axis': {'range': [0, 50]}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col5:
        fig_cost = px.bar(
            x=["Estimated Cost"],
            y=[prediction],
            labels={"x": "Category", "y": "Cost (₹)"},
            title="Insurance Cost"
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # ---------------- PDF ----------------
    st.markdown("### 📄 Download Report")

    fig, ax = plt.subplots()
    ax.bar(["Cost"], [prediction])

    tmp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(tmp_chart.name)
    plt.close()

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("Insurance Report", styles['Title']),
        Spacer(1, 10),
        Paragraph(f"Age: {age}", styles['Normal']),
        Paragraph(f"BMI: {bmi}", styles['Normal']),
        Paragraph(f"Children: {children}", styles['Normal']),
        Paragraph(f"Smoker: {smoker}", styles['Normal']),
        Paragraph(f"Cost: ₹{prediction:,.0f}", styles['Heading2']),
        Spacer(1, 10),
        Image(tmp_chart.name, width=400, height=250)
    ]

    doc.build(content)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button("📥 Download PDF", f, "insurance_report.pdf")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with Machine Learning + Streamlit")
