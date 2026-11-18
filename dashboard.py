# dashboard.py
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets


class Dashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rocket HIL — Telemetry")
        self.resize(900, 600)

        layout = QtWidgets.QGridLayout(self)

        self.alt_plot = pg.PlotWidget(title="Altitude (m)")
        self.vel_plot = pg.PlotWidget(title="Velocity (m/s)")
        self.fin_plot = pg.PlotWidget(title="Fin angles (°)")
        self.traj_plot = pg.PlotWidget(title="Ground track (lat/lon)")

        self.alt_curve = self.alt_plot.plot(pen='c')
        self.vel_curve = self.vel_plot.plot(pen='y')
        self.fin_curves = [
            self.fin_plot.plot(pen=c) for c in ('r', 'g', 'b', 'm')
        ]
        self.traj_curve = self.traj_plot.plot(pen='w')

        for i, w in enumerate([self.alt_plot, self.vel_plot, self.fin_plot]):
            layout.addWidget(w, 0, i)
        layout.addWidget(self.traj_plot, 1, 0, 1, 3)

        self.t_data, self.alt_data, self.vel_data = [], [], []
        self.fin_data = [[], [], [], []]
        self.lat_data, self.lon_data = [], []

    def update(self, t, alt, vel, fins, lat, lon):
        self.t_data.append(t)
        self.alt_data.append(alt)
        self.vel_data.append(vel)
        for i in range(4):
            self.fin_data[i].append(fins[i])
        self.lat_data.append(lon)   # X = lon
        self.lon_data.append(lat)   # Y = lat

        N = 3000
        self.alt_curve.setData(self.t_data[-N:], self.alt_data[-N:])
        self.vel_curve.setData(self.t_data[-N:], self.vel_data[-N:])
        for i in range(4):
            self.fin_curves[i].setData(self.t_data[-N:], self.fin_data[i][-N:])
        self.traj_curve.setData(self.lat_data[-N:], self.lon_data[-N:])