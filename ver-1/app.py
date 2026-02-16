from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import os
import subprocess
import textwrap

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# -------------------------------------------------
# APP
# -------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------
# FONT
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

# -------------------------------------------------
# HOME
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------------------
# EXCEL → ML → AI → PDF
# -------------------------------------------------
@app.route("/upload-excel", methods=["POST"])
def upload_excel():

    file = request.files.get("excel_file")
    if not file:
        return "Excel dosyası seçilmedi", 400

    # -----------------------------
    # EXCEL OKU
    # -----------------------------
    df = pd.read_excel(file)

    # Kolonları standartlaştır
    df["Region"] = df["Region"].astype(str).str.strip().str.title()
    df["Product"] = df["Product"].astype(str).str.strip()

    # Sayısal kolonları güvenli şekilde dönüştür
    for col in ["Revenue", "Expense", "Profit", "Units_Sold"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = 0

    df.dropna(inplace=True)

    # -----------------------------
    # ML MODEL
    # -----------------------------
    X = df[["Revenue", "Expense"]]
    y = df["Profit"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    r2 = r2_score(y_test, model.predict(X_test))

    df["Predicted_Profit"] = model.predict(X)
    df["Deviation"] = (
        (df["Profit"] - df["Predicted_Profit"]) / df["Predicted_Profit"]
    ) * 100

    # -----------------------------
    # RISK DEĞERLENDİRMESİ (Quantile Yöntemi)
    # -----------------------------
    lower = df["Deviation"].quantile(0.33)
    upper = df["Deviation"].quantile(0.66)

    def risk_label(x):
        if x <= lower:
            return "Yüksek Risk"
        elif x >= upper:
            return "Düşük Risk"
        else:
            return "Orta Risk"

    df["Risk"] = df["Deviation"].apply(risk_label)

    # -----------------------------
    # ŞUBE ÖZET
    # -----------------------------
    summary = df.groupby("Region").agg(
        Ortalama_Gelir=("Revenue", "mean"),
        Ortalama_Gider=("Expense", "mean"),
        Ortalama_Kar=("Profit", "mean"),
        Urun_Cesit_Sayisi=("Product", "nunique"),
        Toplam_Satis_Adedi=("Units_Sold", "sum"),
        Genel_Risk=("Risk", lambda x: x.value_counts().idxmax())
    ).reset_index()

    # -----------------------------
    # ÜRÜN – ŞUBE SATIŞ
    # -----------------------------
    product_sales = df.groupby(["Region", "Product"]).agg(
        Toplam_Satis_Adedi=("Units_Sold", "sum"),
        Ortalama_Kar=("Profit", "mean")
    ).reset_index()

    # -----------------------------
    # OLLAMA – AI
    # -----------------------------
    prompt = f"""
Sen bir finansal analiz uzmanısın ve **SADECE TÜRKÇE** yazabilirsin. 
Hiçbir şekilde İngilizce yazma. 
Rapor dilini tamamen Türkçe kullan.

Aşağıda şube ve ürün bazlı veriler var:

=====================
ŞUBE ÖZET TABLOSU
=====================
{summary.to_string(index=False)}

=====================
ŞUBE ÜRÜN SATIŞ TABLOSU
=====================
{product_sales.to_string(index=False)}

MODEL DOĞRULUK SKORU (R²): {r2:.2f}

Yapılacaklar:
Her şubeyi ayrı bir başlık altında değerlendir.
- Finansal durum
- Ürün çeşitliliği
- Güçlü ürünler
- Zayıf ürünler
- Şubeye özel istatistiklere göre öneriler

En sonunda:
"GENEL YÖNETİCİ ÖNERİLERİ" başlığı altında 5 maddelik genel net öneri yaz.

Kurumsal rapor dili kullan ve **kesinlikle İngilizce kelime kullanma**.
"""


    env = os.environ.copy()
    env["OLLAMA_NO_GPU"] = "1"

    ai_result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        env=env
    )

    ai_text = ai_result.stdout.strip() if ai_result.stdout else "Yapay zekâ yorumu üretilemedi."

    # -----------------------------
    # PDF
    # -----------------------------
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def new_page():
        pdf.showPage()
        pdf.setFont("DejaVu", 10)
        return height - 50

    y = height - 50

    pdf.setFont("DejaVu", 14)
    pdf.drawString(40, y, "Finansal ve Ürün Bazlı Performans Raporu")
    y -= 30

    pdf.setFont("DejaVu", 10)
    pdf.drawString(40, y, f"Model R² Skoru: {r2:.2f}")
    y -= 30

    pdf.setFont("DejaVu", 11)
    pdf.drawString(40, y, "Şube Özeti")
    y -= 20

    pdf.setFont("DejaVu", 9)
    for line in summary.to_string(index=False).split("\n"):
        if y < 50:
            y = new_page()
        pdf.drawString(40, y, line)
        y -= 14

    y -= 25
    pdf.setFont("DejaVu", 11)
    pdf.drawString(40, y, "Yapay Zekâ Değerlendirmeleri")
    y -= 20

    pdf.setFont("DejaVu", 9)
    for paragraph in ai_text.split("\n"):
        wrapped = textwrap.wrap(paragraph, 90)
        for line in wrapped:
            if y < 50:
                y = new_page()
            pdf.drawString(40, y, line)
            y -= 14

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Finansal_Analiz_Raporu.pdf",
        mimetype="application/pdf"
    )

# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
