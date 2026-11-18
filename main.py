# main.py
import sys
import numpy as np
from scipy.integrate import solve_ivp

from PyQt5 import QtWidgets, QtCore
from pyvistaqt import QtInteractor

import config as C
import physics
from comms import HILComms
from globe3d import Globe3D
from dashboard import Dashboard
from orbital import compute_orbit, ecef_to_lla


class Simulator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIL Active Fin Rocket — 3D Simulator")
        self.resize(1600, 900)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        # 3D globe (QtInteractor — snake_case API)
        self.plotter = QtInteractor(central)
        self.plotter.set_background("black")   # ✅ FIX: snake_case
        layout.addWidget(self.plotter.interactor, 3)
        self.globe = Globe3D(self.plotter)

        # Dashboard
        self.dash = Dashboard()
        layout.addWidget(self.dash, 2)

        # State
        self.state = physics.initial_state()
        self.t = 0.0
        self.comms = HILComms()
        self.orbit_computed = False

        # 50 Hz timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.start(int(C.DT * 1000))

    def step(self):
        fins = self.comms.latest_fins

        try:
            sol = solve_ivp(
                lambda t, y: physics.derivatives(t, y, fins),
                [self.t, self.t + C.DT],
                self.state,
                method='RK45', rtol=1e-6, atol=1e-8,
            )
            self.state = sol.y[:, -1]
        except Exception as e:
            print("Physics integration error:", e)
            return

        self.t += C.DT
        pos = self.state[0:3]
        vel = self.state[3:6]
        quat = self.state[6:10]
        omega = self.state[10:13]

        self.comms.send_state(self.t, pos, vel, quat, omega)

        lat, lon, alt = ecef_to_lla(pos)
        v_mag = np.linalg.norm(vel)

        self.dash.update(self.t, alt, v_mag, fins, lat, lon)
        self.globe.update(pos)

        if not self.orbit_computed and alt > 100_000:
            info = compute_orbit(pos, vel)
            print("ORBITAL ELEMENTS:", info)
            self.orbit_computed = True

    def closeEvent(self, event):
        self.comms.stop()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = Simulator()
    win.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()