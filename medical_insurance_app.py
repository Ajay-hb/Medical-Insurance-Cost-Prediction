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
st.set_page_config(page_title="Insurance Intelligence Dashboard", layout="wide")

# ---------------- LOAD ----------------
model = joblib.load("model.pkl")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🏥 Insurance Cost Intelligence Dashboard</h1>
<p style='text-align: center;'>💰 Predict • Analyze • Optimize</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Simulator", "Dataset"])

# ===================== DASHBOARD =====================
if page == "Dashboard":

    st.markdown("## 📊 Customer Input Panel")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", 18, 65, 30)
        bmi = st.number_input("BMI", 10.0, 50.0, 25.0)

    with col2:
        children = st.number_input("Children", 0, 5, 1)
        smoker = st.selectbox("Smoker", ["Yes", "No"])

    with col3:
        sex = st.selectbox("Gender", ["Male", "Female"])

    smoker_val = 1 if smoker == "Yes" else 0
    sex_val = 1 if sex == "Male" else 0

    input_data = pd.DataFrame({
        "age":[age],
        "bmi":[bmi],
        "children":[children],
        "smoker":[smoker_val],
        "sex":[sex_val]
    })

    prediction = model.predict(input_data)[0]

    # ---------------- KPI CARDS ----------------
    st.markdown("### 💼 Key Metrics")

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("💰 Estimated Cost", f"₹{prediction:,.0f}")

    with k2:
        risk = "Low"
        if smoker == "Yes" or bmi > 30:
            risk = "High"
        elif bmi > 25:
            risk = "Medium"

        st.metric("⚠️ Risk Level", risk)

    with k3:
        if bmi < 25:
            health = "Good"
        else:
            health = "Needs Attention"

        st.metric("🏃 Health Status", health)

    # ---------------- INTERACTIVE DASHBOARD ----------------
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

    # Cost Bar
    with col5:
        fig_cost = px.bar(
            x=["Estimated Cost"],
            y=[prediction],
            title="💰 Cost Estimate"
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # ---------------- COMPARISON ----------------
    st.markdown("### 📈 Impact Analysis")

    baseline = pd.DataFrame({
        "age":[age],
        "bmi":[25],
        "children":[children],
        "smoker":[0],
        "sex":[sex_val]
    })

    baseline_cost = model.predict(baseline)[0]

    fig_compare = px.bar(
        x=["Your Profile", "Optimized Profile"],
        y=[prediction, baseline_cost],
        title="Optimization Potential"
    )

    st.plotly_chart(fig_compare, use_container_width=True)

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
        Paragraph(f"Cost: ₹{prediction:,.0f}", styles['Normal']),
        Spacer(1, 10),
        Image(tmp_chart.name, width=400, height=250)
    ]

    doc.build(content)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button("📥 Download PDF", f, "report.pdf")

# ===================== SIMULATOR =====================
elif page == "Simulator":

    st.title("🎯 What-If Simulator")

    col1, col2 = st.columns(2)

    with col1:
        bmi_old = st.number_input("Current BMI", 10.0, 50.0, 30.0)
    with col2:
        bmi_new = st.number_input("Improved BMI", 10.0, 50.0, 25.0)

    data_old = pd.DataFrame({"age":[30],"bmi":[bmi_old],"children":[1],"smoker":[1],"sex":[1]})
    data_new = pd.DataFrame({"age":[30],"bmi":[bmi_new],"children":[1],"smoker":[0],"sex":[1]})

    cost_old = model.predict(data_old)[0]
    cost_new = model.predict(data_new)[0]

    fig = px.bar(x=["Current","Improved"], y=[cost_old, cost_new])
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"💰 Savings: ₹{(cost_old-cost_new):,.0f}")

# ===================== DATASET =====================
elif page == "Dataset":

    st.title("📂 Dataset")

    df = pd.read_csv("medical_insurance.csv")

    st.dataframe(df)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        "dataset.csv"
    )

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built using ML + Streamlit")
