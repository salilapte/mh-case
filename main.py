"""
@File    :   main.py
@Time    :   2025/10/05
@Author  :   Salil Apte
@Version :   1.0
@Contact :   sal1l@pm.me
@Desc    :   Run the full Reactive Strength Index (RSI) pipeline for multiple subjects.

- Traverses the Data folder for OpenSim .pkl files
- Detects jump events (GC, TO, LD)
- Computes RSI (Flight-time and Peak-height)
- Combines left and right foot metrics and computes asymmetry
- Saves results as CSV with timestamp
- Generates plots for GCT vs Peak Height and RSI vs normative bands

Run in terminal:
    python -m main
"""

# Import pipeline
from src.rsi_analysis_pipeline import batch_process
from src.plots import plot_gct_vs_peakheight, plot_rsi_normative
from datetime import datetime
import os

# Now run batch processing; the new values will be used
results = batch_process("Data", plot=False)

# Ensure results folder exists
results_folder = "results"
os.makedirs(results_folder, exist_ok=True)

# Generate timestamp as suffix
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"rsi_results_{timestamp}.csv"

csv_path = os.path.join(results_folder, csv_filename)

results.to_csv(csv_path, index=False)
print(results.head())

# After generating results DataFrame
plot_gct_vs_peakheight(results, save=True)
plot_rsi_normative(results, save=True)