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

def plot_rsi_comparison(df, save=False, output_dir="results"):
    """
    Compare RSI_Peak and RSI_Flight across all trials and subjects.

    Args:
        df (pd.DataFrame): Combined results DataFrame.
        save (bool): If True, saves the figure as PNG.
        output_dir (str): Path to save the plot.
    """

    # Melt the DataFrame for plotting
    df_melt = df.melt(
        id_vars=["Subject", "Trial", "Limb"],
        value_vars=["RSI_Flight", "RSI_Peak"],
        var_name="RSI_Method",
        value_name="RSI_Value"
    )

    plt.figure(figsize=(10, 6))
    sns.pointplot(
        data=df_melt,
        x="Subject",
        y="RSI_Value",
        hue="RSI_Method",
        dodge=0.3,
        errorbar=("ci", 95),
        join=False,
        markers=["o", "s"],
        scale=1.3,
        linewidth=1.5,
        palette=["#eb811b", "#4ea72e"]
    )

    plt.title("Comparison of RSI_Peak and RSI_Flight Across Subjects", fontsize=14, weight="bold")
    plt.xlabel("Subject")
    plt.ylabel("Reactive Strength Index (RSI)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(title="RSI Method", loc="upper right", fontsize=10, title_fontsize=11)
    plt.tight_layout()

    if save:
        from datetime import datetime
        import os

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(output_dir, exist_ok=True)
        png_file = os.path.join(output_dir, f"rsi_comparison_{timestamp}.png")
        plt.savefig(png_file, dpi=300)
        print(f"Plot saved to: {png_file}")

    plt.show()

def plot_asymmetry_by_subject(df, save=False, output_dir="results"):
    """
    Create a subject-wise Asymmetry_% point plot with 95% CI and off-centre median labels.
    """

    # Filter for combined limb results only
    df_combined = df[df["Limb"] == "Combined"].copy()

    # Initialize figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Point plot (thin, dark teal)
    sns.pointplot(
        data=df_combined,
        x="Subject",
        y="Asymmetry_Peak%",
        errorbar=("ci", 95),
        color="#eb811b",
        markers="o",
        scale=1.2,
        join=False,
        ax=ax,
        linewidth=0.8
    )

    # Compute and annotate median values per subject (offset to avoid occlusion)
    medians = df_combined.groupby("Subject")["Asymmetry_Peak%"].median().reset_index()
    for i, row in medians.iterrows():
        ax.text(
            i + 0.35, 
            row["Asymmetry_Peak%"] + 0.5,  # offset vertically
            f"{row['Asymmetry_Peak%']:.1f}%", 
            ha="right", 
            va="top", 
            fontsize=9,
            color="#eb811b",
            fontweight="bold"
        )

    # Aesthetic adjustments
    ax.set_title("Jump Asymmetry by Subject", fontsize=14, fontweight="bold", color="#273a3d", pad=15)
    ax.set_xlabel("Subject", fontsize=12, color="#273a3d")
    ax.set_ylabel("Asymmetry (%)", fontsize=12, color="#273a3d")
    ax.grid(True, linestyle="--", alpha=0.3)
    sns.despine()

    # Tight layout
    plt.tight_layout()

    # Save plot with timestamp
    if save:
        from datetime import datetime
        import os

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"asymmetry_by_subject_{timestamp}.png"
        path = os.path.join(output_dir, filename)
        plt.savefig(path, dpi=300, bbox_inches="tight")
        print(f"Plot saved to: {path}")

    plt.show()
