import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

# --- 페이지 설정 (프로그램 이름 반영) ---
st.set_page_config(page_title="지구 자기장 시뮬레이터", layout="wide")
st.title("🧲 지구 자기장 시뮬레이터")

st.write("지구와 지구 자기장을 3D로 시각화합니다. 위도·경도·고도를 조절해 현재 위치를 확인하세요.")

# --- 레이아웃 구성 (좌측: 입력 / 우측: 그래프) ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("위치 설정")
    lat = st.slider("위도 (°)", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("경도 (°)", -180.0, 180.0, 127.0, step=0.1)
    alt = st.slider("고도 (km)", 0.0, 1000.0, 0.0, step=10.0)

# --- 지구 좌표 변환 (위도, 경도 → 3D 좌표) ---
R = 1.0  # 지구 반지름을 1로 정규화
lat_r = np.radians(lat)
lon_r = np.radians(lon)
x_pos = (R + alt/6371) * np.cos(lat_r) * np.cos(lon_r)
y_pos = (R + alt/6371) * np.cos(lat_r) * np.sin(lon_r)
z_pos = (R + alt/6371) * np.sin(lat_r)

# --- Dipole 자기장 계산 ---
def dipole_field(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    m = np.array([0, 0, 1])  # dipole along z-axis
    r_vec = np.array([x, y, z])
    dot = np.dot(m, r_vec)
    B = (3 * dot * r_vec / r**5) - (m / r**3)
    return B

# --- 지구 표면 생성 ---
phi, theta = np.mgrid[0:2*np.pi:30j, 0:np.pi:15j]
xs = R * np.cos(phi) * np.sin(theta)
ys = R * np.sin(phi) * np.sin(theta)
zs = R * np.cos(theta)

# --- 3D 플롯 ---
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(xs, ys, zs, color='b', alpha=0.3)  # 지구 구체

# 자기장 벡터 샘플링
u, v, w = [], [], []
xg, yg, zg = [], [], []
grid = np.linspace(-2, 2, 7)
for xi in grid:
    for yi in grid:
        for zi in grid:
            if 0.8 < np.sqrt(xi**2 + yi**2 + zi**2) < 2.0:
                B = dipole_field(xi, yi, zi)
                xg.append(xi); yg.append(yi); zg.append(zi)
                u.append(B[0]); v.append(B[1]); w.append(B[2])

# 자기장 벡터필드 (시각화 텍스트는 영어 유지)
ax.quiver(xg, yg, zg, u, v, w, length=0.3, normalize=True, color='orange', alpha=0.7)

# 현재 선택 위치 표시
ax.scatter(x_pos, y_pos, z_pos, color='r', s=100, label='Current Location')

# 축과 스타일 (영어)
ax.set_xlim([-2, 2]); ax.set_ylim([-2, 2]); ax.set_zlim([-2, 2])
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title("Earth with Magnetic Dipole Field")
ax.legend()

with col2:
    st.pyplot(fig)
    st.info("주황색 화살표: 지구 자기장 방향 / 파란 구: 지구 / 빨간 점: 현재 위치")
