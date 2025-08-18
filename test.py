import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("지구 자기장 시뮬레이터 (Dipole Field)")

# 사용자 입력
angle_deg = st.slider("자기모멘트 각도 (도)", 0, 180, 0)
strength = st.slider("자기모멘트 세기", 1, 10, 5)

# 각도 → 라디안
angle_rad = np.deg2rad(angle_deg)
m = np.array([strength*np.cos(angle_rad), strength*np.sin(angle_rad)])  # 2D 모멘트

# 격자 생성
x = np.linspace(-2, 2, 40)
z = np.linspace(-2, 2, 40)
X, Z = np.meshgrid(x, z)
R = np.sqrt(X**2 + Z**2)

# dipole field 계산 (2D 근사)
Bx = (3*X*(m[0]*X + m[1]*Z)/R**5 - m[0]/R**3)
Bz = (3*Z*(m[0]*X + m[1]*Z)/R**5 - m[1]/R**3)

# 중심(0,0) 값은 NaN → 0으로 처리
Bx[R == 0] = 0
Bz[R == 0] = 0

# 시각화
fig, ax = plt.subplots(figsize=(6,6))
ax.streamplot(X, Z, Bx, Bz, color=np.log(np.sqrt(Bx**2+Bz**2)), cmap='plasma')
circle = plt.Circle((0,0), 0.2, color='blue')  # 지구 표시
ax.add_artist(circle)
ax.set_title("지구 자기장 (Dipole Approximation)")
ax.set_xlabel("x (지구 반경)")
ax.set_ylabel("z (지구 반경)")
ax.set_aspect('equal')

st.pyplot(fig)
