"""Validate four Lasso solvers, then execute the prespecified common-tolerance benchmark."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"
sys.path.insert(0, str(ROOT / "src"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sklearn
import scipy
from sklearn.linear_model import Lasso
from threadpoolctl import threadpool_info, threadpool_limits
from optimizers import soft_threshold, solve, evaluate

METHODS = ("ISTA", "FISTA", "CD", "ADMM")
COLORS = {"ISTA": "#2563eb", "FISTA": "#d97706", "CD": "#15803d", "ADMM": "#805AB1"}
CONFIG = {
    "main_lambda_ratio": 0.1, "lambda_ratios": [0.01, 0.1, 0.5, 1.0],
    "tolerance": 1e-6, "max_rounds": 10000, "timing_repeats": 5,
    "nonzero_threshold": 1e-6, "blas_threads": 1,
    "objective": "squared_loss/(2*n) + lambda*L1",
    "methods": list(METHODS), "admm_rho": 1.0,
    "timing_includes": "solver setup, factorization if applicable, updates, objective/history and common residual",
    "timing_excludes": "data loading, preprocessing, shared spectral calculation and plotting",
}


def load_data(name, record):
    path = ROOT / "data" / record["file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    X = np.array([[float(row[c]) for c in record["feature_columns"]] for row in rows])
    y = np.array([float(row["target"]) for row in rows])
    train = np.array([row["split"] == "train" for row in rows])
    mean, std = X[train].mean(axis=0), X[train].std(axis=0, ddof=0)
    keep = std > 0
    Xt = np.ascontiguousarray((X[train][:, keep] - mean[keep]) / std[keep])
    Xtest = np.ascontiguousarray((X[~train][:, keep] - mean[keep]) / std[keep])
    ymean = float(y[train].mean())
    yt = np.ascontiguousarray(y[train] - ymean)
    begin = perf_counter()
    L = float(np.linalg.norm(Xt, ord=2) ** 2 / len(yt))
    spectral_seconds = perf_counter() - begin
    maximum = float(np.max(np.abs(Xt.T @ yt / len(yt))))
    return {
        "name": name, "X": Xt, "y": yt, "Xtest": Xtest, "ytest": y[~train],
        "ymean": ymean, "std": std[keep], "keep": keep, "L": L,
        "lambda_max": maximum, "spectral_seconds": spectral_seconds,
        "train_samples": int(train.sum()), "test_samples": int((~train).sum()),
    }


def validate(data):
    checks = {}
    rng = np.random.default_rng(123)
    Q, _ = np.linalg.qr(rng.normal(size=(64, 8)))
    X = Q * np.sqrt(64)
    v = np.array([1.2, -0.4, 0.1, 2.0, -1.0, 0.0, 0.25, -0.8])
    y = X @ v
    L = float(np.linalg.norm(X, ord=2) ** 2 / len(y))
    expected = soft_threshold(v, 0.3)
    for method in METHODS:
        answer = solve(X, y, 0.3, L, method, tol=1e-10)
        error = float(np.max(np.abs(answer["w"] - expected)))
        assert error < 1e-9, (method, error)
        checks[f"orthogonal_{method}"] = {"max_coefficient_error": error}
    lam = 0.1 * data["lambda_max"]
    reference = Lasso(alpha=lam, fit_intercept=False, tol=1e-12,
                      max_iter=100000, selection="cyclic").fit(data["X"], data["y"])
    scale = max(1.0, data["lambda_max"])
    ref_objective, ref_residual = evaluate(
        data["X"], data["y"], reference.coef_, lam, data["L"], scale)
    assert ref_residual < 1e-8
    checks["reference"] = {"objective": ref_objective, "residual": ref_residual,
                           "dual_gap": float(reference.dual_gap_)}
    for method in METHODS:
        answer = solve(data["X"], data["y"], lam, data["L"], method)
        relative_difference = abs(answer["objective"]-ref_objective)/max(1,abs(ref_objective))
        assert answer["converged"] and relative_difference < 1e-8
        checks[f"reference_{method}"] = {
            "max_coefficient_error": float(np.max(np.abs(answer["w"]-reference.coef_))),
            "relative_objective_difference": relative_difference,
            "residual": answer["residual"],
        }
    return checks


def write_csv(path, records):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def plot_outputs(output, rows, solutions, traces, penalties, manifest):
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 160})
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    for ax, name in zip(axes, ("synthetic_seed0", "diabetes")):
        for method in METHODS:
            h = traces[(name, method)]
            ax.plot(h[:, 1]*1000, h[:, 2], label=method, color=COLORS[method])
        ax.set(title=name.replace("_", " "), xlabel="Elapsed time (ms)",
               ylabel="Training objective F")
        ax.grid(alpha=0.2)
        ax.legend()
    fig.savefig(output/"convergence.png")
    fig.savefig(output/"convergence.pdf")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    for ax, name in zip(axes, ("synthetic_seed0", "diabetes")):
        for method in METHODS:
            h = traces[(name, method)]
            ax.semilogy(h[:, 0], np.maximum(h[:, 3], 1e-16),
                        label=method, color=COLORS[method])
        ax.axhline(1e-6, color="gray", linestyle="--", linewidth=1)
        ax.set(title=name.replace("_", " "), xlabel="Iterations / complete CD sweeps",
               ylabel="Normalized residual R")
        ax.grid(alpha=0.2)
        ax.legend()
    fig.savefig(output/"stationarity.png")
    fig.savefig(output/"stationarity.pdf")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    ratios = CONFIG["lambda_ratios"]
    for name, label, color in [("synthetic", "Synthetic mean (3 instances)", "#2563eb"),
                                ("diabetes", "Diabetes fixed split", "#d97706")]:
        subset = [r for r in penalties if r["dataset"].startswith(name)]
        mse, nnz = [], []
        for ratio in ratios:
            selected = [r for r in subset if r["lambda_ratio"]==ratio]
            mse.append(float(np.mean([r["test_mse"] for r in selected])))
            nnz.append(float(np.mean([r["nonzero"] for r in selected])))
        # MSE has different target scales, so each curve has its own panel.
        ax = axes[0 if name=="synthetic" else 1]
        ax.semilogx(ratios, mse, "o-", color=color, label="Test MSE")
        ax.set(title=label, xlabel="lambda / lambda_max", ylabel="Test MSE")
        twin=ax.twinx()
        twin.semilogx(ratios, nnz, "s--", color="#15803d", label="Nonzero")
        twin.set_ylabel("Nonzero coefficients", color="#15803d")
        ax.grid(alpha=0.2)
    fig.savefig(output/"regularization.png")
    fig.savefig(output/"regularization.pdf")
    plt.close(fig)
    fig, ax=plt.subplots(figsize=(9,3.5), constrained_layout=True)
    truth=np.array(manifest["synthetic_generation"]["true_coefficients"])
    ax.plot(truth,"o",color="#111827",label="True coefficient",markersize=4)
    for method in METHODS:
        ax.plot(solutions[("synthetic_seed0",method)]["raw_w"],"-",
                color=COLORS[method],label=method,alpha=0.8)
    ax.set(xlabel="Feature index",ylabel="Coefficient in original units",
           title="Synthetic seed 0 at lambda / lambda_max = 0.1")
    ax.legend(ncol=4)
    ax.grid(alpha=0.2)
    fig.savefig(output/"coefficients.png")
    fig.savefig(output/"coefficients.pdf")
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", default="results/2026-11-06-four-solvers/main")
    args=parser.parse_args()
    output=(ROOT/args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest=json.loads((ROOT/"data/manifest.json").read_text())
    shutil.copy2(ROOT/"report.tex", output/"report_before_experiments.tex")
    shutil.copy2(ROOT/"experiment_plan_admm.md", output/"protocol_before_experiments.md")
    source_output = output/"source"
    source_output.mkdir()
    source_paths = ["src/optimizers.py", "scripts/run_experiments.py", "scripts/run_extended_experiments.py", "scripts/run_admm_sensitivity.py", "requirements-admm.txt", "experiment_plan_admm.md"]
    for relative in source_paths:
        shutil.copy2(ROOT/relative, source_output/Path(relative).name)
    (source_output/"sha256.json").write_text(json.dumps({relative:hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() for relative in source_paths},indent=2)+"\n")
    raw, all_rows, penalties, traces, solutions=[], [], [], {}, {}
    with threadpool_limits(limits=1):
        datasets={name:load_data(name,record) for name,record in manifest["datasets"].items()}
        checks=validate(datasets["synthetic_seed0"])
        (output/"validation.json").write_text(json.dumps(checks,indent=2)+"\n")
        print("Analytic and scikit-learn reference checks passed.", flush=True)
        for name,data in datasets.items():
            X,y,L=data["X"],data["y"],data["L"]
            lam=CONFIG["main_lambda_ratio"]*data["lambda_max"]
            answers={method:[] for method in METHODS}
            for repeat in range(CONFIG["timing_repeats"]):
                # Interleave methods by repeat to avoid a fixed warm-up ordering.
                for method in METHODS[repeat%len(METHODS):]+METHODS[:repeat%len(METHODS)]:
                    ans=solve(X,y,lam,L,method,CONFIG["tolerance"],CONFIG["max_rounds"])
                    answers[method].append(ans)
                    mse=float(np.mean((data["Xtest"]@ans["w"]+data["ymean"]-data["ytest"])**2))
                    raw.append({"dataset":name,"method":method,"repeat":repeat,
                                "time_seconds":ans["elapsed_seconds"],"setup_seconds":ans["setup_seconds"],
                                "iteration_seconds":ans["iteration_seconds"],"rounds":ans["rounds"],
                                "objective":ans["objective"],"residual":ans["residual"],
                                "test_mse":mse,"nonzero":int(np.sum(np.abs(ans["w"])>1e-6)),
                                "converged":ans["converged"]})
            for method in METHODS:
                times=np.array([a["elapsed_seconds"] for a in answers[method]])
                representative=answers[method][int(np.argsort(times)[len(times)//2])]
                row=next(r.copy() for r in raw if r["dataset"]==name and r["method"]==method)
                row.pop("repeat")
                row["time_seconds"]=float(np.median(times))
                row["minimum_time_seconds"]=float(times.min())
                row["maximum_time_seconds"]=float(times.max())
                row["setup_seconds"]=representative["setup_seconds"]
                row["iteration_seconds"]=representative["iteration_seconds"]
                if method=="ADMM":
                    write_csv(output/f"admm_diagnostics_{name}.csv", [dict(zip(["round","primal_l2","dual_l2"],v)) for v in representative["diagnostic_history"]])
                all_rows.append(row)
                traces[(name,method)]=representative["history"]
                write_csv(output/f"trace_{name}_{method}.csv",
                    [dict(zip(["round","seconds","objective","residual"],v)) for v in representative["history"]])
                raw_w=np.zeros(data["keep"].shape[0])
                raw_w[data["keep"]]=representative["w"]/data["std"]
                solutions[(name,method)]={"standardized_w":representative["w"],"raw_w":raw_w}
                np.savez(output/f"coefficients_{name}_{method}.npz",**solutions[(name,method)])
                print(f"{name:18s} {method:5s} {row['rounds']:4d} rounds  "
                      f"{1000*row['time_seconds']:.3f} ms  R={row['residual']:.2g}  "
                      f"MSE={row['test_mse']:.5g}",flush=True)
            for ratio in CONFIG["lambda_ratios"]:
                ans=solve(X,y,ratio*data["lambda_max"],L,"CD")
                penalties.append({"dataset":name,"lambda_ratio":ratio,
                    "lambda":ratio*data["lambda_max"],"objective":ans["objective"],
                    "residual":ans["residual"],"rounds":ans["rounds"],
                    "converged":ans["converged"],
                    "test_mse":float(np.mean((data["Xtest"]@ans["w"]+data["ymean"]-data["ytest"])**2)),
                    "nonzero":int(np.sum(np.abs(ans["w"])>1e-6))})
        env={"python":platform.python_version(),"platform":platform.platform(),
             "machine":platform.machine(),"numpy":np.__version__,
             "sklearn":sklearn.__version__,"scipy":scipy.__version__,"matplotlib":matplotlib.__version__,
             "source_sha256":{relative:hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() for relative in source_paths},
             "threadpools":threadpool_info(),"configuration":CONFIG,
             "datasets":{name:{"L":d["L"],"lambda_max":d["lambda_max"],
                    "spectral_seconds":d["spectral_seconds"],
                    "train_samples":d["train_samples"],"test_samples":d["test_samples"]}
                         for name,d in datasets.items()},
             "input_checksums":{name:r["sha256"] for name,r in manifest["datasets"].items()}}
        (output/"run_config.json").write_text(json.dumps(env,indent=2)+"\n")
        write_csv(output/"timing_repeats.csv",raw)
        write_csv(output/"optimization_results.csv",all_rows)
        write_csv(output/"regularization_results.csv",penalties)
        assert all(r["converged"] for r in all_rows+penalties), "A run did not converge"
        plot_outputs(output,all_rows,solutions,traces,penalties,manifest)
    print(f"Saved completed experiments to {output}",flush=True)


if __name__=="__main__":
    main()
