import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from igrf import igrf_value
import math

st.set_page_config(page_title="지구 자기장 (IGRF)", layout="wide")
st.title("🧲 지구 자기장 시각화 (IGRF 기반)")

st.write("위도와 경도를 조절하면 해당 위치의 실제 지구 자기장을 IGRF13 모델로 계산합니다.")

col1, col2 = st.columns([1,2])

# --- 사용자 입력 ---
with col1:
    lat = st.slider("위도", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("경도", -180.0, 180.0, 127.0, step=0.1)
    alt = st.slider("고도 (km)", 0.0, 1000.0, 0.0, step=10.0)

    # 현재 시각 연도 사용 (2025.0)
    year = 2025.0
    Bx, By, Bz, Bh, ti, dec, dip = igrf_value(lat, lon, alt, year)
    # ti: total intensity [nT], dec: declination, dip: inclination

    st.subheader("선택한 위치의 자기장 (IGRF13)")
    st.metric("세기 (nT)", f"{ti:.0f}")
    st.metric("경사각 (°)", f"{dip:.1f}")
    st.metric("편각 (°)", f"{dec:.1f}")

    st.markdown(
        f"<div style='padding:10px; background-color:rgb({int(min(ti/60000*255,255))},0,{int(255-min(ti/60000*255,255))}); color:white;'>세기 색상 표시</div>", 
        unsafe_allow_html=True
    )

# --- 전세계 자기장 시각화 ---
with col2:
    lat_grid = np.linspace(-80, 80, 21)
    lon_grid = np.linspace(-180, 180, 37)
    B_grid = np.zeros((len(lat_grid), len(lon_grid)))
    U = np.zeros_like(B_grid)
    V = np.zeros_like(B_grid)

    for i, la in enumerate(lat_grid):
        for j, lo in enumerate(lon_grid):
            bx, by, bz, bh, ti_, dec_, dip_ = igrf_value(la, lo, alt, year)
            B_grid[i, j] = ti_
            U[i, j] = math.cos(math.radians(dec_)) * math.cos(math.radians(dip_)
)
            V[i, j] = math.sin(math.radians(dec_)) * math.cos(math.radians(dip_)
)

    fig, ax = plt.subplots(figsize=(8,5))
    c = ax.imshow(B_grid, extent=[-180,180,-80,80], origin='lower', cmap='plasma')
    plt.colorbar(c, ax=ax, label='Strength (nT)')
    ax.quiver(lon_grid, lat_grid, U, V, color='white', scale=30)
    ax.plot(lon, lat, 'ro', markersize=10, label='Current location')
    arrow_length = 20
    ax.arrow(lon, lat, arrow_length*math.cos(math.radians(dec)), arrow_length*math.sin(math.radians(dec)),
             color='red', width=1.5, head_width=6, head_length=8)
    ax.set_xlabel('Longitude (°)')
    ax.set_ylabel('Latitude (°)')
    ax.set_title('Earth Magnetic Field (IGRF13)')
    ax.legend(loc='lower left')
    st.pyplot(fig)

st.info("빨간 점은 선택한 위치, 빨간 화살표는 해당 위치의 자기장 방향을 의미합니다. 색상은 세기를 나타냅니다.")
