FOUR-SOLVER FIGURES — COMP6704 Group 9

Generated only from saved numerical records, with no optimizer calls.
Run: python scripts/plot_four_solver_results.py
Each chart is available as vector PDF/SVG and a 220-dpi PNG.
Colors: ISTA blue; FISTA orange; cyclic CD green; ADMM purple.
R is the common proximal-gradient stationarity residual for the original Lasso objective.
ADMM beta is called rho in the numerical CSVs and is distinct from correlation rho and model lambda.
Solver-specific setup and monitoring are included in solver times; shared spectral setup is excluded.
Five timing repetitions yield one instance median in the main and extended benchmarks.
Error bars show sample SD across three instances where indicated, not timing uncertainty.
Sensitivity uses three timing repetitions per instance and beta setting.
The machine-readable figure_manifest.json records all consumed input hashes and output hashes.

convergence: Objective against elapsed time on two fixed inputs; each curve uses the median-time repetition. ADMM setup and all methods' monitoring are included.
stationarity: Common original-objective stationarity residual versus rounds; one CD round is a full sweep. Dashed line: 1e-6. ADMM is evaluated at its returned z coefficients.
timing_repetitions: All five timings for each of the four main instances. Small horizontal offsets distinguish repetitions and carry no meaning; black bars show medians. Repetitions are not independent datasets.
efficiency_summary: Main benchmark solver times. Synthetic bars: means and sample SD of three instance medians, each from five repeats. Diabetes has a single split and no across-instance error bar.
correlation_comparison: Paired block-correlation study. Time/round points show means and sample SD across three instances (five repeats per instance). Bottom left is seed 10 only; bottom right is the mean full-Gram condition number. Correlation levels are equally spaced categorical positions.
dimension_comparison: Independent-feature dimension study. Points show means and sample SD across three instance medians (five timings per instance). ADMM factorization is included; shared spectral setup is excluded.
coefficient_analysis: CD coefficients at lambda/lambda_max=0.1. Synthetic panel shows generating values and mean ± sample SD over three instances in original units, displaying the first ten of fifty coefficients. Diabetes coefficients are standardized, with no known true support.
regularization: CD penalty sensitivity at four prespecified lambda ratios. Synthetic values are means and sample SD across three instances; Diabetes has one split. Test scores are descriptive and are not used to select lambda.
coefficient_paths: CD cold-start paths over 34 prespecified penalties. Colored synthetic curves correspond to the five true active coefficients; colored Diabetes curves are variables selected at ratio 0.1, not known ground truth. Gray curves are the remaining coefficients.
admm_penalty_sensitivity: ADMM algorithmic-penalty sensitivity (beta, saved as rho in CSV), distinct from the model lambda. Each saved value is the median of three repeated cold starts. Correlated-design points show mean and sample SD across three instance medians; the two original inputs have no across-instance SD. Main comparisons prespecify beta=1.
setup_cost: Solver time decomposed into the saved solver-specific setup component and the remainder (iterations and monitoring). Main instance medians are summarized within each dataset family; ADMM setup includes Gram construction and Cholesky factorization.
