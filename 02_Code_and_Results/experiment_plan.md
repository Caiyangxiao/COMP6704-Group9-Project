# Current experiment protocol

The four-solver protocol below was recorded in experiment_plan_admm.md before the new measurements. The previous three-solver plan is retained in output/archive/pre-admm-2026-11-06/experiment_plan.md and historical run snapshots.

# Four-solver Lasso revision: protocol fixed before new timings

Date: 6 November 2026. This file specifies the new comparison before examining the new timing results. Historical results remain in their original directories and are not pooled with this rerun.

## Objective and implementations

All solvers minimize `||Xw-y||^2/(2*n) + lambda*||w||_1` on the same centered, training-standardized inputs. Methods: ISTA, standard FISTA without restart, cyclic coordinate descent, and fixed-penalty scaled ADMM. All primal coefficient vectors start at zero; ADMM's split and scaled dual vectors also start at zero. CD uses complete coordinate sweeps.

ADMM splits `g(x)+lambda*||z||_1` subject to `x=z`, uses `rho=1.0`, no over-relaxation or adaptive penalty, and returns `w=z`. Its x update solves `(X.T@X/n+rho*I)x = X.T@y/n+rho*(z-u)` by a cached Cholesky factorization. The factorization, Gram matrix, and right-hand-side preparation occur inside each timed cold solve. No factorization is reused across timing repetitions, instances, or penalty values. Thresholding uses `lambda/rho`. Both the loss and L1 term in a plotted objective are evaluated at the returned coefficient vector z, not at two different split vectors.

## Shared accuracy and measurements

Use the existing proximal-gradient mapping residual R at the returned coefficient vector for every method. Stop at R <= 1e-6 or 10,000 rounds. Record and flag unconverged runs. A small R is a stationarity measure and is not asserted to be an objective-error upper bound. For ADMM additionally save the primal residual `||x-z||_2` and dual residual `rho*||z-z_previous||_2` as diagnostics, not a replacement stopping rule.

Each instance-method pair has five timings, with method order rotated by repetition over all four methods. Report the median elapsed time, including preparation, per-round objective/residual monitoring and history recording. Report ADMM preparation separately to expose its cold-factorization cost. Shared data loading, preprocessing, spectral-norm computation, and plotting are excluded; shared spectral setup is recorded separately. Request one numerical thread before imports and record detected thread pools and actual runtime/library versions.

## Data and studies

1. Main comparison: the three supplied synthetic CSVs and Diabetes CSV, using their saved splits and verified SHA-256 hashes. Lambda is 0.1*lambda_max with lambda_max=||X.T@y/n||_infinity. Synthetic: 300 observations, 50 features, 240/60 train/test, seeds 0–2. Diabetes: 442 observations, 10 features, 353/89 train/test. No train/test split or predictor values are changed.
2. Correlation study: the existing paired generator, 600 observations, 60 features, six blocks of ten, correlations 0, 0.5, 0.9, 0.99, seeds 10–12, 480/120 train/test. Preserve shared underlying random draws and splits across correlation levels.
3. Dimension study: the existing paired generator, 1,000 observations, 800/200 train/test, d=50,100,300,600, seeds 10–12; use prefixes of the same widest matrix and the same response per seed.
4. Model sensitivity: retain the four CD penalty ratios 0.01,0.1,0.5,1 on the four main instances and the 34-point CD paths on synthetic seed 0 and Diabetes. These are model illustrations, not solver-ranking experiments or test-based penalty selection.
5. ADMM parameter sensitivity: rho=0.1,1,10 on synthetic seed 0, Diabetes, and the three correlation-0.99 instances, with three timings per setting. Keep lambda and R tolerance fixed. The main comparison remains at the predeclared rho=1 regardless of these outcomes.

## Validation and summaries

Validate the normalized objective against an orthogonal closed form and a tight independent scikit-learn Lasso reference. Include ADMM-specific tests for rho changes and rank-deficient designs. Save raw timings, representative median-time traces, coefficient arrays, split inputs, diagnostics, source snapshots and hashes, configurations, environment versions, and validation outputs.

Synthetic and controlled-study summaries are means and sample standard deviations across three instance medians. Diabetes remains a single fixed split. Repeated timings measure execution variability, not data uncertainty. Do not assign a universal solver ranking, equate CD sweeps to equal-cost vector rounds, treat split-objective values as the original Lasso objective, or claim personal implementation authorship without member confirmation.

Expected primary run counts: 80 main timings + 480 controlled-study timings = 560 timed solves; 16 four-ratio penalty fits; 68 coefficient-path fits. ADMM sensitivity adds 45 timed solves. Deviations, numerical failures, or changes made after these measurements must be documented separately.
