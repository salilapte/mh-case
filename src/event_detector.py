"""
@File    :   event_detector.py
@Date    :   2025/10/06
@Author  :   Salil Apte
@Version :   0.1.0
@Contact :   sal1l@pm.me
@Desc    :   Jump event detection for Reactive Strength Index (RSI) analysis.

Defines the `JumpEventDetector` class to:
- Filter toe Y-position signals
- Compute velocity
- Detect GC (ground contact), TO (toe-off), LD (landing)
- Validate jumps based on height and velocity thresholds
- Provide visualization of positions, velocity, and events

Inputs:
- time, left_toe_y, right_toe_y
- cutoff, rel_thresh, jump_height_thresh, vel_peak_thresh, vel_contact_thresh

Outputs:
- left_jumps, right_jumps
- left_filtered, right_filtered
- left_vel, right_vel

Usage:
>>> detector = JumpEventDetector(time, left_toe_y, right_toe_y)
>>> detector.plot()
>>> print(detector.left_jumps, detector.right_jumps)
"""

import numpy as np
from scipy.signal import butter, filtfilt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class JumpEventDetector:
    def __init__(
        self,
        time,
        left_toe_z,
        right_toe_z,
        cutoff=15,
        rel_thresh=0.05,
        jump_height_thresh=0.05,
        vel_peak_thresh=1.0,
        vel_contact_thresh=0.2,
    ):
        """
        Parameters
        ----------
        time : array
            Time array (s)
        left_toe_z, right_toe_z : arrays
            Vertical toe positions
        cutoff : float
            Low-pass filter cutoff frequency (Hz)
        rel_thresh : float
            Relative threshold above ground to detect TO/LD (m)
        jump_height_thresh : float
            Minimum displacement (m) for valid jump
        vel_peak_thresh : float
            Min absolute velocity peak (m/s) in both directions to accept a jump
        vel_contact_thresh : float
            Max velocity magnitude at ground contact (m/s)
        """
        self.time = time
        self.dt = np.mean(np.diff(time))
        self.fs = 1 / self.dt

        self.cutoff = cutoff
        self.rel_thresh = rel_thresh
        self.jump_height_thresh = jump_height_thresh
        self.vel_peak_thresh = vel_peak_thresh
        self.vel_contact_thresh = vel_contact_thresh

        # Filter signals
        self.left_filtered = self._butter_lowpass_filter(left_toe_z)
        self.right_filtered = self._butter_lowpass_filter(right_toe_z)

        # Velocities
        self.left_vel = np.gradient(self.left_filtered, self.dt)
        self.right_vel = np.gradient(self.right_filtered, self.dt)

        # Ground levels (mean of last 1.5 second)
        self.left_ground = np.mean(self.left_filtered[int(-1.5 * self.fs) :])
        self.right_ground = np.mean(self.right_filtered[-int(-1.5 * self.fs) :])

        # Events
        self.left_jumps = self._detect_jumps(
            self.left_filtered, self.left_vel, self.left_ground
        )
        self.right_jumps = self._detect_jumps(
            self.right_filtered, self.right_vel, self.right_ground
        )

    def _butter_lowpass_filter(self, signal):
        nyq = 0.5 * self.fs
        normal_cutoff = self.cutoff / nyq
        b, a = butter(4, normal_cutoff, btype="low", analog=False)
        return filtfilt(b, a, signal)

    def _detect_jumps(self, pos, vel, ground):
        """
        Detect reactive jumps:
        GC = initial landing (from drop, requires negative velocity peak)
        TO = toe-off (start of reactive jump)
        LD = final landing (end of reactive jump)
        """
        jumps = []
        state = "waiting_gc"
        gc, to, ld = None, None, None

        for i in range(1, len(pos)):
            # --- Detect Ground Contact (drop landing) ---
            if state == "waiting_gc" and pos[i] <= ground + self.rel_thresh:
                # Look back for a recent strong negative velocity peak
                window = vel[max(0, i - int(0.4 * self.fs)) : i + 1]  # last 200 ms
                if len(window) > 0 and np.min(window) <= -self.vel_peak_thresh:
                    # Confirm velocity is small at GC
                    if abs(vel[i]) <= self.vel_contact_thresh:
                        gc = i
                        state = "waiting_to"

            # --- Detect Toe-Off ---
            elif state == "waiting_to" and pos[i] > ground + self.rel_thresh:
                to = i
                state = "waiting_ld"

            # --- Detect Landing (end of reactive jump) ---
            elif state == "waiting_ld" and pos[i] <= ground + self.rel_thresh:
                ld = i
                state = "done"

                # ---- Validation ----
                disp = np.max(pos[to:ld]) - np.min(pos[to:ld])
                if disp < self.jump_height_thresh:
                    state = "waiting_gc"
                    continue

                v_segment = vel[to:ld]

                # Must cross zero once (up -> down)
                if not np.any(np.diff(np.sign(v_segment))):
                    state = "waiting_gc"
                    continue

                # Take only the largest upward and downward velocities
                vmax = np.max(v_segment)
                vmin = np.min(v_segment)

                if vmax < self.vel_peak_thresh or abs(vmin) < self.vel_peak_thresh:
                    state = "waiting_gc"
                    continue

                # Save valid jump
                jumps.append((gc, to, ld))
                state = "waiting_gc"  # ready for next jump

        return jumps

    def plot(self):
        """
        Plot left and right toe Z and velocities in four rows with detected events.
        GC = Ground Contact (landing from drop)
        TO = Toe-Off (start of reactive jump)
        LD = Landing (end of reactive jump)
        """
        fig = make_subplots(
            rows=4,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(
                "Left Toe Y",
                "Left Toe Velocity",
                "Right Toe Y",
                "Right Toe Velocity",
            ),
        )

        # Left traces
        fig.add_trace(
            go.Scatter(
                x=self.time, y=self.left_filtered, mode="lines", name="Left Toe Y"
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=self.time, y=self.left_vel, mode="lines", name="Left Toe Velocity"
            ),
            row=2,
            col=1,
        )

        # Right traces
        fig.add_trace(
            go.Scatter(
                x=self.time, y=self.right_filtered, mode="lines", name="Right Toe Y"
            ),
            row=3,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=self.time, y=self.right_vel, mode="lines", name="Right Toe Velocity"
            ),
            row=4,
            col=1,
        )

        # Event colors
        event_colors = {"GC": "black", "TO_LD": "green"}

        # Add events with labels
        for jumps, foot, z_row, vel_row in [
            (self.left_jumps, "Left", 1, 2),
            (self.right_jumps, "Right", 3, 4),
        ]:
            for j_idx, (gc, to, ld) in enumerate(jumps, start=1):
                gc_time = self.time[gc]
                to_time, ld_time = self.time[to], self.time[ld]
                mid_time = (to_time + ld_time) / 2

                # For both position and velocity rows
                for row in [z_row, vel_row]:
                    # Vertical line for GC
                    fig.add_vline(
                        x=gc_time,
                        line=dict(color=event_colors["GC"], dash="dash"),
                        row=row,
                        col=1,
                    )

                    # GC label
                    fig.add_annotation(
                        x=gc_time,
                        y=0,
                        xref="x",
                        yref=f"y{row}",
                        text=f"{foot} GC",
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        font=dict(color=event_colors["GC"]),
                    )

                    # Shaded area for TO → LD
                    fig.add_vrect(
                        x0=to_time,
                        x1=ld_time,
                        fillcolor=event_colors["TO_LD"],
                        opacity=0.2,
                        line_width=0,
                        row=row,
                        col=1,
                    )

                    # Jump label in shaded area
                    fig.add_annotation(
                        x=mid_time,
                        y=0,
                        xref="x",
                        yref=f"y{row}",
                        text=f"{foot} Jump {j_idx}",
                        showarrow=False,
                        font=dict(color="black", size=10),
                        bgcolor="white",
                        opacity=0.7,
                    )

        # Axis labels
        fig.update_yaxes(title_text="Position (m)", row=1, col=1)
        fig.update_yaxes(title_text="Velocity (m/s)", row=2, col=1)
        fig.update_yaxes(title_text="Position (m)", row=3, col=1)
        fig.update_yaxes(title_text="Velocity (m/s)", row=4, col=1)
        fig.update_xaxes(title_text="Time (s)", row=4, col=1)

        fig.update_layout(
            height=800,
            width=1000,
            title="Jump Event Detection (Left/Right Toe)",
            legend=dict(title="Events", x=1.05, y=1),
        )
        fig.show()
