
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import arabic_reshaper
from bidi.algorithm import get_display

# إعدادات
font_name = "Amiri"
font_path = "Amiri-Regular.ttf"
logo_path = "Logo-04.png"
excel_path = "asstv2.xlsx"
output_pdf = "تقرير_الأصول_عربي_مبسط.pdf"

# تسجيل الخط العربي
pdfmetrics.registerFont(TTFont(font_name, font_path))

# تحميل البيانات واختيار الأعمدة المطلوبة
df = pd.read_excel(excel_path, skiprows=2)
columns = ["اسم الجهة", "المدينة", "الوصف بالعربي", "التكلفة", "القيمة الدفترية", "العمر المتبقي"]
df = df[columns].fillna("")

# إعداد ملف PDF
c = canvas.Canvas(output_pdf, pagesize=A4)
width, height = A4

# إدراج الشعار
try:
    logo = ImageReader(logo_path)
    c.drawImage(logo, x=80, y=height - 100, width=50*mm, height=30*mm, mask='auto')
except:
    pass

# عنوان التقرير
c.setFont(font_name, 16)
title = get_display(arabic_reshaper.reshape("تقرير الأصول"))
c.drawCentredString(width / 2, height - 120, title)

# إعداد الجدول
c.setFont(font_name, 10)
x_offset = width - 30
y_offset = height - 140
row_height = 18
row_count = 0
max_rows_per_page = 26

for _, row in df.iterrows():
    if row_count >= max_rows_per_page:
        c.showPage()
        c.setFont(font_name, 10)
        y_offset = height - 50
        row_count = 0

    y = y_offset - row_height * row_count
    values = [str(row[col]) for col in columns]
    reshaped = [get_display(arabic_reshaper.reshape(val)) for val in values]
    line = " | ".join(reshaped)
    c.drawRightString(x_offset, y, line)
    row_count += 1

# حفظ PDF
c.save()
print(f"✅ تم إنشاء التقرير: {output_pdf}")
