import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import math

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="지구 자기장 (근사 모델)", layout="wide")
st.title("🧲 지구 자기장 시각화 (간단 근사)")

st.write("**위도/경도/고도**를 조절하면 단순한 경사 이중극자 모델로 계산한 자기장을 보여줍니다.")
st.write("이 모델은 실제 IGRF13 모델보다 단순하지만 설치 없이 실행됩니다.")

# --- 사용자 입력 ---
col1, col2 = st.columns([1, 2])

with col1:
    lat = st.slider("위도 (°)", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("경도 (°)", -180.0, 180.0, 127.0, step=0.1)
    alt = st.slider("고도 (km)", 0.0, 1000.0, 0.0, step=10.0)

    # 지구 자기장 dipole 근사 (경사축 11°)
    B0 = 30000  # nT (지표면 평균 자기장 세기)
    tilt = math.radians(11)
    colat = math.radians(90 - lat)
    # 단순 위도/경도 변화 (약간의 경사 포함)
    B = B0 * (1 + 0.3 * math.sin(colat) * math.cos(math.radians(lon)))

    # 경사각(자기장 방향) 단순 근사
    dip = 90 - lat + math.degrees(tilt) * math.cos(math.radians(lon))
    dec = 0.0  # 편각은 단순화

    st.subheader("선택한 위치의 자기장 (근사값)")
    st.metric("세기 (nT)", f"{B:.0f}")
    st.metric("경사각 (°)", f"{dip:.1f}")
    st.metric("편각 (°)", f"{dec:.1f}")

    # 색상으로 세기 표시
    st.markdown(
        f"<div style='padding:10px; background-color:rgb({int(min(B/60000*255,255))},0,{int(255-min(B/60000*255,255))}); color:white;'>"
        f"세기 색상 표시</div>", 
        unsafe_allow_html=True
    )

with col2:
    # 전세계 자기장 세기 맵
    lat_grid = np.linspace(-80, 80, 41)
    lon_grid = np.linspace(-180, 180, 73)
    B_grid = np.zeros((len(lat_grid), len(lon_grid)))

    for i, la in enumerate(lat_grid):
        for j, lo in enumerate(lon_grid):
            colat = math.radians(90 - la)
            B_grid[i, j] = B0 * (1 + 0.3 * math.sin(colat) * math.cos(math.radians(lo)))

    fig, ax = plt.subplots(figsize
