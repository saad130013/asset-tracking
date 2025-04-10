
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from base64 import b64encode

# إعداد الصفحة
st.set_page_config(page_title="لوحة متابعة الأصول", layout="wide")

# ====== تنسيقات CSS ======
custom_css = """
<style>
    .main {
        background-color: #f9f9f9;
        color: #333;
    }
    h1, h2, h3 {
        color: #004080;
    }
    .stButton>button, .stDownloadButton>button {
        color: white;
        background-color: #004080;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ====== شعار الجهة ======
with open("Logo-04.png", "rb") as img_file:
    logo_base64 = b64encode(img_file.read()).decode()

st.markdown(
    f"""
    <div style="text-align:center; margin-bottom: 30px;">
        <img src="data:image/png;base64,{logo_base64}" alt="شعار الهيئة" width="200">
        <h2 style="color:#004080; margin-top: 10px;">هيئة المساحة الجيولوجية السعودية</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ====== تحميل البيانات ======
@st.cache_data
def load_data():
    df = pd.read_excel("asstv2.xlsx", skiprows=2)
    return df

df = load_data()

# ====== تحويل الأعمدة الرقمية ======
columns_to_convert = [
    "القيمة الدفترية", "القيمة المتبقية في نهاية العمر", "الاستهلاك المتراكم",
    "قسط الاهلاك", "التكلفة", "العمر الإنتاجي", "العمر المتبقي"
]
for col in columns_to_convert:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ====== الفلاتر ======
st.sidebar.header("🎛️ فلاتر البحث")
selected_entity = st.sidebar.multiselect("اسم الجهة", options=df["اسم الجهة"].dropna().unique())
selected_city = st.sidebar.multiselect("المدينة", options=df["المدينة"].dropna().unique())
selected_type = st.sidebar.multiselect("الوصف بالعربي", options=df["الوصف بالعربي"].dropna().unique())
selected_class_1 = st.sidebar.multiselect("تصنيف الأصل - المستوى الأول", options=df["وصف تصنيف الأصول المستوى الأول - عربي"].dropna().unique())
selected_class_2 = st.sidebar.multiselect("تصنيف الأصل - المستوى الثاني", options=df["وصف تصنيف الأصول المستوى الثاني - عربي"].dropna().unique())
selected_class_3 = st.sidebar.multiselect("تصنيف الأصل - المستوى الثالث", options=df["وصف تصنيف الأصول المستوى الثالث - عربي"].dropna().unique())

filtered_df = df.copy()
if selected_entity:
    filtered_df = filtered_df[filtered_df["اسم الجهة"].isin(selected_entity)]
if selected_city:
    filtered_df = filtered_df[filtered_df["المدينة"].isin(selected_city)]
if selected_type:
    filtered_df = filtered_df[filtered_df["الوصف بالعربي"].isin(selected_type)]
if selected_class_1:
    filtered_df = filtered_df[filtered_df["وصف تصنيف الأصول المستوى الأول - عربي"].isin(selected_class_1)]
if selected_class_2:
    filtered_df = filtered_df[filtered_df["وصف تصنيف الأصول المستوى الثاني - عربي"].isin(selected_class_2)]
if selected_class_3:
    filtered_df = filtered_df[filtered_df["وصف تصنيف الأصول المستوى الثالث - عربي"].isin(selected_class_3)]

