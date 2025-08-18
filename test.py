# Earth Magnetic Field Simulator — Easy Version for Beginners
# -----------------------------------------------------------
# Requirements (requirements.txt):
# streamlit
# numpy
# matplotlib
# geomag (optional, for real WMM/IGRF)
# -----------------------------------------------------------

import math
import datetime as dt
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Optional: Use real geomagnetic model if available
try:
    from geomag import GeoMag
    GM = GeoMag()
    HAVE_GEOMAG = True
except Exception:
    GM = None
    HAVE_GEOMAG = False

# --- Helper Functions ---
def get_magnetic_field(lat, lon):
    if HAVE_GEOMAG and GM is not None:
        res = GM.GeoMag(lat, lon)
        return res.ti, res.dip, res.dec  # total intensity, inclination, declination
    # Simple fallback (approximate dipole)
    B = 30000 * math.sqrt(1+3*(math.sin(math.radians(lat))**2))
    I = math.degrees(math.atan2(2*math.tan(math.radians(lat)),1))
    return B, I, 0.0

# --- Streamlit App ---
st.set_page_config(page_title="지구 자기장 보기", layout="wide")
st.title("🧭 지구 자기장 시뮬레이터 (쉬운 버전)")

st.write("""
이 앱은 전 세계 어디서나 **자기장의 세기(nT)**, **경사각(지표를 향하는 각도)**, **편각(동서 방향으로 치우친 각도)**를 간단히 확인할 수 있습니다.  
**geomag** 라이브러리가 있으면 실제 WMM/IGRF 모델을 사용하고, 없으면 기본 근사값을 보여줍니다.
""")

lat = st.slider("위도 (남극 -90° ~ 북극 90°)", -90.0, 90.0, 37.5, step=0.1)
lon = st.slider("경도 (서쪽 -180° ~ 동쪽 180°)", -180.0, 180.0, 127.0, step=0.1)

B, I, D = get_magnetic_field(lat, lon)

st.subheader("현재 위치의 자기장")
st.metric("세기 (nT)", f"{B:.0f}")
st.metric("경사각 (°)", f"{I:.1f}")
st.metric("편각 (°)", f"{D:.1f}")

st.write("""
- **세기**: 자기장의 크기 (숫자가 클수록 강함)  
- **경사각**: 나침반 바늘이 지표를 향하는 기울기  
- **편각**: 진북과 자기북의 차이 (양수 = 동쪽으로 치우침)
""")

# Quick global map
grid_lat = np.linspace(-90,90,19)
grid_lon = np.linspace(-180,180,37)
DATA = np.zeros((len(grid_lat), len(grid_lon)))
for i, la in enumerate(grid_lat):
    for j, lo in enumerate(grid_lon):
        b,_,_ = get_magnetic_field(la,lo)
        DATA[i,j] = b

fig, ax = plt.subplots(figsize=(8,4))
c = ax.imshow(DATA, extent=[-180,180,-90,90], origin='lower', cmap='plasma')
plt.colorbar(c, ax=ax, label='세기 (nT)')
ax.set_xlabel('경도 (°)')
ax.set_ylabel('위도 (°)')
ax.set_title('전 지구 자기장 세기 (간단 지도)')
st.pyplot(fig)

st.info("슬라이더를 움직여 위도/경도를 바꾸면 즉시 값이 업데이트됩니다!")
