# 🏥 Medical Insurance Cost Prediction

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Regression-green)
![Library](https://img.shields.io/badge/Scikit--Learn-Enabled-orange)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Project Overview
This project predicts **medical insurance costs** using machine learning techniques based on personal and lifestyle factors like age, BMI, and smoking status.

It helps understand **what drives insurance charges** and builds a predictive model for real-world applications.

---

## 🎯 Objectives
- Analyze factors affecting insurance costs  
- Perform Exploratory Data Analysis (EDA)  
- Build regression models  
- Improve prediction performance  

---

## 📂 Dataset Features

| Feature   | Description |
|----------|------------|
| age      | Age of the individual |
| sex      | Gender |
| bmi      | Body Mass Index |
| children | Number of dependents |
| smoker   | Smoking status |
| region   | Residential region |
| charges  | Insurance cost (Target) |

---

## 🛠️ Tech Stack
- **Python**
- **Pandas, NumPy**
- **Matplotlib, Seaborn**
- **Scikit-learn**

---

## 🔍 Project Workflow

### 📊 1. Data Preprocessing
- Handling categorical variables  
- Checking missing values  
- Feature encoding  

### 📈 2. Exploratory Data Analysis
- Distribution of charges  
- Impact of smoking  
- Correlation heatmaps  

### 🤖 3. Model Building
- Linear Regression  
- Model training & testing  

### 📏 4. Evaluation Metrics
- R² Score  
- MAE  
- MSE  

---

## 📊 Results
- Strong predictors: **Smoking, BMI, Age**  
- Achieved good accuracy using regression model  
- Clear cost difference between smokers vs non-smokers  

---

## 📸 Project Screenshots

### 🔹 Data Distribution
![Distribution](images/distribution.png)

### 🔹 Correlation Heatmap
![Heatmap](images/Screenshot 2026-04-24 115011.png)

### 🔹 Model Prediction vs Actual
![Prediction](images/prediction.png)



---

## 🚀 How to Run

```bash
# Clone repo
git clone https://github.com/your-username/medical-insurance-prediction.git

# Move into project folder
cd medical-insurance-prediction

# Install dependencies
pip install -r requirements.txt

# Run notebook
jupyter notebook
