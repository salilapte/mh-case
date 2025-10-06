"""
@File    :   plots.py
@Date    :   2025/10/06
@Author  :   Salil Apte
@Version :   0.1.0
@Contact :   sal1l@pm.me
@Desc    :   Plotting utilities for Reactive Strength Index (RSI) analysis.

Includes functions to:
- Plot Ground Contact Time vs Peak Height
- Plot RSI_Peak with normative bands
- Color-code trials by subject
- Save plots as PNG with timestamp

Usage:
>>> from src.plots import plot_gct_vs_peakheight, plot_rsi_normative
>>> plot_gct_vs_peakheight(results, save=True)
>>> plot_rsi_normative(results, save=True)
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import seaborn as sns
import numpy as np

sns.set_theme(style="whitegrid")  # nicer background for plots


def plot_gct_vs_peakheight(
    results: pd.DataFrame,
    limb="Combined",
    save: bool = False,
    results_folder: str = "results",
):
    """
    Scatter plot of GCT vs PeakHeight_Detected with prominent markers per subject.
    """
    df_plot = results[results["Limb"] == limb].copy()

    plt.figure(figsize=(10, 6))
    subjects = df_plot["Subject"].unique()
    markers = ["o", "s", "D", "^", "v", "<", ">"]  # cycle if more subjects
    for i, subj in enumerate(subjects):
        df_subj = df_plot[df_plot["Subject"] == subj]
        plt.scatter(
            df_subj["GCT"],
            df_subj["PeakHeight_Detected"],
            label=subj,
            s=80,
            edgecolor="k",
            marker=markers[i % len(markers)],
        )

    plt.xlabel("Ground Contact Time (s)")
    plt.ylabel("Peak Height Detected (m)")
    plt.title("GCT vs. Peak Height")
    plt.legend()
    plt.tight_layout()

    if save:
        folder = Path(results_folder)
        folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_file = folder / f"gct_vs_peakheight_{timestamp}.png"
        plt.savefig(png_file, dpi=300)
        print(f"Plot saved to: {png_file.resolve()}")

    plt.show()


def plot_rsi_normative(
    results: pd.DataFrame,
    limb="Combined",
    save: bool = False,
    results_folder: str = "results",
):
    """
    Seaborn pointplot of RSI_Peak per subject with lighter normative bands.
    Shows mean ± 95% CI per subject, overlay of individual trials, and median annotations.
    Normative RSI categories (GymAware):
    https://gymaware.com/reactive-strength-index-rsi-in-sports/
        Poor <0.6, Below Avg 0.6-0.8, Average 0.8-1.2, Good 1.2-1.8, Excellent >1.8
    """
    df_plot = results[results["Limb"] == limb].copy()
    subjects = df_plot["Subject"].unique()

    # Normative bands
    bands = [
        (0, 0.6, "Poor <0.6", "#FFCCCC"),
        (0.6, 0.8, "Below Avg 0.6-0.8", "#FFFFCC"),
        (0.8, 1.2, "Average 0.8-1.2", "#CCFFCC"),
        (1.2, 1.8, "Good 1.2-1.8", "#CCE5FF"),
        (1.8, 2.5, "Excellent >1.8", "#E5CCFF"),
    ]

    plt.figure(figsize=(12, 6))

    # Plot shaded bands and labels inside the band on the right edge
    x_max = len(subjects) - 0.55  # right edge of last subject
    for y0, y1, label, color in bands:
        plt.axhspan(y0, y1, facecolor=color, alpha=0.3)
        plt.text(x_max + 0.1, (y0 + y1) / 2, label, va="center", fontsize=12)

    # Point plot per subject (mean ± 95% CI)
    sns.pointplot(
        x="Subject",
        y="RSI_Peak",
        data=df_plot,
        errorbar=("ci", 95),
        markers="o",
        linestyle="none",
        color="black",
    )

    # Overlay individual points
    sns.stripplot(
        x="Subject",
        y="RSI_Peak",
        data=df_plot,
        jitter=True,
        size=8,
        edgecolor="k",
        alpha=0.7,
        color="skyblue",
    )

    # Annotate median for each subject
    for i, subj in enumerate(subjects):
        median_val = df_plot[df_plot["Subject"] == subj]["RSI_Peak"].mean()
        plt.text(
            i,
            median_val + 0.17,
            f"{median_val:.2f}",
            ha="center",
            va="bottom",
            fontsize=14,
            color="black",
        )

    plt.ylabel("Reactive Strength Index (RSI)")
    plt.xlabel("Subject")
    plt.title("RSI per subject with normative bands")
    plt.tight_layout()

    if save:
        folder = Path(results_folder)
        folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        png_file = folder / f"rsi_peak_pointplot_{timestamp}.png"
        plt.savefig(png_file, dpi=300)
        print(f"Plot saved to: {png_file.resolve()}")

    plt.show()
