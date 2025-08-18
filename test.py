import math
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

try:
    from geomag import GeoMag
    GM = GeoMag()
    HAVE_GEOMAG = True
except Exception:
    GM = None
    HAVE_GEOMAG = False

def get_magnetic_field(lat, lon):
    if HAVE_GEOMAG and GM is not None:
        res = GM.GeoMag(lat, lon)
        return res.ti, res.dip, res.dec
    B = 30000 * math.sqrt(1+3*(math.sin(math.radians(lat))**2))
    I = math.degrees(math.atan2(2*math.tan(math.radians(lat)),1))
    return B, I, 0.0

st.set_page_config(page_title="지구 자기장", layout="wide")
st.title("🧲 지구 자기장 시각화 (강화 버전)")

st.write("위도와 경도를 조절하세요. 선택한 위치가 지도 위에 표시되며, 자기장의 방향과 세기가 함께 나타납니다.")

col1, col2 = st.columns([1,2])

with col1:
    lat = st.slider("위도", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("경도", -180.0, 180.0, 127.0, step=0.1)

    B, I, D = get_magnetic_field(lat, lon)

    st.subheader("선택한 위치의 자기장")
    st.metric("세기 (nT)", f"{B:.0f}")
    st.metric("경사각 (°)", f"{I:.1f}")
    st.metric("편각 (°)", f"{D:.1f}")

    st.markdown(f"<div style='padding:10px; background-color:rgb({int(min(B/60000*255,255))},0,{int(255-min(B/60000*255,255))}); color:white;'>세기 색상 표시</div>", unsafe_allow_html=True)

with col2:
    lat_grid = np.linspace(-80,80,21)
    lon_grid = np.linspace(-180,180,37)
    B_grid = np.zeros((len(lat_grid), len(lon_grid)))
    U = np.zeros_like(B_grid)
    V = np.zeros_like(B_grid)

    for i, la in enumerate(lat_grid):
        for j, lo in enumerate(lon_grid):
            b, inc, dec = get_magnetic_field(la, lo)
            B_grid[i,j] = b
            U[i,j] = math.cos(math.radians(dec)) * math.cos(math.radians(inc))
            V[i,j] = math.sin(math.radians(dec)) * math.cos(math.radians(inc))

    fig, ax = plt.subplots(figsize=(8,5))
    c = ax.imshow(B_grid, extent=[-180,180,-80,80], origin='lower', cmap='plasma')
    plt.colorbar(c, ax=ax, label='Strength (nT)')  # 영어
    ax.quiver(lon_grid, lat_grid, U, V, color='white', scale=30)

    ax.plot(lon, lat, 'ro', markersize=10, label='Current location')  # 영어
    arrow_length = 20
    ax.arrow(lon, lat, arrow_length*math.cos(math.radians(D)), arrow_length*math.sin(math.radians(D)),
             color='red', width=1.5, head_width=6, head_length=8)
    ax.set_xlabel('Longitude (°)')  # 영어
    ax.set_ylabel('Latitude (°)')   # 영어
    ax.set_title('Global Magnetic Field + Highlighted Location')  # 영어
    ax.legend(loc='lower left')
    st.pyplot(fig)

st.info("빨간 점은 선택한 위치, 빨간 화살표는 해당 위치의 자기장 방향을 의미합니다. 색상 박스는 세기를 나타냅니다.")
