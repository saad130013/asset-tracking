
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
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
st.set_page_config(page_title="لوحة متابعة الأصول", layout="wide")
st.title("📊 لوحة متابعة الأصول")

# تحميل البيانات
df = pd.read_excel("asstv2.xlsx", skiprows=2)
columns = ["اسم الجهة", "المدينة", "الوصف بالعربي", "التكلفة", "القيمة الدفترية", "العمر المتبقي"]
df = df[columns].fillna("")

# Tabs for data and map
tab1, tab2 = st.tabs(["📊 لوحة البيانات", "🗺️ خريطة الأصول"])

# Tab 1: عرض البيانات
with tab1:
    st.subheader("📈 عرض الأصول")
    st.dataframe(df)

# Tab 2: عرض الأصول على الخريطة
with tab2:
    st.subheader("🗺️ عرض الأصول على الخريطة")
    st.markdown("### اختر المنطقة")
    selected_region = st.selectbox("اختر المنطقة", sorted(df["المنطقة"].dropna().unique()))
    filtered_df = df[df["المنطقة"] == selected_region]
    
    # التأكد من وجود الإحداثيات
    filtered_df = filtered_df[filtered_df["Geographical Coordinates"].notna()]
    
    # تحويل الإحداثيات إلى (lat, lon)
    def extract_coordinates(coord):
        try:
            parts = str(coord).split(",")
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return lat, lon
        except:
            return None, None
        return None, None

    filtered_df["lat"], filtered_df["lon"] = zip(*filtered_df["Geographical Coordinates"].apply(extract_coordinates))
    filtered_df = filtered_df.dropna(subset=["lat", "lon"])

    # إنشاء الخريطة
    m = folium.Map(location=[filtered_df["lat"].mean(), filtered_df["lon"].mean()], zoom_start=6)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in filtered_df.iterrows():
        popup_text = f"""<b>الجهة:</b> {row.get('اسم الجهة', '')}<br>
                         <b>المدينة:</b> {row.get('المدينة', '')}<br>
                         <b>الوصف:</b> {row.get('الوصف بالعربي', '')}<br>
                         <b>التكلفة:</b> {row.get('التكلفة', '')}"""
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(marker_cluster)

    # عرض الخريطة في Streamlit
    st_data = st_folium(m, width=1000, height=600)
