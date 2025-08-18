# Earth Magnetic Field Simulator (Realistic with WMM/IGRF via `geomag`)
# ---------------------------------------------------------------
# Requirements (add these to requirements.txt):
# streamlit
# numpy
# matplotlib
# geomag
#
# Run locally: streamlit run app_magnetic_field.py
# ---------------------------------------------------------------

import math
import datetime as dt
from typing import Tuple

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Try to use a realistic geomagnetic model via the `geomag` package (WMM/IGRF-like)
# If unavailable, fall back to a dipole approximation so the app still works.
try:
    from geomag import GeoMag  # type: ignore
    _GM = GeoMag()
    HAVE_GEOMAG = True
except Exception:
    _GM = None
    HAVE_GEOMAG = False

EARTH_RADIUS_KM = 6371.2  # reference radius used by many geomagnetic models

# -----------------------------
# Utilities
# -----------------------------

def decimal_year(date: dt.date) -> float:
    """Convert a datetime.date to a decimal year (e.g., 2025.62)."""
    start = dt.date(date.year, 1, 1)
    end = dt.date(date.year + 1, 1, 1)
    return date.year + (date - start).days / ((end - start).days)


def dipole_intensity_nT(lat_deg: float, alt_km: float, B0_equator_nT: float = 30000.0) -> float:
    """Very simple dipole magnitude model in nT as a fallback.
    B ~ B0 * sqrt(1 + 3 sin^2(lat)) / r^3, where r = (R_E + h)/R_E.
    """
    lat = math.radians(lat_deg)
    r = (EARTH_RADIUS_KM + alt_km) / EARTH_RADIUS_KM
    return B0_equator_nT * math.sqrt(1.0 + 3.0 * (math.sin(lat) ** 2)) / (r ** 3)


def dipole_inclination_deg(lat_deg: float) -> float:
    """Inclination I for an axial dipole: tan I = 2 tan(lat)."""
    lat = math.radians(lat_deg)
    I = math.atan2(2.0 * math.tan(lat), 1.0)
    return math.degrees(I)


def get_geomag(lat: float, lon: float, alt_km: float, date: dt.date):
    """Query the real model if available, else return dipole-like values.
    Returns dict with keys: dec (deg), inc (deg), total (nT), north (nT), east (nT), down (nT)
    """
    if HAVE_GEOMAG and _GM is not None:
        # GeoMag expects altitude in km, geodetic lat/lon in degrees.
        # Some versions accept a decimal year; others accept datetime.
        # We'll pass a decimal year to be safe.
        ydec = decimal_year(date)
        try:
            res = _GM.GeoMag(lat, lon, alt_km, time=ydec)
        except TypeError:
            # Some versions use named args differently
            res = _GM.GeoMag(lat, lon, alt_km, ydec)
        # Normalize field names across versions
        total = getattr(res, "t", None) or getattr(res, "ti", None)
        north = getattr(res, "x", None)
        east = getattr(res, "y", None)
        down = getattr(res, "z", None)
        dec = getattr(res, "dec", None) or getattr(res, "d", None)
        inc = getattr(res, "dip", None) or getattr(res, "i", None) or getattr(res, "inc", None)
        return {
            "dec": float(dec) if dec is not None else 0.0,
            "inc": float(inc) if inc is not None else 0.0,
            "total": float(total) if total is not None else 0.0,
            "north": float(north) if north is not None else 0.0,
            "east": float(east) if east is not None else 0.0,
            "down": float(down) if down is not None else 0.0,
        }
    # Fallback — simple dipole (no declination variation)
    B = dipole_intensity_nT(lat, alt_km)
    I = dipole_inclination_deg(lat)
    return {
        "dec": 0.0,        # axial dipole has zero declination in this simple 2D fallback
        "inc": I,
        "total": B,
        # horizontal components (approx)
        "north": B * math.cos(math.radians(I)),
        "east": 0.0,
        "down": B * math.sin(math.radians(I)),
    }


