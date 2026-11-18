# globe3d.py
import numpy as np
import pyvista as pv

# Offline Earth texture (bundled cache). If not available → blue sphere.
try:
    from pyvista import examples
    EARTH_TEXTURE = examples.download_globe_texture()
except Exception:
    EARTH_TEXTURE = None


class Globe3D:
    def __init__(self, plotter, scale=1e-6):
        self.p = plotter
        self.scale = scale
        self.traj_points = []
        self.traj_actor = None
        self.marker_actor = None

        # Earth sphere
        earth = pv.Sphere(
            radius=6_371_000 * scale,
            theta_resolution=90,
            phi_resolution=90,
        )
        if EARTH_TEXTURE is not None:
            self.p.add_mesh(earth, texture=EARTH_TEXTURE,
                            smooth_shading=True)
        else:
            self.p.add_mesh(earth, color="steelblue",
                            smooth_shading=True)

        # Rocket marker (small sphere instead of Cone — simpler)
        self.marker_mesh = pv.Sphere(
            radius=2e-5, theta_resolution=8, phi_resolution=8
        )

        self.p.camera_position = 'xy'
        self.p.reset_camera()

    def update(self, pos_m, show_trail=True):
        p = np.array(pos_m) * self.scale

        # Remove old marker
        if self.marker_actor is not None:
            self.p.remove_actor(self.marker_actor)
            self.marker_actor = None

        # Add new marker at current position
        self.marker_actor = self.p.add_mesh(
            self.marker_mesh, color="red", reset_camera=False
        )
        # Translate mesh
        self.marker_actor.SetPosition(float(p[0]), float(p[1]), float(p[2]))

        # Trail
        if show_trail:
            self.traj_points.append(p)
            if len(self.traj_points) > 1:
                if self.traj_actor is not None:
                    self.p.remove_actor(self.traj_actor)
                    self.traj_actor = None
                pts = np.array(self.traj_points[-5000:])
                line = pv.lines_from_points(pts)
                self.traj_actor = self.p.add_mesh(
                    line, color="yellow", line_width=3,
                    reset_camera=False,
                )

        self.p.render()