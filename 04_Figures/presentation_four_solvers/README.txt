PRESENTATION FOUR-SOLVER ASSETS — COMP6704 Group 9

Regenerate: python scripts/plot_presentation_assets.py
All numerical experiments are read from frozen CSV/JSON/NPZ files; no model is rerun.
Large-label figures use 16 pt axis text, 14 pt ticks and 12–14 pt legends.
Two-panel figures are approximately 12 x 3.7 in; single figures approximately 6.4 x 3.6 in.
White backgrounds; muted blue/orange/green/purple; PNG at 220 dpi plus vector SVG/PDF.
R(z) measures stationarity for the original objective. ADMM split residuals are labeled as raw Euclidean norms.
ADMM algorithmic beta is recorded as rho in CSV; it differs from feature correlation rho and model lambda.
Solver time includes method-specific setup and monitoring; shared spectral setup is excluded.
Use caption and provenance records when writing notes and citing statistics.
Nine transparent PNG equation assets use DejaVu Serif math text at 28 pt and 180 dpi.

truth_support: Known synthetic generating coefficients: five active variables among fifty candidates. This is data-generation input, not an estimated result.
soft_threshold: Analytic soft-threshold function with tau=0.5, generated directly from its definition rather than experimental fits.
main_runtime: All four solvers rerun on the same host. Synthetic bars: mean ± sample SD over three instance medians (five repeats per instance). Diabetes bars: median of five repeats, with all five timing points shown. Solver setup and monitoring are included; shared spectral setup is excluded.
convergence: Original unsplit objective versus elapsed solver time; median-time repetition on each input. ADMM is evaluated at z, so its displayed value is F(z), not a mixed split objective.
stationarity: Common original-objective stationarity versus rounds; median-time repetition. ADMM is evaluated at z. One CD round is a full sweep. Dashed horizontal line: R=1e-6.
correlation_time: Block-correlation study: means and sample SD across three instance medians, five repeats each. Correlation levels are shown at equally spaced categorical positions. Logarithmic time axis.
correlation_seed_times: FISTA and ADMM timing medians for the three individual instances at within-block correlation 0.99. Each bar is one five-repeat median; these bars reveal across-instance variation, not uncertainty within a timing repetition.
dimension_time: Independent-feature dimension study with 800 training samples. Means and sample SD across three instance medians, five repeats each. Both axes are logarithmic. ADMM factorization is included in solver time.
admm_setup: ADMM mean solver times split into paired saved setup and iteration components across three instance medians. Setup includes Gram construction and Cholesky factorization. Percent labels are the setup share of total time; shared spectral setup remains excluded.
admm_beta: ADMM beta sensitivity, distinct from model lambda and feature-correlation rho. Saved CSVs call beta 'rho'. Each value uses three timing repetitions; correlated points summarize three instance medians with sample SD. Main comparisons fix beta=1 before timing; this panel does not retrospectively tune the main benchmark.
coefficient_analysis: CD coefficients at lambda/lambda_max=0.1. Synthetic: first ten of fifty coefficients, generating values versus mean ± sample SD across three instances in original units. Diabetes: standardized coefficients, with no known true support. The CD fit represents the converged model shared numerically by all four solvers.
regularization: CD model-penalty study for synthetic data at four prespecified ratios. Synthetic values show means and sample SD across three instances; Diabetes uses one fixed split. Test scores describe settings and are not used for tuning lambda.
regularization_diabetes: CD model-penalty study for diabetes data at four prespecified ratios. Synthetic values show means and sample SD across three instances; Diabetes uses one fixed split. Test scores describe settings and are not used for tuning lambda.
timing_repetitions: Backup chart retaining all five main timing measurements per instance and solver. Black bars are medians; horizontal jitter only distinguishes repeated measurements. Timing repetitions are not independent datasets.
admm_diagnostics: Correlation 0.99, seed 10, beta=1. Left: unnormalized Euclidean primal and dual ADMM split residuals, with the zero initialization omitted on the logarithmic axis. Right: separately normalized original-objective stationarity R(z), the common stopping criterion. The raw split norms and R have different definitions and should not be compared numerically.
