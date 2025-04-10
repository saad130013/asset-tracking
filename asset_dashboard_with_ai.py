
import streamlit as st
import pandas as pd

st.set_page_config(page_title="لوحة متابعة الأصول", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("asstv2.xlsx", skiprows=2)
    return df

df = load_data()

# تحويل الأعمدة المالية إلى أرقام
columns_to_convert = [
    "القيمة الدفترية", "القيمة المتبقية في نهاية العمر", "الاستهلاك المتراكم",
    "قسط الاهلاك", "التكلفة", "العمر الإنتاجي", "العمر المتبقي"
]

for col in columns_to_convert:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

st.title("📊 لوحة متابعة الأصول")

# ====== الفلاتر التفاعلية ======
st.sidebar.header("🎛️ فلاتر البحث")

selected_entity = st.sidebar.multiselect("اسم الجهة", options=df["اسم الجهة"].dropna().unique())
selected_city = st.sidebar.multiselect("المدينة", options=df["المدينة"].dropna().unique())
selected_type = st.sidebar.multiselect("الوصف بالعربي", options=df["الوصف بالعربي"].dropna().unique())


selected_class_1 = st.sidebar.multiselect(
    "تصنيف الأصل - المستوى الأول",
    options=df["وصف تصنيف الأصول المستوى الأول - عربي"].dropna().unique()
)

selected_class_2 = st.sidebar.multiselect(
    "تصنيف الأصل - المستوى الثاني",
    options=df["وصف تصنيف الأصول المستوى الثاني - عربي"].dropna().unique()
)

selected_class_3 = st.sidebar.multiselect(
    "تصنيف الأصل - المستوى الثالث",
    options=df["وصف تصنيف الأصول المستوى الثالث - عربي"].dropna().unique()
)

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

# ====== المؤشرات الرئيسية ======
col1, col2, col3 = st.columns(3)

col1.metric("📘 صافي القيمة الدفترية", f"{filtered_df['القيمة الدفترية'].sum():,.0f} ريال")
col2.metric("💰 القيمة المتبقية", f"{filtered_df['القيمة المتبقية في نهاية العمر'].sum():,.0f} ريال")
col3.metric("📦 إجمالي التكلفة", f"{filtered_df['التكلفة'].sum():,.0f} ريال")

st.markdown("---")

# ====== توزيع حسب المدينة ======
st.subheader("📍 توزيع الأصول حسب المدينة")
if "المدينة" in filtered_df.columns:
    city_count = filtered_df["المدينة"].value_counts().reset_index()
    city_count.columns = ["المدينة", "عدد الأصول"]
    st.dataframe(city_count)

# ====== عرض كامل للبيانات ======
st.subheader("🗂️ بيانات الأصول (بعد التصفية)")
st.dataframe(filtered_df)
