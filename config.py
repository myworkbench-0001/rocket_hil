# config.py
import numpy as np

R_EARTH = 6_371_000.0
G = 6.67430e-11
M_EARTH = 5.972e24

LAUNCH_LAT = 7.8731
LAUNCH_LON = 80.7718
LAUNCH_ALT = 0.0
LAUNCH_AZIMUTH = 90.0

ROCKET = dict(
    dry_mass=50.0,
    prop_mass=150.0,
    Isp=200.0,
    thrust=8000.0,
    burn_time=20.0,
    Cd=0.5,
    area=np.pi * 0.15**2,
    fin_area=0.01,
    fin_arm=0.35,
    max_fin_deg=20.0,
    inertia=np.diag([0.5, 5.0, 5.0]),
)

DT = 0.02
UDP_PORT = 5005
ESP32_IP = "192.168.4.1"