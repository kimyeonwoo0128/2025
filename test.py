# Earth Magnetic Field Simulator — Enhanced Visualization
# -----------------------------------------------------------
# Requirements (requirements.txt):
# streamlit
# numpy
# matplotlib
# geomag (optional)
# -----------------------------------------------------------

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

st.set_page_config(page_title="지구 자기장 보기", layout="wide")
st.title("🧲 지구 자기장 시각화 (강화 버전)")

st.write("위도를 조정하면 지도 위에 위치가 표시되고, 자기장의 방향과 세기가 강조됩니다.")

# Layout: side-by-side
col1, col2 = st.columns([1,2])

with col1:
    lat = st.slider("위도", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("경도", -180.0, 180.0, 127.0, step=0.1)

    B, I, D = get_magnetic_field(lat, lon)

    st.subheader("현재 위치 자기장")
    st.metric("세기 (nT)", f"{B:.0f}")
    st.metric("경사각 (°)", f"{I:.1f}")
    st.metric("편각 (°)", f"{D:.1f}")

    # 색상 박스로 세기 강조
    st.markdown(f"<div style='padding:10px; background-color:rgb({int(min(B/60000*255,255))},0,{int(255-min(B/60000*255,255))}); color:white;'>현재 세기 색상</div>", unsafe_allow_html=True)

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
    plt.colorbar(c, ax=ax, label='세기 (nT)')
    ax.quiver(lon_grid, lat_grid, U, V, color='white', scale=30)

    # 현재 위치 점 표시
    ax.plot(lon, lat, 'ro', markersize=10, label='현재 위치')
    # 현재 위치 화살표 강조
    arrow_length = 20
    ax.arrow(lon, lat, arrow_length*math.cos(math.radians(D)), arrow_length*math.sin(math.radians(D)),
             color='red', width=1.5, head_width=6, head_length=8)
    ax.set_xlabel('경도 (°)')
    ax.set_ylabel('위도 (°)')
    ax.set_title('전 지구 자기장 + 현재 위치 강조')
    ax.legend(loc='lower left')
    st.pyplot(fig)

st.info("빨간 점은 선택한 위치, 빨간 화살표는 해당 지점의 자기장 방향을 나타냅니다. 색상 박스는 세기 변화를 직관적으로 표현합니다.")