def compute_global_map(var: str, alt_km: float, date: dt.date, res_deg: int = 3) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute a global map for a chosen variable at given altitude/date.
    var in {"declination", "inclination", "intensity"}
    Returns (LON, LAT, DATA) grids.
    """
    lats = np.arange(-90, 90 + res_deg, res_deg)
    lons = np.arange(-180, 180 + res_deg, res_deg)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")  # LAT shape: (nlat, nlon)

    data = np.zeros_like(LAT, dtype=float)

    for i in range(LAT.shape[0]):
        for j in range(LAT.shape[1]):
            g = get_geomag(float(LAT[i, j]), float(LON[i, j]), alt_km, date)
            if var == "declination":
                data[i, j] = g["dec"]
            elif var == "inclination":
                data[i, j] = g["inc"]
            else:  # intensity
                data[i, j] = g["total"]

    return LON, LAT, data


def plot_global_map(lon_grid, lat_grid, value_grid, title: str, unit: str):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    im = ax.imshow(
        value_grid,
        extent=[-180, 180, -90, 90],
        origin="lower",
        aspect="auto",
        interpolation="nearest",
    )
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(unit)
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title(title)
    ax.grid(True, alpha=0.2)
    return fig


def plot_local_quiver(center_lat: float, center_lon: float, span_deg: float, alt_km: float, date: dt.date, step_deg: float = 5.0):
    lats = np.arange(center_lat - span_deg, center_lat + span_deg + 1e-6, step_deg)
    lons = np.arange(center_lon - span_deg, center_lon + span_deg + 1e-6, step_deg)
    LAT, LON = np.meshgrid(lats, lons, indexing="ij")
    north = np.zeros_like(LAT)
    east = np.zeros_like(LAT)

    for i in range(LAT.shape[0]):
        for j in range(LAT.shape[1]):
            g = get_geomag(float(LAT[i, j]), float(LON[i, j]), alt_km, date)
            north[i, j] = g["north"]
            east[i, j] = g["east"]

    # Normalize for quiver clarity
    mag = np.sqrt(north**2 + east**2) + 1e-9
    u = east / mag  # x-component (east)
    v = north / mag # y-component (north)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.quiver(LON, LAT, u, v, mag, scale=25, minlength=0.1)
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title("Local Horizontal Magnetic Field Direction (colored by |H|)")
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    return fig

# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(page_title="Earth Magnetic Field (IGRF/WMM)", layout="wide")
st.title("지구 자기장 시뮬레이터 — 현실적 모델 (WMM/IGRF)")

with st.sidebar:
    st.subheader("설정")
    date = st.date_input("날짜", value=dt.date.today())
    alt_km = st.slider("고도 (km)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
    res = st.select_slider("지도 해상도 (도)", options=[1, 2, 3, 5, 10], value=5)
    var = st.selectbox("지도 변수", ["intensity", "inclination", "declination"], index=0,
                       format_func=lambda x: {"intensity":"세기 (nT)","inclination":"경사각 (deg)","declination":"편각 (deg)"}[x])

    st.markdown("---")
    st.caption("📍 위치 선택 (정확한 값 보기)")
    user_lat = st.number_input("위도 (deg)", min_value=-90.0, max_value=90.0, value=37.5665, step=0.1)
    user_lon = st.number_input("경도 (deg)", min_value=-180.0, max_value=180.0, value=126.9780, step=0.1)

    st.markdown("---")
    st.caption("🧭 로컬 벡터 화살표")
    span = st.slider("주변 영역 (±deg)", 2.0, 30.0, 10.0, 1.0)
    step = st.select_slider("샘플 간격 (deg)", options=[1.0, 2.0, 5.0, 10.0], value=5.0)

    st.markdown("---")
    if HAVE_GEOMAG:
        st.success("실제 WMM/IGRF 모델 사용 중 (geomag)")
    else:
        st.warning("geomag 패키지를 찾을 수 없어 단순 쌍극자 근사를 사용합니다. requirements.txt에 'geomag'를 추가하세요.")

# 1) Global map
with st.spinner("전 지구 지도 계산 중..."):
    LON, LAT, DATA = compute_global_map(var, alt_km, date, res_deg=int(res))

unit = {"intensity": "nT", "inclination": "deg", "declination": "deg"}[var]
map_title = {
    "intensity": f"전 지구 자기장 세기 (고도 {alt_km:.0f} km, {date.isoformat()})",
    "inclination": f"전 지구 자기장 경사각 (고도 {alt_km:.0f} km, {date.isoformat()})",
    "declination": f"전 지구 자기장 편각 (고도 {alt_km:.0f} km, {date.isoformat()})",
}[var]

fig_map = plot_global_map(LON, LAT, DATA, map_title, unit)
st.pyplot(fig_map, use_container_width=True)

# 2) Exact values at user point
g = get_geomag(user_lat, user_lon, alt_km, date)
col1, col2, col3, col4 = st.columns(4)
col1.metric("세기 |B| (nT)", f"{g['total']:.0f}")
col2.metric("경사각 I (deg)", f"{g['inc']:.1f}")
col3.metric("편각 D (deg)", f"{g['dec']:.1f}")
col4.metric("수직성분 Down (nT)", f"{g['down']:.0f}")

st.caption("참고: 경사각 I>0 이면 아래쪽(지표로) 향함. 편각 D>0 이면 동쪽으로 치우침.")

# 3) Local horizontal field arrows (quiver)
with st.spinner("로컬 벡터 계산 중..."):
    fig_quiver = plot_local_quiver(user_lat, user_lon, span, alt_km, date, step_deg=float(step))
st.pyplot(fig_quiver, use_container_width=True)

st.markdown("---")
st.markdown(
    """
**설명**  
- 이 앱은 기본적으로 `geomag` 패키지를 사용해 월드 자기장 모델(WMM/IGRF 계열)을 질의합니다.  
- 전 지구 지도는 위도/경도 격자에서 각 지점의 자기장 변수를 계산해 그립니다.  
- `geomag`가 설치되지 않은 경우, 물리 수업용으로 널리 쓰는 **쌍극자 근사**로 대체 계산합니다 (현실성과 정확도는 낮아집니다).  

**정확도를 높이려면**  
- `requirements.txt`에 `geomag`를 추가해 주세요.  
- 더 최신 계수(예: 최신 WMM/IGRF)를 쓰고 싶다면, 해당 패키지 버전을 최신으로 유지하세요.
    """
)
