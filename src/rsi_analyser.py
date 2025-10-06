"""
@File    :   rsi_analyser.py
@Date    :   2025/10/06
@Author  :   Salil Apte
@Version :   0.1.0
@Contact :   sal1l@pm.me
@Desc    :   Reactive Strength Index (RSI) calculator.

Defines the `RSICalculator` class to:
- Compute RSI for each jump using:
    - Flight-time method
    - Peak-height method
- Combine left and right foot metrics
- Compute asymmetry percentages
- Output results as a pandas DataFrame

Inputs:
- time : np.ndarray
- pos : np.ndarray (toe Y or Z positions)
- jumps : list of tuples (GC, TO, LD)
- foot : "Left" or "Right"

Outputs:
- DataFrame with columns:
    Jump | Limb | GCT | PeakHeight_Flight | PeakHeight_Detected
    | RSI_Flight | RSI_Peak | Asymmetry_%

Usage:
>>> rsi_calc = RSICalculator()
>>> df_left = rsi_calc.compute_rsi_for_jumps(time, left_filtered, left_jumps, foot="Left")
>>> df_combined = rsi_calc.combine_feet(df_left, df_right)
"""

import numpy as np
import pandas as pd


class RSICalculator:
    def __init__(self, g=9.81):
        # Gravity constant used to compute jump height
        self.g = g

    def compute_rsi_for_jumps(self, time, pos, jumps, foot="Left"):
        """
        Compute RSI for each jump using both methods:
        - Flight time method: h = g * t^2 / 8
        - Position peak method: peak displacement - baseline

        Returns DataFrame (per foot) with:
        Jump | Limb | GCT | PeakHeight_Flight | PeakHeight_Detected | RSI_Flight | RSI_Peak | Asymmetry_Peak%
        """
        rows = []
        for j, (gc, toe, land) in enumerate(jumps, start=1):
            # Estimate durations
            if gc is not None and toe is not None:
                gct = time[toe] - time[gc]
            else:
                gct = None
            if toe is not None and land is not None:
                flight_time = time[land] - time[toe]
            else:
                flight_time = None

            # Estimate heights
            if flight_time:
                h_flight = self.g * (flight_time**2) / 8
            else:
                h_flight = None
            if toe is not None and land is not None:
                peak = np.max(pos[toe:land])
            else:
                peak = None
            if peak is not None and gc is not None:
                h_peak = peak - np.mean(pos[gc:toe])
            else:
                h_peak = None

            # RSI
            if gct and gct > 0 and h_flight is not None:
                rsi_flight = h_flight / gct
            else:
                rsi_flight = None
            if gct and gct > 0 and h_peak is not None:
                rsi_peak = h_peak / gct
            else:
                rsi_peak = None

            rows.append(
                {
                    "Jump": j,
                    "Limb": foot,
                    "GCT": gct,
                    "PeakHeight_Flight": h_flight,
                    "PeakHeight_Detected": h_peak,
                    "RSI_Flight": rsi_flight,
                    "RSI_Peak": rsi_peak,
                    "Asymmetry_%": None,
                }
            )
        return pd.DataFrame(rows)

    def _compute_asym(self, left, right):
        """Compute asymmetry percentage given two values."""
        if pd.isna(left) or pd.isna(right):
            return None
        if max(left, right) == 0:
            return None
        return 2 * abs(left - right) / (left + right) * 100

    def combine_feet(self, df_left, df_right):
        """
        Combine left & right RSI results into long-format DataFrame.

        Output schema:
        Jump | Limb | GCT | PeakHeight_Flight | PeakHeight_Detected | RSI_Flight | RSI_Peak | Asymmetry_%
        """
        rows = []

        # Case: no jumps
        if df_left.empty and df_right.empty:
            print("Warning: No jumps detected.")
            return pd.DataFrame(
                columns=[
                    "Jump",
                    "Limb",
                    "GCT",
                    "PeakHeight_Flight",
                    "PeakHeight_Detected",
                    "RSI_Flight",
                    "RSI_Peak",
                    "Asymmetry_%",
                ]
            )

        # Case: only one side present
        if df_left.empty or df_right.empty:
            print("Warning: Jump detected for only one leg.")
            df_present = df_left if not df_left.empty else df_right
            return df_present.copy()  # Already in long format per limb

        # Case: both present
        df_all = pd.merge(
            df_left, df_right, on="Jump", how="outer", suffixes=("_Left", "_Right")
        )

        for _, row in df_all.iterrows():
            j = row["Jump"]

            # Append left row
            rows.append(
                {
                    "Jump": j,
                    "Limb": "Left",
                    "GCT": row["GCT_Left"],
                    "PeakHeight_Flight": row["PeakHeight_Flight_Left"],
                    "PeakHeight_Detected": row["PeakHeight_Detected_Left"],
                    "RSI_Flight": row["RSI_Flight_Left"],
                    "RSI_Peak": row["RSI_Peak_Left"],
                    "Asymmetry_Peak%": None,
                }
            )

            # Append right row
            rows.append(
                {
                    "Jump": j,
                    "Limb": "Right",
                    "GCT": row["GCT_Right"],
                    "PeakHeight_Flight": row["PeakHeight_Flight_Right"],
                    "PeakHeight_Detected": row["PeakHeight_Detected_Right"],
                    "RSI_Flight": row["RSI_Flight_Right"],
                    "RSI_Peak": row["RSI_Peak_Right"],
                    "Asymmetry_Peak%": None,
                }
            )

            # Combined row
            rsi_flight_vals = [
                v
                for v in [row["RSI_Flight_Left"], row["RSI_Flight_Right"]]
                if not pd.isna(v)
            ]
            rsi_peak_vals = [
                v
                for v in [row["RSI_Peak_Left"], row["RSI_Peak_Right"]]
                if not pd.isna(v)
            ]

            comb_row = {
                "Jump": j,
                "Limb": "Combined",
                "GCT": np.nanmean([row["GCT_Left"], row["GCT_Right"]]),
                "PeakHeight_Flight": np.nanmean(
                    [row["PeakHeight_Flight_Left"], row["PeakHeight_Flight_Right"]]
                ),
                "PeakHeight_Detected": np.nanmean(
                    [row["PeakHeight_Detected_Left"], row["PeakHeight_Detected_Right"]]
                ),
                "RSI_Flight": np.median(rsi_flight_vals) if rsi_flight_vals else None,
                "RSI_Peak": np.median(rsi_peak_vals) if rsi_peak_vals else None,
                "Asymmetry_Peak%": self._compute_asym(
                    row["RSI_Peak_Left"], row["RSI_Peak_Right"]
                ),
            }
            rows.append(comb_row)

        return pd.DataFrame(rows)
