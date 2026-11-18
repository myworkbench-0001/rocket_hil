# atmosphere.py
import numpy as np

def atmosphere(h_m):
    """
    International Standard Atmosphere (0–86 km).
    Returns: rho (kg/m^3), P (Pa), T (K)
    """
    if h_m < 0:
        h_m = 0.0
    h = h_m / 1000.0  # km

    if h < 11:      # Troposphere
        T = 288.15 - 6.5*h
        P = 101325.0 * (T/288.15)**5.2559
    elif h < 20:    # Lower stratosphere
        T = 216.65
        P = 22632.0 * np.exp(-0.1577*(h-11))
    elif h < 32:    # Upper stratosphere
        T = 216.65 + (h-20)
        P = 5474.9 * (T/216.65)**(-34.16)
    elif h < 47:
        T = 228.65 + 2.8*(h-32)
        P = 868.02 * (T/228.65)**(-12.20)
    elif h < 51:
        T = 270.65
        P = 110.91 * np.exp(-0.1262*(h-47))
    elif h < 71:
        T = 270.65 - 2.8*(h-51)
        P = 66.94 * (T/270.65)**11.39
    elif h < 86:
        T = 214.65 - 2.0*(h-71)
        P = 3.956 * (T/214.65)**17.08
    else:           # Thermosphere (approx)
        T = 186.0 + (h-86)*0.05
        P = 0.373 * np.exp(-(h-86)/7.0)

    rho = P / (287.05 * T)
    return rho, P, T

def speed_of_sound(h_m):
    _, _, T = atmosphere(h_m)
    return np.sqrt(1.4 * 287.05 * T)