import streamlit as st
import pandas as pd
import joblib
import pdfkit
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Insurance Predictor", layout="wide")

model = joblib.load("model.pkl")

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(90deg,#00c6ff,#0072ff);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
🏥 Medical Insurance Cost Predictor
</h1>
<p style='text-align:center'>Smart Insights • Better Decisions</p>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
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

# ---------------- PREDICT ----------------
if st.button("🚀 Generate Report"):

    with st.spinner("Generating report..."):
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

    # Risk
    if smoker == "Yes" or bmi > 30:
        risk = "HIGH RISK"
        risk_color = "#ff4d4f"
    elif bmi > 25:
        risk = "MEDIUM RISK"
        risk_color = "#faad14"
    else:
        risk = "LOW RISK"
        risk_color = "#52c41a"

    # Suggestions
    suggestions = []
    if smoker == "Yes":
        suggestions.append("Quit smoking to significantly reduce cost")
    if bmi > 25:
        suggestions.append("Maintain healthy BMI with exercise")
    if age > 50:
        suggestions.append("Regular health checkups recommended")

    if not suggestions:
        suggestions.append("No changes required — healthy profile")

    # Key factors
    factors = []
    if smoker == "Yes":
        factors.append("Smoking increases cost significantly")
    if bmi > 25:
        factors.append("Higher BMI increases risk")
    if age > 50:
        factors.append("Age contributes to higher cost")

    # ---------------- HTML REPORT ----------------
    html = f"""
    <html>
    <head>
    <style>

    body {{
        font-family: Arial;
        background: #f5f7fb;
        padding: 20px;
    }}

    .header {{
        background: linear-gradient(90deg,#0f2027,#2c5364);
        color: white;
        padding: 20px;
        border-radius: 12px;
    }}

    .card {{
        background: white;
        padding: 15px;
        border-radius: 12px;
        margin-top: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}

    .row {{
        display: flex;
        justify-content: space-between;
    }}

    .badge {{
        padding: 6px 12px;
        border-radius: 8px;
        color: white;
        background: {risk_color};
        font-weight: bold;
    }}

    ul {{
        padding-left: 20px;
    }}

    </style>
    </head>

    <body>

    <div class="header">
        <h2>Medical Insurance Cost Predictor</h2>
        <p>Smart Insights. Better Decisions.</p>
    </div>

    <div class="card">
        <h3>Customer Profile</h3>
        <p><b>Age:</b> {age} &nbsp; | 
           <b>BMI:</b> {bmi} &nbsp; | 
           <b>Children:</b> {children} &nbsp; | 
           <b>Smoker:</b> {smoker} &nbsp; | 
           <b>Gender:</b> {sex}
        </p>
    </div>

    <div class="card">
        <h3>Estimated Insurance Cost</h3>
        <h2>₹{prediction:,.0f}</h2>
        <p>Risk Level: <span class="badge">{risk}</span></p>
    </div>

    <div class="card">
        <h3>Key Drivers</h3>
        <ul>
        {''.join([f"<li>{f}</li>" for f in factors])}
        </ul>
    </div>

    <div class="card">
        <h3>Personalized Suggestions</h3>
        <ul>
        {''.join([f"<li>{s}</li>" for s in suggestions])}
        </ul>
    </div>

    </body>
    </html>
    """

    # Save HTML
    with open("report.html", "w") as f:
        f.write(html)

    # Convert to PDF
    pdfkit.from_file("report.html", "final_report.pdf")

    # Download
    with open("final_report.pdf", "rb") as f:
        st.download_button("📥 Download Report", f, "Medical_Insurance_Report.pdf")
