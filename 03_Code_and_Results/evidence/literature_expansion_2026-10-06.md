# Literature expansion: four Lasso survey candidates

Verified: 2026-10-06. Scope: basic mechanisms and limitations for a course survey. Sources below are publisher records or author-hosted/submitted papers. Listed sections were read; this is not a full proof audit. No report, code, data, or experimental results were changed.

The project uses \(F(w)=\|Xw-y\|_2^2/(2n)+\lambda\|w\|_1\). Preserve this normalization when explaining updates; the cited papers use different loss coefficients. These additions explain alternative solvers, acceleration, and screening, without extending the experiment.

## 1. Interior-point reformulation

**Verified citation:** Seung-Jean Kim, Kwangmoo Koh, Michael Lustig, Stephen Boyd, and Dimitry Gorinevsky. 2007. *An Interior-Point Method for Large-Scale ℓ1-Regularized Least Squares*. IEEE Journal on Selected Topics in Signal Processing, 1(4):606–617. DOI: [10.1109/JSTSP.2007.910971](https://doi.org/10.1109/JSTSP.2007.910971).

**Primary sources and actual reading:** [Author record](https://stanford.edu/~boyd/papers/l1_ls.html); [author-hosted journal PDF](https://stanford.edu/~boyd/papers/pdf/l1_ls.pdf), title page, author biographies for expanded names, §III-B (gap), §IV-A, Equation (13), and §IV-B (PCG). Journal pagination 606–617; Equation (13) is on p. 609. IEEE's landing page did not return usable content; the journal PDF itself verifies the DOI and publication header.

**Safe English summary (46 words):** Kim et al. reformulate ℓ1-regularized least squares as a quadratic program by introducing auxiliary variables satisfying \(-u_i\leq x_i\leq u_i\), replacing the absolute-value penalty with a linear sum of these bounds. Their specialized interior-point method uses a logarithmic barrier and approximate Newton directions computed by preconditioned conjugate gradients.

**Limits:** The paper uses \(\|Ax-y\|^2+\lambda\|x\|_1\). Its specialized implementation exploits matrix operations; generic quadratic-program solvers do not inherit its reported performance. Gap-based finite stopping certifies the specified suboptimality tolerance rather than an exact numerical solution.

## 2. ADMM splitting and linear algebra

**Verified citation:** Stephen Boyd, Neal Parikh, Eric Chu, Borja Peleato, and Jonathan Eckstein. 2011. *Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers*. Foundations and Trends in Machine Learning, 3(1):1–122. DOI: [10.1561/2200000016](https://doi.org/10.1561/2200000016).

**Primary sources and actual reading:** [Current publisher record](https://www.emerald.com/ftmal/article-abstract/3/1/1/1331527/Distributed-Optimization-and-Statistical-Learning?redirectedFrom=fulltext); [author record](https://web.stanford.edu/~boyd/papers/admm_distr_stats.html); [author PDF](https://web.stanford.edu/~boyd/papers/pdf/admm_distr_stats.pdf), title page, §3.3, §3.4.1, §4.2.1–4.2.3, and §6.4, p. 43.

**Date distinction:** The current publisher gives 26 July 2011 and 3(1):1–122 (2011); the author page agrees. The author PDF header labels the volume “2010” and copyright “2011”; the older now Publishers summary recommends 2010. Use 2011 consistently with the current publisher, retaining this discrepancy here.

**Safe English summary (48 words):** ADMM splits Lasso into a quadratic loss and an ℓ1 penalty linked by an equality constraint. Iterations alternate a regularized linear solve, soft thresholding, and a dual update. A fixed penalty parameter permits factorization reuse; changing it can alter convergence behavior and require recomputing the factorization.

**Mechanism locator:** §6.4 gives the system \((A^\top A+\rho I)x^{k+1}=A^\top b+\rho(z^k-u^k)\) and threshold \(\lambda/\rho\). §4.2 distinguishes factorization from subsequent solves.

**Limits:** ADMM introduces \(\rho\), distinct from Lasso's \(\lambda\). Cost depends on matrix structure and the solve strategy. Residual stopping tolerances are approximate optimality criteria. This survey reference does not establish that ADMM outperforms the project's three implementations.

## 3. Adaptive restart

**Verified citation:** Brendan O’Donoghue and Emmanuel Candès. 2015. *Adaptive Restart for Accelerated Gradient Schemes*. Foundations of Computational Mathematics, 15:715–732. DOI: [10.1007/s10208-013-9150-3](https://doi.org/10.1007/s10208-013-9150-3).

**Primary sources and actual reading:** [Springer record](https://link.springer.com/article/10.1007/s10208-013-9150-3), abstract and citation metadata; [author-submitted preprint](https://arxiv.org/pdf/1204.3982), §1 (reset), §3.1–3.2 (criteria), §4.2 and §4.5–4.6 (analysis and limits), §5.2 (FISTA application), Equation (12). These section/page locators refer to the 17-page preprint, not final journal pagination.

**Date distinction:** Springer gives online publication 3 July 2013 and issue date June 2015; journal citation year is 2015. The [arXiv record](https://arxiv.org/abs/1204.3982) identifies v1 submitted 18 April 2012. The rendered PDF also displays a 2024 title-page date; this is not the journal publication year.

**Safe English summary (49 words):** Adaptive restart resets accelerated-method momentum when the objective increases or a gradient-based criterion signals an unhelpful direction. The paper applies a generalized-gradient version to FISTA for sparse regression. Restart may improve convergence after suitable local quadratic behavior emerges, but the paper does not provide a universal Lasso linear-convergence guarantee.

**Limits:** The analysis uses approximations for positive-definite quadratics; the publisher calls it heuristic. §5.2 presents the Lasso extension as an expectation after support identification. §4.6 notes that early restarting can slow convergence. This supports discussing a possible extension, without relabeling standard FISTA or predicting an experimental speedup.

## 4. Gap Safe screening

**Verified citation:** Eugene Ndiaye, Olivier Fercoq, Alexandre Gramfort, and Joseph Salmon. 2017. *Gap Safe Screening Rules for Sparsity Enforcing Penalties*. Journal of Machine Learning Research, 18(128):1–33. [Official article record](https://jmlr.org/papers/v18/16-577.html).

**Title correction:** The candidate title “Gap Safe Screening Rules for Sparse Multi-Task and Multi-Class Models” is not the title of this JMLR article. Use the verified title above; no DOI is asserted.

**Primary source and actual reading:** [JMLR full text](https://jmlr.org/papers/volume18/16-577/16-577.pdf), §3.1 (Proposition 5), §3.2.1–3.2.2 (dual feasibility, sphere test, Theorem 6), §4.5 (Proposition 14), and §5.1 (Lasso).

**Safe English summary (45 words):** Gap Safe screening uses a dual-feasible point and the primal-dual gap to construct a region containing the dual optimum. Variables passing a strict screening test are guaranteed to have zero optimal coefficients and can be removed. As optimization progresses and the gap decreases, the safe region shrinks.

**Limits:** Safety requires a valid containing region and dual feasibility. A gap below ε bounds objective suboptimality by ε; it does not certify an exact coefficient vector. Finite identification concerns the equicorrelation set, which can exceed the optimal support. No paper speedup is transferred to this project.


## 5. Ridge reference

Arthur E. Hoerl and Robert W. Kennard. 1970. *Ridge Regression: Biased Estimation for Nonorthogonal Problems*. Technometrics, 12(1):55–67. DOI [10.1080/00401706.1970.10488634](https://doi.org/10.1080/00401706.1970.10488634). Publisher metadata and the [original journal scan](https://homepages.math.uic.edu/~lreyzin/papers/ridge.pdf) agree. Read §2 and §3b, equations (2.1), (3.3)–(3.7): diagonal regularization and the squared-norm constraint. The report uses its own loss normalization; it does not claim that any fixed ridge penalty improves prediction on all datasets. Online digitization in 2012 is distinct from publication in 1970.

## 6. Adaptive Lasso reference

Hui Zou. 2006. *The Adaptive Lasso and Its Oracle Properties*. Journal of the American Statistical Association, 101(476):1418–1429. DOI [10.1198/016214506000000735](https://doi.org/10.1198/016214506000000735). Verified against publisher metadata, [author profile](https://cse.umn.edu/isye/hui-zou), and [journal reprint](https://pages.stat.wisc.edu/~shao/stat992/zou2006.pdf). Read §3.1–3.2, definition (4) and Theorem 2 assumptions. Fixed positive weights retain convexity; statistical guarantees depend on initial-estimator, design and penalty-sequence conditions. The report does not transfer asymptotic guarantees to every finite dataset. Publication is 2006; online digitization is 2012.
