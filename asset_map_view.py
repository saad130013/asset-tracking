
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# إعداد الصفحة
st.set_page_config(page_title="خريطة الأصول", layout="wide")
st.title("🗺️ عرض الأصول على الخريطة")

# تحميل البيانات
df = pd.read_excel("asstv2.xlsx", skiprows=2)

# التأكد من وجود الإحداثيات
df = df[df["Geographical Coordinates"].notna()]

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

df["lat"], df["lon"] = zip(*df["Geographical Coordinates"].apply(extract_coordinates))
df = df.dropna(subset=["lat", "lon"])

# فلتر للمنطقة
selected_region = st.selectbox("اختر المنطقة", sorted(df["المنطقة"].dropna().unique()))
filtered_df = df[df["المنطقة"] == selected_region]

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
