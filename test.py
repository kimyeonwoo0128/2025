import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

# --- 페이지 설정 ---
st.set_page_config(page_title="지구 자기장 시각화", layout="wide")
st.title("🧲 지구 자기장 시각화")

# --- 사용자 입력 ---
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("위치 설정")
    lat = st.slider("위도 (°)", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("경도 (°)", -180.0, 180.0, 127.0, step=0.1)
    alt = st.slider("고도 (km)", 0.0, 1000.0, 0.0, step=10.0)

# --- 좌표 변환 ---
R = 1.0
lat_r = np.radians(lat)
lon_r = np.radians(lon)
x_pos = (R + alt/6371) * np.cos(lat_r) * np.cos(lon_r)
y_pos = (R + alt/6371) * np.cos(lat_r) * np.sin(lon_r)
z_pos = (R + alt/6371) * np.sin(lat_r)

# --- Dipole 자기장 계산 ---
def dipole_field(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    m = np.array([0, 0, 1])
    r_vec = np.array([x, y, z])
    dot = np.dot(m, r_vec)
    B = (3 * dot * r_vec / r**5) - (m / r**3)
    return B

# --- 지구 표면 ---
phi, theta = np.mgrid[0:2*np.pi:30j, 0:np.pi:15j]
xs = R * np.cos(phi) * np.sin(theta)
ys = R * np.sin(phi) * np.sin(theta)
zs = R * np.cos(theta)

# --- 3D 플롯 ---
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(xs, ys, zs, color='b', alpha=0.3)

# --- 자기장 벡터 계산 ---
xg, yg, zg, u, v, w, colors = [], [], [], [], [], [], []
grid = np.linspace(-2, 2, 7)
B_magnitudes = []

# 먼저 모든 B 크기 계산
for xi in grid:
    for yi in grid:
        for zi in grid:
            r = np.sqrt(xi**2 + yi**2 + zi**2)
            if 0.8 < r < 2.0:
                B = dipole_field(xi, yi, zi)
                B_magnitudes.append(np.linalg.norm(B))

B_max = max(B_magnitudes)

# 다시 벡터 생성 (색상 + 길이 반영)
for xi in grid:
    for yi in grid:
        for zi in grid:
            r = np.sqrt(xi**2 + yi**2 + zi**2)
            if 0.8 < r < 2.0:
                B = dipole_field(xi, yi, zi)
                strength = np.linalg.norm(B)
                scale = 0.5  # 길이 조절
                B_scaled = B * scale
                xg.append(xi); yg.append(yi); zg.append(zi)
                u.append(B_scaled[0]); v.append(B_scaled[1]); w.append(B_scaled[2])
                colors.append(cm.viridis(strength / B_max))  # 색상

# --- 자기장 화살표 ---
ax.quiver(xg, yg, zg, u, v, w, color=colors, alpha=0.9)

# --- 현재 위치 표시 ---
ax.scatter(x_pos, y_pos, z_pos, color='r', s=100, label='Current Location')

# --- 축 설정 ---
ax.set_xlim([-2, 2]); ax.set_ylim([-2, 2]); ax.set_zlim([-2, 2])
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax.set_title("Earth with Magnetic Dipole Field")
ax.legend()

# --- Streamlit 출력 ---
with col2:
    st.pyplot(fig)

# --- 현재 위치 자기장 세기 표시 ---
B_current = dipole_field(x_pos, y_pos, z_pos)
B_strength = np.linalg.norm(B_current)
st.metric(label="현재 위치 자기장 세기", value=f"{B_strength:.3f}")

# --- 시각화 설명 (쉼표 구분) ---
st.info(
    "화살표 길이와 색깔 = 자기장 세기, 길고 진한 색 = 강한 자기장, 짧고 연한 색 = 약한 자기장, 파란 구 = 지구, 빨간 점 = 현재 선택 위치"
)
