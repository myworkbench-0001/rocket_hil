# comms.py
import socket, json, threading
import numpy as np
import config as C


class HILComms:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind(("0.0.0.0", C.UDP_PORT))
        except OSError as e:
            print("UDP bind failed (continuing in sim-only mode):", e)
        self.sock.settimeout(0.001)
        self.latest_fins = np.zeros(4)
        self.running = True
        self.thread = threading.Thread(target=self._rx_loop, daemon=True)
        self.thread.start()

    def _rx_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                pkt = json.loads(data.decode())
                if 'fins' in pkt:
                    self.latest_fins = np.array(pkt['fins'], dtype=float)
            except socket.timeout:
                pass
            except Exception:
                pass

    def send_state(self, t, pos, vel, quat, omega):
        alt = np.linalg.norm(pos) - C.R_EARTH
        v = np.linalg.norm(vel)
        pkt = {
            "t": round(float(t), 3),
            "quat": [round(float(x), 4) for x in quat],
            "omega": [round(float(x), 4) for x in omega],
            "alt": round(float(alt), 1),
            "vel": round(float(v), 2),
        }
        try:
            self.sock.sendto(
                json.dumps(pkt).encode(), (C.ESP32_IP, C.UDP_PORT)
            )
        except Exception:
            pass

    def stop(self):
        self.running = False