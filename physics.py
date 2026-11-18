# physics.py — only the changed functions
import numpy as np
from scipy.spatial.transform import Rotation as R
from atmosphere import atmosphere
import config as C

G0 = 9.80665


def thrust_at(t):
    if 0 <= t < C.ROCKET['burn_time']:
        return C.ROCKET['thrust']
    return 0.0


def mass_at(t):
    m0 = C.ROCKET['dry_mass'] + C.ROCKET['prop_mass']
    if t < C.ROCKET['burn_time']:
        mdot = C.ROCKET['thrust'] / (C.ROCKET['Isp'] * G0)
        return max(m0 - mdot * t, C.ROCKET['dry_mass'])
    return C.ROCKET['dry_mass']


def gravity_vector(pos):
    r = np.linalg.norm(pos)
    if r < 1.0:
        return np.zeros(3)
    return -C.G * C.M_EARTH * pos / r**3


def aerodynamics(state, fin_deg):
    pos = state['pos']; vel = state['vel']
    alt = np.linalg.norm(pos) - C.R_EARTH
    rho, _, _ = atmosphere(alt)

    v_mag = np.linalg.norm(vel)
    if v_mag < 1e-3:
        return np.zeros(3), np.zeros(3)

    q_dyn = 0.5 * rho * v_mag**2
    F_drag = -q_dyn * C.ROCKET['Cd'] * C.ROCKET['area'] * (vel / v_mag)

    q_dyn_fin = q_dyn * C.ROCKET['fin_area'] * 1.5
    pitch_force = q_dyn_fin * np.deg2rad(fin_deg[0] - fin_deg[2])
    yaw_force   = q_dyn_fin * np.deg2rad(fin_deg[1] - fin_deg[3])

    rot = R.from_quat(state['quat'])
    body_force = np.array([0.0, pitch_force, yaw_force])
    F_control = rot.apply(body_force)

    M = np.array([
        0.0,
        pitch_force * C.ROCKET['fin_arm'],
        yaw_force   * C.ROCKET['fin_arm'],
    ])

    return F_drag + F_control, M


def derivatives(t, y, fin_deg):
    pos = y[0:3]; vel = y[3:6]
    quat = y[6:10]; omega = y[10:13]

    m = mass_at(t)
    rot = R.from_quat(quat)

    F_thrust = rot.apply([thrust_at(t), 0, 0])
    F_grav = gravity_vector(pos) * m
    F_aero, M_aero = aerodynamics(
        {'pos': pos, 'vel': vel, 'quat': quat, 'omega': omega}, fin_deg)

    F_total = F_thrust + F_grav + F_aero
    a = F_total / m

    I = C.ROCKET['inertia']
    domega = np.linalg.solve(I, M_aero - np.cross(omega, I @ omega))

    p, q, r = omega
    dquat = 0.5 * np.array([
        -p*quat[1] - q*quat[2] - r*quat[3],
         p*quat[0] + r*quat[2] - q*quat[3],
         q*quat[0] - r*quat[1] + p*quat[3],
         r*quat[0] + q*quat[1] - p*quat[2],
    ])

    return np.concatenate([vel, a, dquat, domega])


def initial_state():
    lat = np.deg2rad(C.LAUNCH_LAT)
    lon = np.deg2rad(C.LAUNCH_LON)
    r = C.R_EARTH + C.LAUNCH_ALT
    pos = np.array([
        r*np.cos(lat)*np.cos(lon),
        r*np.cos(lat)*np.sin(lon),
        r*np.sin(lat),
    ])
    up = pos / np.linalg.norm(pos)
    x = np.array([1, 0, 0])
    v = np.cross(x, up)
    s = np.linalg.norm(v)
    c = np.dot(x, up)
    if s < 1e-6:
        quat = np.array([1.0, 0.0, 0.0, 0.0])
    else:
        axis = v / s
        ang = np.arctan2(s, c)
        quat = np.concatenate([[np.cos(ang/2)], axis*np.sin(ang/2)])
    return np.concatenate([pos, [0, 0, 0], quat, [0, 0, 0]])