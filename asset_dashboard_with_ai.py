
import streamlit as st
import pandas as pd

st.set_page_config(page_title="لوحة متابعة الأصول", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("asstv2.xlsx", skiprows=2)
    return df

df = load_data()

# تحويل الأعمدة المالية إلى أرقام والتعامل مع القيم غير الرقمية
columns_to_convert = [
    "القيمة الدفترية", "القيمة المتبقية في نهاية العمر", "الاستهلاك المتراكم",
    "قسط الاهلاك", "التكلفة", "العمر الإنتاجي", "العمر المتبقي"
]

for col in columns_to_convert:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

st.title("📊 لوحة متابعة الأصول")

col1, col2, col3 = st.columns(3)

col1.metric("صافي القيمة الدفترية", f"{df['القيمة الدفترية'].sum():,.0f} ريال")
col2.metric("القيمة المتبقية", f"{df['القيمة المتبقية في نهاية العمر'].sum():,.0f} ريال")
col3.metric("إجمالي التكلفة", f"{df['التكلفة'].sum():,.0f} ريال")

st.markdown("---")

st.subheader("📍 توزيع الأصول حسب المدينة")
if "المدينة" in df.columns:
    city_count = df["المدينة"].value_counts().reset_index()
    city_count.columns = ["المدينة", "عدد الأصول"]
    st.dataframe(city_count)

st.subheader("🗂️ بيانات الأصول الكاملة")
st.dataframe(df)
