# Earth Magnetic Field Simulator — Visualized Version
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
st.title("🧲 지구 자기장 시각화")

st.write("""
세계 어느 위치든 자기장의 세기·경사각·편각을 숫자와 시각화로 볼 수 있습니다.
""")

lat = st.slider("위도", -90.0, 90.0, 37.5, step=0.1)
lon = st.slider("경도", -180.0, 180.0, 127.0, step=0.1)

B, I, D = get_magnetic_field(lat, lon)

st.subheader("현재 위치 자기장")
st.metric("세기 (nT)", f"{B:.0f}")
st.metric("경사각 (°)", f"{I:.1f}")
st.metric("편각 (°)", f"{D:.1f}")

# Global field visualization (intensity + direction)
lat_grid = np.linspace(-80,80,21)
lon_grid = np.linspace(-180,180,37)
B_grid = np.zeros((len(lat_grid), len(lon_grid)))
U = np.zeros_like(B_grid)
V = np.zeros_like(B_grid)

for i, la in enumerate(lat_grid):
    for j, lo in enumerate(lon_grid):
        b, inc, dec = get_magnetic_field(la, lo)
        B_grid[i,j] = b
        # direction arrows: simple horizontal projection
        U[i,j] = math.cos(math.radians(dec)) * math.cos(math.radians(inc))
        V[i,j] = math.sin(math.radians(dec)) * math.cos(math.radians(inc))

fig, ax = plt.subplots(figsize=(10,5))
c = ax.imshow(B_grid, extent=[-180,180,-80,80], origin='lower', cmap='plasma')
plt.colorbar(c, ax=ax, label='세기 (nT)')
ax.quiver(lon_grid, lat_grid, U, V, color='white', scale=30)
ax.set_xlabel('경도 (°)')
ax.set_ylabel('위도 (°)')
ax.set_title('전 지구 자기장 세기 + 방향')
st.pyplot(fig)

st.info("색은 자기장의 세기, 흰 화살표는 수평 방향을 나타냅니다.")
