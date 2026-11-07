"""Numerical validation of the four solvers, especially normalized ADMM.

Run from 02_Code_and_Results with:
    python -m unittest discover -s tests -v
These are correctness checks, not timing or solver-ranking tests.
"""
from pathlib import Path
import sys
import unittest

import numpy as np
from sklearn.linear_model import Lasso

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from optimizers import evaluate, soft_threshold, solve


METHODS = ("ISTA", "FISTA", "CD", "ADMM")


class SolverValidation(unittest.TestCase):
    @staticmethod
    def problem(seed=29):
        rng = np.random.default_rng(seed)
        X = rng.normal(size=(90, 14))
        X[:, 1] += 0.6 * X[:, 0]
        X = (X - X.mean(axis=0)) / X.std(axis=0)
        truth = np.r_[2.0, -1.5, 0.7, np.zeros(11)]
        y = X @ truth + 0.1 * rng.normal(size=len(X))
        y -= y.mean()
        L = float(np.linalg.norm(X, 2) ** 2 / len(y))
        maximum = float(np.max(np.abs(X.T @ y / len(y))))
        return X, y, L, maximum

    def test_orthogonal_closed_form_for_every_solver(self):
        rng = np.random.default_rng(123)
        Q, _ = np.linalg.qr(rng.normal(size=(64, 8)))
        X = np.sqrt(64) * Q
        v = np.array([1.2, -0.4, 0.1, 2.0, -1.0, 0.0, 0.25, -0.8])
        y = X @ v
        L = float(np.linalg.norm(X, 2) ** 2 / len(y))
        expected = soft_threshold(v, 0.3)
        for method in METHODS:
            with self.subTest(method=method):
                result = solve(X, y, 0.3, L, method, tol=1e-11)
                self.assertTrue(result["converged"])
                np.testing.assert_allclose(result["w"], expected, atol=2e-10, rtol=0)

    def test_admm_first_round_uses_normalized_system_and_returns_z(self):
        X, y, L, maximum = self.problem()
        lam, rho = 0.1 * maximum, 0.4
        x = np.linalg.solve(X.T @ X / len(y) + rho * np.eye(X.shape[1]),
                            X.T @ y / len(y))
        expected = soft_threshold(x, lam / rho)
        result = solve(X, y, lam, L, "ADMM", tol=1e-14, max_rounds=1,
                       admm_rho=rho)
        self.assertEqual(result["rounds"], 1)
        np.testing.assert_allclose(result["w"], expected, rtol=1e-12, atol=1e-12)
        objective, residual = evaluate(X, y, expected, lam, L, max(1.0, maximum))
        self.assertAlmostEqual(result["objective"], objective, places=12)
        self.assertAlmostEqual(result["residual"], residual, places=12)
        self.assertAlmostEqual(result["primal_residual"], np.linalg.norm(x - expected), places=12)
        self.assertAlmostEqual(result["dual_residual"], rho * np.linalg.norm(expected), places=12)

    def test_nonorthogonal_reference_and_rho_sensitivity(self):
        X, y, L, maximum = self.problem()
        lam = 0.1 * maximum
        reference = Lasso(alpha=lam, fit_intercept=False, tol=1e-13,
                          max_iter=100000, selection="cyclic").fit(X, y)
        reference_objective, _ = evaluate(X, y, reference.coef_, lam, L, max(1, maximum))
        for rho in (0.1, 1.0, 10.0):
            with self.subTest(rho=rho):
                result = solve(X, y, lam, L, "ADMM", tol=1e-10, admm_rho=rho)
                self.assertTrue(result["converged"])
                np.testing.assert_allclose(result["w"], reference.coef_, atol=2e-8, rtol=0)
                self.assertLess(abs(result["objective"] - reference_objective), 1e-9)
                self.assertEqual(result["diagnostic_history"].shape, (result["rounds"] + 1, 3))
                self.assertEqual(result["history"].shape, (result["rounds"] + 1, 4))
                self.assertGreaterEqual(result["setup_seconds"], 0)
                self.assertGreaterEqual(result["iteration_seconds"], 0)
                self.assertAlmostEqual(result["setup_seconds"] + result["iteration_seconds"],
                                       result["elapsed_seconds"], places=14)
                self.assertTrue(np.all(np.diff(result["history"][:, 1]) >= 0))

    def test_lambda_max_stops_at_zero_for_all_methods(self):
        X, y, L, maximum = self.problem()
        for method in METHODS:
            with self.subTest(method=method):
                result = solve(X, y, 1.1 * maximum, L, method)
                self.assertTrue(result["converged"])
                self.assertEqual(result["rounds"], 0)
                np.testing.assert_array_equal(result["w"], np.zeros(X.shape[1]))

    def test_rank_deficient_underdetermined_admm(self):
        rng = np.random.default_rng(7)
        X = rng.normal(size=(18, 30))
        X[:, -1] = X[:, 0]
        y = X[:, 0] - 0.5 * X[:, 1] + 0.1 * rng.normal(size=len(X))
        L = float(np.linalg.norm(X, 2) ** 2 / len(y))
        maximum = float(np.max(np.abs(X.T @ y / len(y))))
        lam = 0.2 * maximum
        reference = Lasso(alpha=lam, fit_intercept=False, tol=1e-12,
                          max_iter=100000, selection="cyclic").fit(X, y)
        reference_objective, _ = evaluate(X, y, reference.coef_, lam, L, max(1, maximum))
        result = solve(X, y, lam, L, "ADMM", tol=1e-10)
        self.assertTrue(result["converged"])
        self.assertLess(abs(result["objective"] - reference_objective), 1e-9)
        np.testing.assert_allclose(X @ result["w"], X @ reference.coef_, atol=2e-8, rtol=0)

    def test_invalid_admm_rho(self):
        X, y, L, maximum = self.problem()
        for rho in (0.0, -1.0, np.nan, np.inf):
            with self.subTest(rho=rho):
                with self.assertRaisesRegex(ValueError, "admm_rho"):
                    solve(X, y, 0.1 * maximum, L, "ADMM", admm_rho=rho)


if __name__ == "__main__":
    unittest.main()
