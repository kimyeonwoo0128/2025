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

st.set_page_config(page_title="Earth Magnetic Field", layout="wide")
st.title("🧲 Earth Magnetic Field Visualization (Enhanced)")

st.write("Adjust latitude and longitude. The map will highlight the location and show the magnetic field direction and strength.")

# Layout: side-by-side
col1, col2 = st.columns([1,2])

with col1:
    lat = st.slider("Latitude", -90.0, 90.0, 37.5, step=0.1)
    lon = st.slider("Longitude", -180.0, 180.0, 127.0, step=0.1)

    B, I, D = get_magnetic_field(lat, lon)

    st.subheader("Magnetic Field at Location")
    st.metric("Strength (nT)", f"{B:.0f}")
    st.metric("Inclination (°)", f"{I:.1f}")
    st.metric("Declination (°)", f"{D:.1f}")

    # Color box for field strength
    st.markdown(f"<div style='padding:10px; background-color:rgb({int(min(B/60000*255,255))},0,{int(255-min(B/60000*255,255))}); color:white;'>Field strength color</div>", unsafe_allow_html=True)

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
    plt.colorbar(c, ax=ax, label='Strength (nT)')
    ax.quiver(lon_grid, lat_grid, U, V, color='white', scale=30)

    # Current location marker
    ax.plot(lon, lat, 'ro', markersize=10, label='Current location')
    # Highlight arrow for current location
    arrow_length = 20
    ax.arrow(lon, lat, arrow_length*math.cos(math.radians(D)), arrow_length*math.sin(math.radians(D)),
             color='red', width=1.5, head_width=6, head_length=8)
    ax.set_xlabel('Longitude (°)')
    ax.set_ylabel('Latitude (°)')
    ax.set_title('Global Magnetic Field + Highlighted Location')
    ax.legend(loc='lower left')
    st.pyplot(fig)

st.info("The red dot shows the selected location. The red arrow indicates the field direction. The color box reflects field strength.")
