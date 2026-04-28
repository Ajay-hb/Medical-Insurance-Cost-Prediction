import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Insurance Cost Pro System", layout="wide")

# ---------------- LOAD ----------------
model = joblib.load("model.pkl")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🏥 Insurance Cost Intelligence System</h1>
<p style='text-align: center;'>💰 Predict • Analyze • Optimize • Simulate</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["Prediction", "What-If Simulator", "Dataset"])

# ===================== PREDICTION =====================
if page == "Prediction":

    st.subheader("📊 Customer Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.slider("Age", 18, 65, 30)
        bmi = st.slider("BMI", 15.0, 40.0, 25.0)

    with col2:
        children = st.slider("Children", 0, 5, 1)
        smoker = st.selectbox("Smoker", ["Yes", "No"])

    with col3:
        sex = st.selectbox("Gender", ["Male", "Female"])

    smoker_val = 1 if smoker == "Yes" else 0
    sex_val = 1 if sex == "Male" else 0

    input_data = pd.DataFrame({
        "age": [age],
        "bmi": [bmi],
        "children": [children],
        "smoker": [smoker_val],
        "sex": [sex_val]
    })

    if st.button("💰 Predict Cost"):

        prediction = model.predict(input_data)[0]

        st.success(f"💵 Estimated Cost: ₹{prediction:,.0f}")

        # ---------------- SUGGESTIONS ----------------
        st.subheader("📊 Improvement Suggestions")

        suggestions = []

        if smoker == "Yes":
            suggestions.append("Quit smoking")
        if bmi > 25:
            suggestions.append("Reduce BMI")
        if age > 50:
            suggestions.append("Regular health checkups")

        for s in suggestions:
            st.write("•", s)

        # ---------------- DASHBOARD ----------------
        st.subheader("📊 Interactive Dashboard")

        # BMI Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            title={'text': "BMI"},
            gauge={'axis': {'range': [0, 40]}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Cost Chart
        fig_cost = px.bar(x=["Cost"], y=[prediction], title="Predicted Cost")
        st.plotly_chart(fig_cost, use_container_width=True)

        # ---------------- PDF ----------------
        tmp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig_cost.write_image(tmp_chart.name)

        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
        styles = getSampleStyleSheet()

        content = [
            Paragraph("Insurance Report", styles['Title']),
            Spacer(1, 10),
            Paragraph(f"Cost: ₹{prediction:,.0f}", styles['Normal'])
        ]

        doc.build(content)

        with open(tmp_pdf.name, "rb") as f:
            st.download_button("📥 Download Report", f, "report.pdf")

# ===================== WHAT-IF SIMULATOR =====================
elif page == "What-If Simulator":

    st.title("🎯 What-If Simulator")

    age = st.slider("Age", 18, 65, 30)
    bmi_original = st.slider("Current BMI", 15.0, 40.0, 30.0)
    bmi_new = st.slider("Improved BMI", 15.0, 40.0, 25.0)

    smoker = st.selectbox("Smoker", ["Yes", "No"])
    children = st.slider("Children", 0, 5, 1)
    sex = st.selectbox("Gender", ["Male", "Female"])

    smoker_val = 1 if smoker == "Yes" else 0
    sex_val = 1 if sex == "Male" else 0

    # Original
    original_data = pd.DataFrame({
        "age": [age],
        "bmi": [bmi_original],
        "children": [children],
        "smoker": [smoker_val],
        "sex": [sex_val]
    })

    # Improved
    new_data = original_data.copy()
    new_data["bmi"] = bmi_new

    cost_original = model.predict(original_data)[0]
    cost_new = model.predict(new_data)[0]

    st.subheader("📊 Cost Comparison")

    fig = px.bar(
        x=["Current", "Improved"],
        y=[cost_original, cost_new],
        title="Cost Reduction Simulation"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"💰 You can save ₹{(cost_original - cost_new):,.0f}")

# ===================== DATASET =====================
elif page == "Dataset":

    st.title("📂 Dataset Explorer")

    df = pd.read_csv("medical_insurance.csv")

    st.dataframe(df.head())

    fig = px.scatter(df, x="bmi", y="charges", color="smoker")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built with Machine Learning + Streamlit")
