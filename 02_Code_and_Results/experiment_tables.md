# Four-solver results: 6 November 2026

Current source: `results/2026-11-06-four-solvers/`. Historical three-solver tables are archived under `output/archive/pre-admm-2026-11-06/`.

| Input | Method | Time (ms) | Rounds | Test MSE | Nonzero |
|---|---|---:|---:|---:|---:|
| Synthetic: mean ± sample SD | ISTA | 0.448 ± 0.004 | 24.7 ± 0.6 | 0.396 ± 0.139 | 5 ± 0 |
| Synthetic: mean ± sample SD | FISTA | 0.608 ± 0.044 | 30.7 ± 2.3 | 0.396 ± 0.139 | 5 ± 0 |
| Synthetic: mean ± sample SD | CD | 0.959 ± 0.119 | 5.0 ± 0.0 | 0.396 ± 0.139 | 5 ± 0 |
| Synthetic: mean ± sample SD | ADMM | 0.618 ± 0.069 | 24.0 ± 1.0 | 0.396 ± 0.139 | 5 ± 0 |
| Diabetes: fixed split | ISTA | 1.510 | 92.0 | 2966.935 | 5 |
| Diabetes: fixed split | FISTA | 1.449 | 85.0 | 2966.936 | 5 |
| Diabetes: fixed split | CD | 0.677 | 14.0 | 2966.937 | 5 |
| Diabetes: fixed split | ADMM | 0.582 | 28.0 | 2966.937 | 5 |

Time includes cold preparation and monitoring. Each instance is the median of five timings. The main ADMM algorithmic penalty is 1.

Controlled study: `extended/aggregated_results.csv`; ADMM sensitivity: `sensitivity/sensitivity_results.csv`.

All 560 primary timings and 45 sensitivity timings converged. At correlation 0.99, ADMM has the lowest mean but FISTA is faster on two of three instances. Main synthetic timing ranges overlap.

Detailed independent checks: `output/four_solver_independent_audit.json`.
