"""Three basic solvers for ||Xw-y||^2/(2n) + lam*||w||_1."""
from time import perf_counter
import numpy as np


def soft_threshold(v, threshold):
    return np.sign(v) * np.maximum(np.abs(v) - threshold, 0.0)


def evaluate(X, y, w, lam, L, residual_scale):
    residual = X @ w - y
    objective = residual @ residual / (2 * len(y)) + lam * np.abs(w).sum()
    gradient = X.T @ residual / len(y)
    mapping = L * (w - soft_threshold(w - gradient / L, lam / L))
    return float(objective), float(np.max(np.abs(mapping)) / residual_scale)


def solve(X, y, lam, L, method, tol=1e-6, max_rounds=10000):
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
    elif method != "ISTA":
        raise ValueError(method)
    objective, stationarity = evaluate(X, y, w, lam, L, residual_scale)
    history = [[0, perf_counter() - start, objective, stationarity]]
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
    return {
        "w": w, "rounds": rounds, "elapsed_seconds": elapsed,
        "objective": objective, "residual": stationarity,
        "converged": stationarity <= tol, "history": np.asarray(history),
    }
