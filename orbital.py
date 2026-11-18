# orbital.py
import numpy as np

# Earth constants (no external dependency)
MU_EARTH = 3.986004418e14   # m^3/s^2
R_EARTH = 6_371_000.0


def compute_orbit(pos_m, vel_m_s):
    """
    Compute classical orbital elements from ECI position/velocity.
    Works for any bound or unbound orbit — no poliastro needed.
    """
    r = np.array(pos_m, dtype=float)
    v = np.array(vel_m_s, dtype=float)

    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)

    # Specific energy
    energy = 0.5 * v_mag**2 - MU_EARTH / r_mag

    # Specific angular momentum
    h = np.cross(r, v)
    h_mag = np.linalg.norm(h)

    # Semi-major axis
    if energy < 0:
        a = -MU_EARTH / (2 * energy)
    else:
        a = float('inf')  # parabolic / hyperbolic

    # Eccentricity vector
    e_vec = (np.cross(v, h) / MU_EARTH) - (r / r_mag)
    ecc = np.linalg.norm(e_vec)

    # Periapsis / apoapsis
    if ecc < 1.0 and a > 0:
        apogee_km = a * (1 + ecc) / 1000.0
        perigee_km = a * (1 - ecc) / 1000.0
        period_min = 2 * np.pi * np.sqrt(a**3 / MU_EARTH) / 60.0
    else:
        apogee_km = float('inf')
        perigee_km = a * (1 - ecc) / 1000.0 if a > 0 else 0.0
        period_min = float('inf')

    # Inclination
    inc_deg = np.rad2deg(np.arccos(h[2] / h_mag)) if h_mag > 0 else 0.0

    # Altitude summary
    alt_km = (r_mag - R_EARTH) / 1000.0

    return dict(
        altitude_km=round(alt_km, 2),
        apogee_km=round(apogee_km, 2) if np.isfinite(apogee_km) else 'inf',
        perigee_km=round(perigee_km, 2),
        period_min=round(period_min, 2) if np.isfinite(period_min) else 'inf',
        eccentricity=round(ecc, 5),
        inclination_deg=round(inc_deg, 2),
        energy_J_kg=round(energy, 2),
    )


def ecef_to_lla(pos):
    """ECEF (m) → (lat_deg, lon_deg, alt_m) — spherical approx."""
    x, y, z = pos
    lon = np.arctan2(y, x)
    p = np.hypot(x, y)
    lat = np.arctan2(z, p)
    alt = np.linalg.norm(pos) - R_EARTH
    return float(np.rad2deg(lat)), float(np.rad2deg(lon)), float(alt)