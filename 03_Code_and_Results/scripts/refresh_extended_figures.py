"""Render presentation figures from saved results; no model is rerun."""
from pathlib import Path
import json
from run_extended_experiments import plots, render_saved_trajectory
root=Path(__file__).resolve().parents[1]
source=root/'results/2026-10-07-extended'
target=root/'output/figures/extended';target.mkdir(parents=True,exist_ok=True)
plots(target,json.loads((source/'summary.json').read_text())['summary'],
      json.loads((source/'coefficient_path_data.json').read_text()),trace_root=source)
render_saved_trajectory(json.loads((source/'trajectory_data.json').read_text()),target)
print('Refreshed four PNG/SVG figure pairs from frozen results.')
