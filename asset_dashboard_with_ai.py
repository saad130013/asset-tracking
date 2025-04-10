
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="لوحة متابعة الأصول", layout="wide")
st.markdown("<h1 style='text-align: right;'>لوحة متابعة الأصول - التصنيف الذكي</h1>", unsafe_allow_html=True)

# تحميل البيانات
@st.cache_data
def load_data():
    file_path = "asset_data_with_prediction.xlsx"
    df = pd.read_excel(file_path)
    df[['lat', 'lon']] = df['الإحداثيات'].str.split(',', expand=True)
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    return df

df = load_data()

# إحصائيات
col1, col2, col3, col4 = st.columns(4)
col1.metric("عدد الأصول", len(df))
col2.metric("التكلفة الأصلية", f"{df['التكلفة الأصلية'].sum():,.0f} ريال")
col3.metric("القيمة الدفترية", f"{df['القيمة الدفترية'].sum():,.0f} ريال")
col4.metric("الأصول بتصنيف مختلف", (df['التصنيف المتوقع (ذكاء صناعي)'] != df['التصنيف الفعلي']).sum())

st.markdown("---")

# خريطة تفاعلية
st.markdown("### خريطة الأصول")
st.map(df[['lat', 'lon']].dropna())

# مربع البحث
search_term = st.text_input("ابحث عن أصل (النوع، المدينة، التصنيف...):", key="search")

if search_term:
    df = df[df.apply(lambda row: search_term.lower() in str(row.values).lower(), axis=1)]

# فلاتر متقدمة
with st.expander("فلاتر"):
    region_filter = st.multiselect("المنطقة:", df['المنطقة'].dropna().unique())
    if region_filter:
        df = df[df['المنطقة'].isin(region_filter)]

    mismatch_only = st.checkbox("عرض الأصول ذات التصنيف المختلف فقط")
    if mismatch_only:
        df = df[df['التصنيف المتوقع (ذكاء صناعي)'] != df['التصنيف الفعلي']]

# عرض الجدول
st.markdown("### تفاصيل الأصول مع التصنيف الذكي")
st.dataframe(df.drop(columns=['lat', 'lon']).style.format(thousands=","), use_container_width=True)
