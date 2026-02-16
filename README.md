# ai-ml-based-financial-reporting-system
A Flask-based financial analysis application that dynamically processes uploaded datasets, applies regression or classification models, and generates structured PDF reports supported by rule-based and AI-generated insights.
📊 Financial ML Decision Support System (Version 1)
📌 Overview

This project is the first version of a machine learning–based financial decision support system developed during my software engineering internship.

The system analyzes uploaded financial datasets, performs regression-based profit prediction, calculates deviation metrics, and generates structured PDF reports for managerial decision support.

Version 1 focuses specifically on financial performance analysis using a fixed-schema regression approach.

🎯 Key Features

📂 Excel file upload support

🧹 Automated data preprocessing (NaN handling, numeric selection)

📈 Linear Regression–based profit prediction

📊 Deviation analysis (Predicted vs Actual comparison)

⚠ Risk classification using quantile-based segmentation

📄 Automated PDF report generation

🌐 Web interface built with Flask

🧠 Machine Learning Approach

Version 1 applies:

Linear Regression for financial profit prediction

R² score for model performance evaluation

Quantile-based risk segmentation for performance categorization

Deviation is calculated as:

Deviation (%) = (Actual Profit - Predicted Profit) / Predicted Profit * 100


This allows identification of high-risk and underperforming units.

🏗 System Architecture

The system follows this workflow:

File Upload

Data Reading (Pandas)

Data Preprocessing

Model Training (Scikit-learn)

Prediction

Performance Evaluation

PDF Report Generation

The backend is implemented using Flask, and reports are generated using ReportLab.

🛠 Tech Stack

Python

Flask

Pandas

Scikit-learn

ReportLab

OpenPyXL

HTML / CSS (Frontend interface)

📂 Example Financial Dataset Structure

The system expects financial datasets including variables such as:

Revenue

Expense

Profit

Units_Sold

Region

Product

Version 1 works with a fixed financial schema.

🚀 How to Run
1️⃣ Create Virtual Environment
python -m venv venv

2️⃣ Activate Environment

Windows:

venv\Scripts\activate

3️⃣ Install Requirements
pip install -r requirements.txt


Or manually:

pip install flask pandas scikit-learn reportlab openpyxl joblib

4️⃣ Run Application
python app.py


Then open:

http://127.0.0.1:5000

🔍 Version Notes

Version 1:

Uses fixed regression model

Designed specifically for financial analysis

Risk classification based on quantile deviation

No dynamic model selection

Future versions introduce:

Dynamic column detection

Automatic model selection (Regression / Classification)

AI-assisted report interpretation

Improved robustness and scalability

📈 Project Purpose

The goal of this project is to demonstrate how machine learning models can be integrated into financial decision-making processes and automated reporting pipelines.

This version establishes the core analytical engine that later evolved into a more flexible and generalized decision support platform.