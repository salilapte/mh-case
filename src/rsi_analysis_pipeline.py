"""
@File    :   rsi_analysis_pipeline.py
@Date    :   2025/10/06
@Author  :   Salil Apte
@Version :   0.1.0
@Contact :   sal1l@pm.me
@Desc    :   Main pipeline for Reactive Strength Index (RSI) analysis.

- Traverses data folders for OpenSim .pkl files
- Loads toe Y-position and time signals
- Detects jump events (GC, TO, LD)
- Computes RSI (Flight-time and Peak-height methods)
- Combines left and right foot metrics with asymmetry in a DataFrame

Usage:
>>> from rsi_analysis_pipeline import batch_process
>>> df_results = batch_process("Data", plot=False)
"""

import pickle
from pathlib import Path
import pandas as pd

from .event_detector import JumpEventDetector
from .rsi_analyser import RSICalculator

# =========================
# GLOBAL THRESHOLDS
# =========================
CUTOFF = 15  # Hz, low-pass filter
REL_THRESH = 0.05  # relative threshold for event detection
JUMP_HEIGHT_THRESH = 0.05  # minimum vertical displacement to count as jump (m)
VEL_PEAK_THRESH = 1.0  # minimum velocity peak magnitude to validate jump (m/s)
VEL_CONTACT_THRESH = 0.2  # minimum velocity during ground contact (m/s)


# -------------------------
def find_pkl_files(root_dir):
    """Traverse directory and return sorted list of all .pkl files."""
    return sorted(Path(root_dir).rglob("*.pkl"))


# -------------------------
def process_trial(file_path, subject, trial_id, plot=False):
    """Process a single trial: load data, detect events, compute RSI."""
    with open(file_path, "rb") as f:
        kinematics = pickle.load(f)

    body_kinematics = kinematics["body_kinematics"]
    time = body_kinematics["time"]
    left_toe_y = body_kinematics["toes_l_ty"]
    right_toe_y = body_kinematics["toes_r_ty"]

    # Initialize detector with all thresholds
    detector = JumpEventDetector(
        time,
        left_toe_y,
        right_toe_y,
        cutoff=CUTOFF,
        rel_thresh=REL_THRESH,
        jump_height_thresh=JUMP_HEIGHT_THRESH,
        vel_peak_thresh=VEL_PEAK_THRESH,
        vel_contact_thresh=VEL_CONTACT_THRESH,
    )

    if plot:
        detector.plot()

    # Compute RSI
    rsi_calc = RSICalculator()
    df_left = rsi_calc.compute_rsi_for_jumps(
        time, detector.left_filtered, detector.left_jumps, foot="Left"
    )
    df_right = rsi_calc.compute_rsi_for_jumps(
        time, detector.right_filtered, detector.right_jumps, foot="Right"
    )
    df_combined = rsi_calc.combine_feet(df_left, df_right)

    # Add metadata
    df_combined["Subject"] = subject
    df_combined["Trial"] = trial_id

    return df_combined


# -------------------------
def batch_process(root_dir, plot=False):
    """
    Traverse data directory and process all .pkl files.
    Returns a single long DataFrame with all results.
    Trial numbering restarts per subject.
    """
    all_results = []
    pkl_files = find_pkl_files(root_dir)

    # Group files by subject
    subject_files = {}
    for file_path in pkl_files:
        parts = Path(file_path).parts
        try:
            subject = parts[parts.index("Data") + 1]  # e.g., Data/subject1/...
        except ValueError:
            subject = "Unknown"
        subject_files.setdefault(subject, []).append(file_path)

    # Process each subject
    for subject, files in subject_files.items():
        print(f"\nProcessing Subject: {subject}")
        for trial_id, file_path in enumerate(sorted(files), start=1):
            print(f"  Trial {trial_id}: {file_path}")
            try:
                df_trial = process_trial(file_path, subject, trial_id, plot=plot)
                all_results.append(df_trial)
            except Exception as e:
                print(f"⚠️ Skipping {file_path} due to error: {e}")

    if not all_results:
        print("No results generated.")
        return pd.DataFrame()

    df_all = pd.concat(all_results, ignore_index=True)

    # Reorder columns
    df_all = df_all[
        [
            "Subject",
            "Trial",
            "Jump",
            "Limb",
            "GCT",
            "PeakHeight_Flight",
            "PeakHeight_Detected",
            "RSI_Flight",
            "RSI_Peak",
            "Asymmetry_Peak%",
        ]
    ]

    return df_all
