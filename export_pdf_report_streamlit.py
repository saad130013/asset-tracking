
import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import arabic_reshaper
from bidi.algorithm import get_display
import io

# تسجيل الخط العربي Amiri
font_path = "Amiri-Regular.ttf"
pdfmetrics.registerFont(TTFont("Amiri", font_path))

# إعداد الصفحة
st.set_page_config(page_title="تقرير الأصول - PDF", layout="wide")
st.title("📄 تصدير تقرير الأصول إلى PDF (يدعم العربية)")

# تحميل البيانات
excel_path = "asstv2.xlsx"
df = pd.read_excel(excel_path, skiprows=2)
columns = ["اسم الجهة", "المدينة", "الوصف بالعربي", "التكلفة", "القيمة الدفترية", "العمر المتبقي"]
df = df[columns].fillna("")

# زر توليد التقرير
if st.button("🚀 إنشاء تقرير PDF"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # إدراج الشعار
    try:
        logo = ImageReader("Logo-04.png")
        c.drawImage(logo, x=80, y=height - 100, width=50*mm, height=30*mm, mask='auto')
    except:
        pass

    # عنوان التقرير
    c.setFont("Amiri", 16)
    title = get_display(arabic_reshaper.reshape("تقرير الأصول"))
    c.drawCentredString(width / 2, height - 120, title)

    # طباعة البيانات
    c.setFont("Amiri", 10)
    x_offset = width - 30
    y_offset = height - 140
    row_height = 18
    row_count = 0
    max_rows_per_page = 26

    for _, row in df.iterrows():
        if row_count >= max_rows_per_page:
            c.showPage()
            c.setFont("Amiri", 10)
            y_offset = height - 50
            row_count = 0

        y = y_offset - row_height * row_count
        values = [str(row[col]) for col in columns]
        reshaped = [get_display(arabic_reshaper.reshape(val)) for val in values]
        line = " | ".join(reshaped)
        c.drawRightString(x_offset, y, line)
        row_count += 1

    c.save()
    buffer.seek(0)

    st.success("✅ تم إنشاء التقرير بنجاح!")

    st.download_button(
        label="⬇️ تحميل تقرير PDF",
        data=buffer,
        file_name="تقرير_الأصول_عربي.pdf",
        mime="application/pdf"
    )
