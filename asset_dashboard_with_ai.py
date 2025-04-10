
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
# ====== تصدير النتائج ======
st.markdown("---")
st.subheader("📤 تصدير النتائج")

col_export1, col_export2 = st.columns(2)

with col_export1:
    excel_filename = "البيانات_المفلترة.xlsx"
    excel_data = filtered_df.to_excel(excel_filename, index=False)
    with open(excel_filename, "rb") as file:
        st.download_button(
            label="📥 تحميل البيانات كـ Excel",
            data=file,
            file_name=excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with col_export2:
    st.info("🚧 تصدير إلى PDF سيتم إضافته قريبًا...")


# ====== إضافة أصل جديد ======
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
        useful_life = st.number_input("Useful Life (بالسنوات)", min_value=0.0, step=1.0)
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
        required_fields = [
            level1_code, level1_desc_ar, level2_code, level2_desc_ar,
            cost, useful_life, remaining_life, country, region, city
        ]

        if all(required_fields):
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
            st.error("⚠️ الرجاء تعبئة جميع الحقول الإلزامية (مثل: التصنيف، التكلفة، الموقع...)")