# ====== المؤشرات ======
st.markdown("<h1 style='color:#004080'>📊 لوحة متابعة الأصول</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("📘 صافي القيمة الدفترية", f"{filtered_df['القيمة الدفترية'].sum():,.0f} ريال")
col2.metric("💰 القيمة المتبقية", f"{filtered_df['القيمة المتبقية في نهاية العمر'].sum():,.0f} ريال")
col3.metric("📦 إجمالي التكلفة", f"{filtered_df['التكلفة'].sum():,.0f} ريال")

# ====== تنبيهات ذكية ======
st.markdown("---")
st.subheader("🔔 تنبيهات ذكية")
alerts = []
if "العمر المتبقي" in df.columns:
    expired_assets = df[pd.to_numeric(df["العمر المتبقي"], errors='coerce') == 0]
    if not expired_assets.empty:
        alerts.append(f"⚠️ يوجد {len(expired_assets)} أصل انتهى عمره الإنتاجي.")
if "القيمة الدفترية" in df.columns:
    zero_value_assets = df[pd.to_numeric(df["القيمة الدفترية"], errors='coerce') == 0]
    if not zero_value_assets.empty:
        alerts.append(f"📉 يوجد {len(zero_value_assets)} أصل قيمته الدفترية صفر.")
if "العمر المتبقي" in df.columns and "العمر الإنتاجي" in df.columns:
    try:
        df["نسبة العمر المتبقي"] = pd.to_numeric(df["العمر المتبقي"], errors='coerce') / pd.to_numeric(df["العمر الإنتاجي"], errors='coerce')
        low_life_assets = df[df["نسبة العمر المتبقي"] < 0.1]
        if not low_life_assets.empty:
            alerts.append(f"⏳ يوجد {len(low_life_assets)} أصل يوشك على الانتهاء (أقل من 10٪ من عمره).")
    except:
        pass
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ لا توجد تنبيهات حالياً، كل الأصول في حالة جيدة.")

# ====== نموذج إدخال أصل جديد ======
st.markdown("---")
st.subheader("➕ إضافة أصل جديد")
with st.form("add_asset_form"):
    col1, col2 = st.columns(2)
    with col1:
        level1_code = st.text_input("Level 1 FA Module Code")
        level1_desc_ar = st.text_input("Level 1 FA Module - Arabic Description")
        level1_desc_en = st.text_input("Level 1 FA Module - English Description")
        level2_code = st.text_input("Level 2 FA Module Code")
        level2_desc_ar = st.text_input("Level 2 FA Module - Arabic Description")
        level2_desc_en = st.text_input("Level 2 FA Module - English Description")
        level3_code = st.text_input("Level 3 FA Module Code")
        level3_desc_ar = st.text_input("Level 3 FA Module - Arabic Description")
        cost = st.number_input("Cost", min_value=0.0, step=1.0)
        depreciation = st.number_input("Depreciation amount", min_value=0.0, step=1.0)
    with col2:
        useful_life = st.number_input("Useful Life", min_value=0.0, step=1.0)
        remaining_life = st.number_input("Remaining Useful Life", min_value=0.0, step=1.0)
        country = st.text_input("Country")
        region = st.text_input("Region")
        city = st.text_input("City")
        coordinates = st.text_input("Geographical Coordinates")
        address_id = st.text_input("National Address ID")
        building_number = st.text_input("Building Number")
        floor_number = st.text_input("Floors Number")
        room_number = st.text_input("Room/office Number")
    submitted = st.form_submit_button("📩 تسجيل الأصل")
    if submitted:
        if all([level1_code, level1_desc_ar, level2_code, level2_desc_ar, cost, useful_life, remaining_life, country, region, city]):
            new_row = {
                "Level 1 FA Module Code": level1_code,
                "Level 1 FA Module - Arabic Description": level1_desc_ar,
                "Level 1 FA Module - English Description": level1_desc_en,
                "Level 2 FA Module Code": level2_code,
                "Level 2 FA Module - Arabic Description": level2_desc_ar,
                "Level 2 FA Module - English Description": level2_desc_en,
                "Level 3 FA Module Code": level3_code,
                "Level 3 FA Module - Arabic Description": level3_desc_ar,
                "Cost": cost,
                "Depreciation amount": depreciation,
                "Useful Life": useful_life,
                "Remaining useful life": remaining_life,
                "Country": country,
                "Region": region,
                "City": city,
                "Geographical Coordinates": coordinates,
                "National Address ID": address_id,
                "Building Number": building_number,
                "Floors Number": floor_number,
                "Room/office Number": room_number
            }
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            st.success("✅ تم تسجيل الأصل بنجاح وتمت إضافته إلى الجدول.")
        else:
            st.error("⚠️ الرجاء تعبئة جميع الحقول الإلزامية.")


# ====== تصدير PDF ======
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
import io

st.markdown("---")
st.subheader("🖨️ تصدير النتائج إلى PDF")

if st.button("📄 إنشاء تقرير PDF"):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    try:
        logo = ImageReader("Logo-04.png")
        c.drawImage(logo, x=80, y=height - 100, width=50*mm, height=30*mm, mask='auto')
    except:
        pass

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 120, "تقرير الأصول")

    c.setFont("Helvetica", 9)
    x_offset = 30
    y_offset = height - 140
    row_height = 15
    max_rows = 30
    row_count = 0

    display_cols = ["اسم الجهة", "المدينة", "الوصف بالعربي", "التكلفة", "القيمة الدفترية", "العمر المتبقي"]
    filtered_display_df = filtered_df[display_cols].fillna("")

    for index, row in filtered_display_df.iterrows():
        if row_count >= max_rows:
            c.showPage()
            y_offset = height - 50
            row_count = 0
        y = y_offset - row_height * row_count
        line = f"{row['اسم الجهة']} | {row['المدينة']} | {row['الوصف بالعربي']} | {row['التكلفة']} | {row['القيمة الدفترية']} | {row['العمر المتبقي']}"
        c.drawString(x_offset, y, line)
        row_count += 1

    c.save()
    pdf_buffer.seek(0)

    st.download_button(
        label="⬇️ تحميل تقرير PDF",
        data=pdf_buffer,
        file_name="تقرير_الأصول.pdf",
        mime="application/pdf"
    )

# ====== عرض البيانات وحفظ ======
st.markdown("---")
st.subheader("🗂️ بيانات الأصول (بعد التصفية)")
st.dataframe(filtered_df)

save_excel_filename = "البيانات_بعد_الإضافة.xlsx"
df.to_excel(save_excel_filename, index=False)
with open(save_excel_filename, "rb") as file:
    st.download_button(
        label="💾 تحميل الملف الكامل بعد الإضافة",
        data=file,
        file_name=save_excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
