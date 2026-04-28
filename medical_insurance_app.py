import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import matplotlib.pyplot as plt
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Insurance Cost Intelligence System", layout="wide")

# ---------------- LOAD ----------------
model = joblib.load("model.pkl")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align: center;'>🏥 Insurance Cost Intelligence System</h1>
<p style='text-align: center;'>💰 Predict • Analyze • Optimize</p>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["Prediction", "What-If Simulator", "Dataset"])

# ===================== PREDICTION =====================
if page == "Prediction":

    st.subheader("📊 Enter Customer Details")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", min_value=18, max_value=65, value=30)
        bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=25.0)

    with col2:
        children = st.number_input("Number of Children", min_value=0, max_value=5, value=1)
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
        st.subheader("📊 Suggestions to Reduce Cost")

        suggestions = []

        if smoker == "Yes":
            suggestions.append("Quit smoking")
        if bmi > 25:
            suggestions.append("Reduce BMI (exercise & diet)")
        if age > 50:
            suggestions.append("Regular health checkups")

        if suggestions:
            for s in suggestions:
                st.write("•", s)
        else:
            st.success("Healthy profile — optimized cost")

        # ---------------- CHART ----------------
        fig = px.bar(x=["Cost"], y=[prediction], title="Predicted Cost")
        st.plotly_chart(fig, use_container_width=True)

        # ---------------- PDF ----------------
        st.markdown("### 📄 Download Report")

        fig2, ax = plt.subplots()
        ax.bar(["Cost"], [prediction])
        ax.set_title("Insurance Cost")

        tmp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp_chart.name)
        plt.close()

        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
        styles = getSampleStyleSheet()

        content = []

        content.append(Paragraph("Medical Insurance Report", styles['Title']))
        content.append(Spacer(1, 10))

        content.append(Paragraph(f"Age: {age}", styles['Normal']))
        content.append(Paragraph(f"BMI: {bmi}", styles['Normal']))
        content.append(Paragraph(f"Children: {children}", styles['Normal']))
        content.append(Paragraph(f"Smoker: {smoker}", styles['Normal']))

        content.append(Spacer(1, 10))
        content.append(Paragraph(f"Predicted Cost: ₹{prediction:,.0f}", styles['Heading2']))

        content.append(Spacer(1, 10))
        content.append(Paragraph("Suggestions:", styles['Heading3']))

        if suggestions:
            for s in suggestions:
                content.append(Paragraph(f"• {s}", styles['Normal']))
        else:
            content.append(Paragraph("No improvements needed", styles['Normal']))

        content.append(Spacer(1, 15))
        content.append(Image(tmp_chart.name, width=400, height=250))

        doc.build(content)

        with open(tmp_pdf.name, "rb") as f:
            st.download_button("📥 Download PDF", f, "report.pdf")

# ===================== WHAT-IF =====================
elif page == "What-If Simulator":

    st.title("🎯 Cost Optimization Simulator")

    st.markdown("### Compare current vs improved lifestyle")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Profile")
        age = st.number_input("Age", 18, 65, 30)
        bmi_current = st.number_input("Current BMI", 10.0, 50.0, 30.0)
        smoker_current = st.selectbox("Smoker (Current)", ["Yes", "No"])
        children = st.number_input("Children", 0, 5, 1)
        sex = st.selectbox("Gender", ["Male", "Female"])

    with col2:
        st.subheader("Improved Profile")
        bmi_new = st.number_input("Improved BMI", 10.0, 50.0, 25.0)
        smoker_new = st.selectbox("Smoker (Improved)", ["Yes", "No"])

    # Encoding
    def encode(smoker, sex):
        return (
            1 if smoker == "Yes" else 0,
            1 if sex == "Male" else 0
        )

    smk_c, sex_val = encode(smoker_current, sex)
    smk_n, _ = encode(smoker_new, sex)

    current = pd.DataFrame({
        "age":[age],"bmi":[bmi_current],"children":[children],"smoker":[smk_c],"sex":[sex_val]
    })

    improved = pd.DataFrame({
        "age":[age],"bmi":[bmi_new],"children":[children],"smoker":[smk_n],"sex":[sex_val]
    })

    cost_current = model.predict(current)[0]
    cost_new = model.predict(improved)[0]

    st.subheader("📊 Cost Comparison")

    fig = px.bar(
        x=["Current", "Improved"],
        y=[cost_current, cost_new],
        title="Cost Impact Analysis"
    )

    st.plotly_chart(fig, use_container_width=True)

    savings = cost_current - cost_new

    if savings > 0:
        st.success(f"💰 You can save ₹{savings:,.0f}")
    else:
        st.warning("No cost improvement detected")

# ===================== DATASET =====================
elif page == "Dataset":

    st.title("📂 Dataset Explorer")

    df = pd.read_csv("insurance.csv")

    st.subheader("📊 Dataset Overview")
    st.write("Shape:", df.shape)

    st.subheader("🔍 Full Dataset")
    st.dataframe(df)

    st.subheader("📈 Summary")
    st.write(df.describe())

    st.download_button(
        "📥 Download Dataset",
        df.to_csv(index=False),
        file_name="insurance_dataset.csv"
    )

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built using Machine Learning & Streamlit")
