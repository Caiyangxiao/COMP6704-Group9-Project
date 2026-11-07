"""Dense solvers for ``||Xw-y||^2/(2*n) + lam*||w||_1``.

ISTA, standard FISTA, cyclic coordinate descent, and scaled ADMM use the same
proximal-gradient stationarity check. ADMM returns its sparse ``z`` variable;
objective values and stationarity are evaluated at that single vector, rather
than mixing the loss at ``x`` with the penalty at ``z`` before feasibility.

ADMM follows the splitting in Boyd et al. (2011), Section 6.4, adapted to the
``1/(2*n)`` loss normalization used throughout this project:
https://web.stanford.edu/~boyd/papers/admm/lasso/lasso.html
"""
from time import perf_counter

import numpy as np
from scipy.linalg import cho_factor, cho_solve


def soft_threshold(v, threshold):
    return np.sign(v) * np.maximum(np.abs(v) - threshold, 0.0)


def evaluate(X, y, w, lam, L, residual_scale):
    residual = X @ w - y
    objective = residual @ residual / (2 * len(y)) + lam * np.abs(w).sum()
    gradient = X.T @ residual / len(y)
    mapping = L * (w - soft_threshold(w - gradient / L, lam / L))
    return float(objective), float(np.max(np.abs(mapping)) / residual_scale)


def solve(X, y, lam, L, method, tol=1e-6, max_rounds=10000, *, admm_rho=1.0):
    """Solve the fixed Lasso problem from zero initialization.

    ``method`` is ISTA, FISTA, CD, or ADMM. A round is one vector update, one
    complete CD sweep, or one complete ADMM x/z/u update. All methods stop when
    the normalized proximal-gradient residual at the returned ``w`` is at most
    ``tol``, or when ``max_rounds`` is exhausted.

    ADMM uses a fixed positive ``admm_rho`` (default 1) without relaxation or
    adaptive penalties. It factors ``X.T @ X / n + rho*I`` once and reuses the
    Cholesky factor. Forming and factoring that system is included in elapsed
    and setup time. This dense implementation stores a d-by-d factor, including
    when d > n; it does not use a Woodbury/sparse specialization.

    ``history`` retains the existing four columns: round, seconds, objective,
    common residual. ``setup_seconds`` includes initialization and the first
    common check; ``iteration_seconds`` is the remaining recorded elapsed time.
    ADMM also returns ``diagnostic_history`` with columns round, primal_l2,
    dual_l2, where primal_l2=||x-z||_2 and dual_l2=rho*||z-z_previous||_2. These
    diagnostics are recorded for interpretation, not used as extra stopping
    conditions. All histories include the zero-initialization row.
    """
    if method == "ADMM":
        admm_rho = float(admm_rho)
        if not np.isfinite(admm_rho) or admm_rho <= 0:
            raise ValueError("admm_rho must be finite and strictly positive")

    start = perf_counter()
    n, d = X.shape
    w = np.zeros(d)
    residual_scale = max(1.0, float(np.max(np.abs(X.T @ y / n))))
    if method == "CD":
        residual = y.copy()
        squared_norms = np.sum(X * X, axis=0) / n
    elif method == "FISTA":
        z = w.copy()
        t = 1.0
    elif method == "ADMM":
        # The normalized least-squares x update solves an SPD system even if X
        # is rank deficient, since rho is strictly positive.
        cross_product = X.T @ y / n
        system = X.T @ X / n
        system.flat[::d + 1] += admm_rho
        factor = cho_factor(system, lower=True, check_finite=False)
        u = np.zeros(d)
        primal_residual = dual_residual = 0.0
        diagnostics = [[0, primal_residual, dual_residual]]
    elif method != "ISTA":
        raise ValueError(method)
    objective, stationarity = evaluate(X, y, w, lam, L, residual_scale)
    setup_seconds = perf_counter() - start
    history = [[0, setup_seconds, objective, stationarity]]
    rounds = 0
    while stationarity > tol and rounds < max_rounds:
        if method == "ISTA":
            gradient = X.T @ (X @ w - y) / n
            w = soft_threshold(w - gradient / L, lam / L)
        elif method == "FISTA":
            gradient = X.T @ (X @ z - y) / n
            next_w = soft_threshold(z - gradient / L, lam / L)
            next_t = (1 + np.sqrt(1 + 4 * t * t)) / 2
            z = next_w + (t - 1) / next_t * (next_w - w)
            w, t = next_w, next_t
        elif method == "ADMM":
            previous_w = w
            x = cho_solve(factor, cross_product + admm_rho * (w - u),
                          check_finite=False)
            w = soft_threshold(x + u, lam / admm_rho)
            u = u + x - w
            primal_residual = float(np.linalg.norm(x - w))
            dual_residual = float(admm_rho * np.linalg.norm(w - previous_w))
            diagnostics.append([rounds + 1, primal_residual, dual_residual])
        else:
            for j in range(d):
                old = w[j]
                partial = residual + X[:, j] * old
                rho = X[:, j] @ partial / n
                w[j] = np.sign(rho) * max(abs(rho) - lam, 0.0) / squared_norms[j]
                residual = partial - X[:, j] * w[j]
        rounds += 1
        objective, stationarity = evaluate(X, y, w, lam, L, residual_scale)
        history.append([rounds, perf_counter() - start, objective, stationarity])
    elapsed = perf_counter() - start
    answer = {
        "w": w, "rounds": rounds, "elapsed_seconds": elapsed,
        "setup_seconds": setup_seconds,
        "iteration_seconds": elapsed - setup_seconds,
        "objective": objective, "residual": stationarity,
        "converged": stationarity <= tol, "history": np.asarray(history),
    }
    if method == "ADMM":
        answer.update({"admm_rho": admm_rho,
                       "primal_residual": primal_residual,
                       "dual_residual": dual_residual,
                       "diagnostic_history": np.asarray(diagnostics)})
    return answer
