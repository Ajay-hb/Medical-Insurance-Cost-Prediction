import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import tempfile
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Insurance Dashboard", layout="wide")

model = joblib.load("model.pkl")

# ---------------- CSS PREMIUM ----------------
st.markdown("""
<style>

/* CARD */
.card {
    background: linear-gradient(135deg, #1f4037, #2c5364);
    padding: 20px;
    border-radius: 15px;
    color: white;
    transition: 0.4s;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 0 30px rgba(0,200,255,0.6);
}

/* FADE */
.fade {
    animation: fadeIn 0.8s ease-in;
}
@keyframes fadeIn {
    from {opacity:0; transform: translateY(10px);}
    to {opacity:1; transform: translateY(0);}
}

/* LOADING */
.skeleton {
    height: 20px;
    background: linear-gradient(90deg, #333, #555, #333);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
    0% {background-position: -200% 0;}
    100% {background-position: 200% 0;}
}

/* PROGRESS */
.progress {
    height: 12px;
    border-radius: 10px;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center'>🏥 Insurance Intelligence System</h1>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("Navigation", ["Prediction", "Dataset"])

# ===================== PREDICTION =====================
if page == "Prediction":

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

        # -------- LOADING --------
        with st.spinner("Analyzing..."):
            time.sleep(1.2)

        smoker_val = 1 if smoker == "Yes" else 0
        sex_val = 1 if sex == "Male" else 0

        df = pd.DataFrame({
            "age":[age],
            "bmi":[bmi],
            "children":[children],
            "smoker":[smoker_val],
            "sex":[sex_val]
        })

        prediction = model.predict(df)[0]

        # -------- RISK --------
        if smoker == "Yes" or bmi > 30:
            risk = "High Risk"
            color = "red"
        elif bmi > 25:
            risk = "Medium Risk"
            color = "orange"
        else:
            risk = "Low Risk"
            color = "green"

        # -------- PROFILE --------
        st.markdown("### 📋 Customer Profile")

        st.markdown(f"""
        <div class="card fade">
        👤 Age: {age} | ⚖️ BMI: {bmi} | 👨‍👩‍👧 Children: {children} | 🚬 Smoker: {smoker} | 🧑 Gender: {sex}
        <hr>
        ⚠️ Risk Level: <span style="color:{color}">{risk}</span>
        </div>
        """, unsafe_allow_html=True)

        # -------- KPI --------
        st.markdown("### 💼 Key Insights")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f'<div class="card fade">💰 Cost <h2>₹{prediction:,.0f}</h2></div>', unsafe_allow_html=True)

        with c2:
            st.markdown(f'<div class="card fade">⚠️ {risk}</div>', unsafe_allow_html=True)

        with c3:
            health = "Good" if bmi < 25 else "Needs Attention"
            st.markdown(f'<div class="card fade">🏃 {health}</div>', unsafe_allow_html=True)

        # -------- PROGRESS BAR --------
        st.markdown("### 📊 Risk Intensity")
        st.markdown(f'<div class="progress" style="width:{min(int(bmi*2),100)}%"></div>', unsafe_allow_html=True)

        # -------- SUGGESTIONS --------
        st.markdown("### 🧠 Suggestions")

        suggestions = []
        if smoker == "Yes":
            suggestions.append("Quit smoking")
        if bmi > 25:
            suggestions.append("Reduce BMI")
        if age > 50:
            suggestions.append("Health checkups")

        for s in suggestions:
            st.write("•", s)

        # -------- PDF --------
        st.markdown("### 📄 Download Report")

        fig, ax = plt.subplots()
        ax.bar(["Cost"], [prediction])

        tmp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(tmp_chart.name)
        plt.close()

        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
        styles = getSampleStyleSheet()

        content = []

        content.append(Paragraph("Insurance Report", styles['Title']))
        content.append(Spacer(1,10))

        content.append(Paragraph("Customer Profile", styles['Heading2']))
        content.append(Paragraph(f"Age: {age}", styles['Normal']))
        content.append(Paragraph(f"BMI: {bmi}", styles['Normal']))
        content.append(Paragraph(f"Children: {children}", styles['Normal']))
        content.append(Paragraph(f"Smoker: {smoker}", styles['Normal']))
        content.append(Paragraph(f"Gender: {sex}", styles['Normal']))
        content.append(Paragraph(f"Risk: {risk}", styles['Normal']))

        content.append(Spacer(1,10))
        content.append(Paragraph(f"Cost: ₹{prediction:,.0f}", styles['Heading2']))

        content.append(Spacer(1,10))
        content.append(Paragraph("Suggestions", styles['Heading2']))

        for s in suggestions:
            content.append(Paragraph(f"• {s}", styles['Normal']))

        content.append(Spacer(1,15))
        content.append(Image(tmp_chart.name, width=400, height=250))

        doc.build(content)

        with open(tmp_pdf.name, "rb") as f:
            st.download_button("📥 Download PDF", f, "report.pdf")

# ===================== DATASET =====================
elif page == "Dataset":

    st.title("📂 Dataset")

    df = pd.read_csv("insurance.csv")

    st.dataframe(df)

    st.download_button("Download CSV", df.to_csv(index=False), "data.csv")
