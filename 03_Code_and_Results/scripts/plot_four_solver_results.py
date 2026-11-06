"""Render four-solver report figures from saved results, without fitting models.

Run from the code package with:
    python scripts/plot_four_solver_results.py
The default source is results/2026-11-06-four-solvers.  Every chart is written as
vector PDF/SVG and a 220-dpi PNG; the same files are mirrored into 04_Figures.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import NullLocator, ScalarFormatter

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("ISTA", "FISTA", "CD", "ADMM")
COLORS = {"ISTA": "#2563A6", "FISTA": "#CF7A26", "CD": "#258365", "ADMM": "#805AB1"}
MARKERS = {"ISTA": "o", "FISTA": "s", "CD": "^", "ADMM": "D"}
LINESTYLES = {"ISTA": "-", "FISTA": "--", "CD": "-.", "ADMM": ":"}
FEATURE_COLORS = ["#2563A6", "#CF7A26", "#258365", "#805AB1", "#C34A76"]
TOL = 1e-6


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="results/2026-11-06-four-solvers")
    parser.add_argument("--output", default="output/figures/four_solvers")
    parser.add_argument("--no-mirror", action="store_true")
    args = parser.parse_args()
    source = (ROOT / args.results).resolve()
    target = (ROOT / args.output).resolve()
    mirror = ROOT.parent / "04_Figures" / "four_solvers"
    target.mkdir(parents=True, exist_ok=True)
    used: set[Path] = set()
    figures: list[dict] = []
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.titlesize": 10, "axes.labelsize": 9, "legend.fontsize": 8,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#777777", "axes.linewidth": .7,
        "grid.color": "#d5d9dd", "grid.alpha": .7, "grid.linewidth": .5,
        "lines.linewidth": 1.6, "lines.markersize": 4,
        "savefig.dpi": 220, "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.fonttype": "none", "axes.unicode_minus": True,
    })

    def read_csv(path):
        path = Path(path)
        used.add(path)
        with path.open(newline="", encoding="utf-8") as stream:
            return list(csv.DictReader(stream))

    def read_json(path):
        path = Path(path)
        used.add(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def read_npz(path):
        path = Path(path)
        used.add(path)
        with np.load(path) as data:
            return {k: data[k].copy() for k in data.files}

    def trace(path):
        rows = read_csv(path)
        return {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}

    def save(fig, name, description):
        record = {"name": name, "description": description, "files": []}
        for ext in ("pdf", "png", "svg"):
            path = target / f"{name}.{ext}"
            fig.savefig(path, bbox_inches="tight", pad_inches=.06,
                        metadata={"Creator": "COMP6704 Group 9 / matplotlib"} if ext == "pdf" else None)
            record["files"].append({"name": path.name, "bytes": path.stat().st_size,
                                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        plt.close(fig)
        figures.append(record)

    def grid(ax):
        ax.grid(True, axis="both")
        ax.set_axisbelow(True)

    def handles():
        return [Line2D([], [], color=COLORS[m], marker=MARKERS[m],
                       linestyle=LINESTYLES[m], label=m) for m in METHODS]

    def common_legend(fig):
        fig.legend(handles=handles(), loc="outside upper center", ncol=4, frameon=False)

    main_dir, extended = source / "main", source / "extended"
    timing = read_csv(main_dir / "timing_repeats.csv")
    main_rows = read_csv(main_dir / "optimization_results.csv")
    penalties = read_csv(main_dir / "regularization_results.csv")
    summary = read_json(extended / "summary.json")["summary"]
    for method in METHODS:
        if not any(row["method"] == method for row in main_rows):
            raise ValueError(f"Missing main benchmark method: {method}")
    dataset_names = ("synthetic_seed0", "diabetes")
    dataset_titles = ("Synthetic seed 0", "Diabetes fixed split")
    main_traces = {(name, method): trace(main_dir / f"trace_{name}_{method}.csv")
                   for name in dataset_names for method in METHODS}

    # Each history belongs to the repetition with the median solver time.
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.55), layout="constrained")
    for ax, name, title in zip(axes, dataset_names, dataset_titles):
        for method in METHODS:
            h = main_traces[(name, method)]
            ax.plot(h["seconds"] * 1000, h["objective"], color=COLORS[method],
                    linestyle=LINESTYLES[method], label=method)
        ax.set(title=title, xlabel="Elapsed solver time (ms)", ylabel="Training objective $F(w)$")
        grid(ax)
    common_legend(fig)
    save(fig, "convergence", "Objective against elapsed time on two fixed inputs; each curve uses the median-time repetition. ADMM setup and all methods' monitoring are included.")

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.55), layout="constrained")
    for ax, name, title in zip(axes, dataset_names, dataset_titles):
        for method in METHODS:
            h = main_traces[(name, method)]
            ax.semilogy(h["round"], np.maximum(h["residual"], 1e-14),
                        color=COLORS[method], linestyle=LINESTYLES[method])
        ax.axhline(TOL, color="#666666", linestyle="--", lw=.9)
        ax.set(title=title, xlabel="Rounds / complete CD sweeps", ylabel="Normalized stationarity $R$")
        grid(ax)
    common_legend(fig)
    save(fig, "stationarity", "Common original-objective stationarity residual versus rounds; one CD round is a full sweep. Dashed line: 1e-6. ADMM is evaluated at its returned z coefficients.")

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 3.8), layout="constrained")
    names = ("synthetic_seed0", "synthetic_seed1", "synthetic_seed2", "diabetes")
    for ax, name in zip(axes.flat, names):
        for x, method in enumerate(METHODS):
            points = np.array([float(row["time_seconds"]) * 1000 for row in timing
                               if row["dataset"] == name and row["method"] == method])
            if len(points) != 5:
                raise ValueError(f"Expected five timing repetitions for {name}/{method}")
            offsets = np.linspace(-.09, .09, len(points))
            ax.scatter(x + offsets, points, color=COLORS[method], s=17, alpha=.8, zorder=3)
            ax.plot([x - .23, x + .23], [np.median(points)] * 2,
                    color="#20252a", lw=1.8, zorder=4)
        ax.set(xticks=range(4), xticklabels=METHODS,
               title=name.replace("_", " ").capitalize(), ylabel="Solver time (ms)")
        ax.grid(True, axis="y")
        ax.set_axisbelow(True)
    save(fig, "timing_repetitions", "All five timings for each of the four main instances. Small horizontal offsets distinguish repetitions and carry no meaning; black bars show medians. Repetitions are not independent datasets.")

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.65), layout="constrained")
    for ax, group, title in zip(axes, ("synthetic", "diabetes"),
                                ("Synthetic: three instance medians", "Diabetes: one fixed split")):
        for x, method in enumerate(METHODS):
            vals = np.array([float(row["time_seconds"]) * 1000 for row in main_rows
                             if row["dataset"].startswith(group) and row["method"] == method])
            mean = float(vals.mean())
            err = float(vals.std(ddof=1)) if len(vals) > 1 else None
            ax.bar(x, mean, yerr=err, width=.62, color=COLORS[method], alpha=.9,
                   capsize=3, error_kw={"elinewidth": 1})
        ax.set(xticks=range(4), xticklabels=METHODS, title=title, ylabel="Solver time (ms)")
        ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "efficiency_summary", "Main benchmark solver times. Synthetic bars: means and sample SD of three instance medians, each from five repeats. Diabetes has a single split and no across-instance error bar.")

    def subset(study, method):
        return sorted([r for r in summary if r["study"] == study and r["method"] == method],
                      key=lambda r: float(r["parameter"]))

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 5.05), layout="constrained")
    correlations = [0., .5, .9, .99]
    for method in METHODS:
        rows = subset("correlation", method)
        for ax, field in zip(axes[0], ("time_ms", "rounds")):
            ax.errorbar(range(4), [float(r[field + "_mean"]) for r in rows],
                        yerr=[float(r[field + "_sd"]) for r in rows],
                        color=COLORS[method], marker=MARKERS[method], linestyle=LINESTYLES[method],
                        capsize=2.3, elinewidth=.8)
        h = trace(extended / f"trace_corr_0.99_seed10_{method}.csv")
        keep = h["round"] > 0
        axes[1, 0].loglog(h["round"][keep], np.maximum(h["residual"][keep], 1e-14),
                          color=COLORS[method], linestyle=LINESTYLES[method])
    for ax, title, ylabel in zip(axes[0], ("Time at common tolerance", "Rounds to common tolerance"),
                                ("Solver time (ms)", "Rounds / complete CD sweeps")):
        ax.set(xticks=range(4), xticklabels=["0", "0.5", "0.9", "0.99"],
               xlabel=r"Within-block correlation $\rho$", ylabel=ylabel, title=title, yscale="log")
        grid(ax)
    axes[1, 0].axhline(TOL, color="#666666", linestyle="--", lw=.9)
    axes[1, 0].set(title=r"$\rho=0.99$, seed 10", xlabel="Rounds / complete CD sweeps",
                   ylabel="Normalized stationarity $R$")
    grid(axes[1, 0])
    rows = subset("correlation", "ISTA")
    axes[1, 1].semilogy(range(4), [float(r["condition_mean"]) for r in rows],
                        "o-", color="#4b5563")
    axes[1, 1].set(xticks=range(4), xticklabels=["0", "0.5", "0.9", "0.99"],
                   xlabel=r"Within-block correlation $\rho$", ylabel=r"$\kappa(X^\top X/n)$",
                   title="Full-design curvature")
    grid(axes[1, 1]); common_legend(fig)
    save(fig, "correlation_comparison", "Paired block-correlation study. Time/round points show means and sample SD across three instances (five repeats per instance). Bottom left is seed 10 only; bottom right is the mean full-Gram condition number. Correlation levels are equally spaced categorical positions.")

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.65), layout="constrained")
    dimensions = [50, 100, 300, 600]
    for method in METHODS:
        rows = subset("scaling", method)
        for ax, field in zip(axes, ("time_ms", "rounds")):
            ax.errorbar(dimensions, [float(r[field + "_mean"]) for r in rows],
                        yerr=[float(r[field + "_sd"]) for r in rows],
                        color=COLORS[method], marker=MARKERS[method], linestyle=LINESTYLES[method],
                        capsize=2.3, elinewidth=.8)
    for ax, title, ylabel in zip(axes, ("Solver time", "Rounds to common tolerance"),
                                ("Solver time (ms)", "Rounds / complete CD sweeps")):
        ax.set(xscale="log", xticks=dimensions, xlabel="Features $d$ (800 training samples)",
               ylabel=ylabel, title=title)
        ax.xaxis.set_major_formatter(ScalarFormatter()); ax.xaxis.set_minor_locator(NullLocator()); grid(ax)
    axes[0].set_yscale("log"); common_legend(fig)
    save(fig, "dimension_comparison", "Independent-feature dimension study. Points show means and sample SD across three instance medians (five timings per instance). ADMM factorization is included; shared spectral setup is excluded.")

    manifest = read_json(ROOT / "data/manifest.json")
    synthetic_coef = np.array([read_npz(main_dir / f"coefficients_synthetic_seed{i}_CD.npz")["raw_w"]
                               for i in range(3)])
    diabetes_coef = read_npz(main_dir / "coefficients_diabetes_CD.npz")["standardized_w"]
    truth = np.array(manifest["synthetic_generation"]["true_coefficients"])
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.65), layout="constrained")
    indices = np.arange(min(10, synthetic_coef.shape[1]))
    axes[0].bar(indices - .18, truth[indices], width=.36, color="#9ca3af", label="Generating")
    axes[0].bar(indices + .18, synthetic_coef.mean(0)[indices], width=.36,
                yerr=synthetic_coef.std(0, ddof=1)[indices], capsize=2,
                color=COLORS["CD"], label="CD mean ± SD")
    axes[0].set(xticks=indices, xlabel="Feature index", ylabel="Coefficient (original units)",
                title="Synthetic: selection and shrinkage")
    axes[0].legend(fontsize=7.5, frameon=False)
    axes[1].bar(np.arange(len(diabetes_coef)), diabetes_coef, color=COLORS["CD"], width=.65)
    axes[1].set(xticks=np.arange(len(diabetes_coef)),
                xticklabels=manifest["datasets"]["diabetes"]["feature_columns"],
                ylabel="Coefficient (standardized units)", title="Diabetes fixed split")
    axes[1].tick_params(axis="x", labelrotation=45)
    for ax in axes: ax.axhline(0, color="#555555", lw=.6); grid(ax)
    save(fig, "coefficient_analysis", "CD coefficients at lambda/lambda_max=0.1. Synthetic panel shows generating values and mean ± sample SD over three instances in original units, displaying the first ten of fifty coefficients. Diabetes coefficients are standardized, with no known true support.")

    fig, axes = plt.subplots(2, 2, figsize=(6.6, 4.35), layout="constrained")
    ratios = sorted(set(float(r["lambda_ratio"]) for r in penalties))
    for col, prefix, title, color in ((0, "synthetic", "Synthetic: three instances", COLORS["ISTA"]),
                                      (1, "diabetes", "Diabetes fixed split", COLORS["FISTA"])):
        for row_idx, field, ylabel in ((0, "test_mse", "Test MSE"), (1, "nonzero", "Nonzero coefficients")):
            means, errors = [], []
            for ratio in ratios:
                values = np.array([float(r[field]) for r in penalties
                                   if r["dataset"].startswith(prefix) and float(r["lambda_ratio"]) == ratio])
                means.append(float(values.mean())); errors.append(float(values.std(ddof=1)) if len(values)>1 else 0.)
            ax = axes[row_idx, col]
            ax.errorbar(ratios, means, yerr=errors, fmt="o-", color=color, capsize=2)
            ax.set(xscale="log", xlabel=r"$\lambda/\lambda_{\max}$", ylabel=ylabel)
            if row_idx == 0: ax.set_title(title)
            grid(ax)
    save(fig, "regularization", "CD penalty sensitivity at four prespecified lambda ratios. Synthetic values are means and sample SD across three instances; Diabetes has one split. Test scores are descriptive and are not used to select lambda.")

    path_file = extended / "coefficient_path_data.json"
    if path_file.exists():
        paths = read_json(path_file)
        fig, axes = plt.subplots(2, 2, figsize=(6.6, 4.55), layout="constrained")
        for col, name, title in ((0, "synthetic_seed0", "Synthetic seed 0"),
                                 (1, "diabetes", "Diabetes fixed split")):
            data = paths[name]; x = np.array(data["ratios"]); coefs = np.array(data["coefficients"])
            active = list(range(5)) if col == 0 else list(np.flatnonzero(np.abs(coefs[data["ratios"].index(.1)]) > 1e-6))
            ax = axes[0, col]
            for j in range(coefs.shape[1]):
                if j not in active: ax.plot(x, coefs[:, j], color="#aab2bd", alpha=.45, lw=.7)
            for k, j in enumerate(active):
                ax.plot(x, coefs[:, j], color=FEATURE_COLORS[k], label=data["features"][j])
            ax.set(xscale="log", xlabel=r"$\lambda/\lambda_{\max}$", title=title,
                   ylabel="Original coefficient" if col == 0 else "Standardized coefficient")
            ax.legend(ncol=3, fontsize=6.8, frameon=False, loc="lower left" if col == 0 else "upper right")
            ax.axhline(0, color="#666666", lw=.6); grid(ax)
            ax = axes[1, col]
            ax.semilogx(x, data["train_mse"], color=COLORS["ISTA"], label="Training")
            ax.semilogx(x, data["test_mse"], color=COLORS["FISTA"], label="Test")
            ax.set(xlabel=r"$\lambda/\lambda_{\max}$", ylabel="MSE")
            ax.legend(frameon=False); grid(ax)
        save(fig, "coefficient_paths", "CD cold-start paths over 34 prespecified penalties. Colored synthetic curves correspond to the five true active coefficients; colored Diabetes curves are variables selected at ratio 0.1, not known ground truth. Gray curves are the remaining coefficients.")

    sensitivity_path = source / "sensitivity" / "sensitivity_results.csv"
    if sensitivity_path.exists():
        sensitivity = read_csv(sensitivity_path)
        grouped = []
        groups = [("synthetic_seed0", "Synthetic seed 0", COLORS["ISTA"]),
                  ("diabetes", "Diabetes fixed split", COLORS["FISTA"]),
                  ("corr_0.99", r"Correlation $\rho=0.99$: three instances", COLORS["ADMM"])]
        fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.85), layout="constrained")
        for prefix, label, color in groups:
            selected = [r for r in sensitivity if r["dataset"].startswith(prefix)]
            if not selected: continue
            rho_values = sorted(set(float(r["rho"]) for r in selected))
            for ax, field, multiplier in zip(axes, ("time_seconds", "rounds"), (1000, 1)):
                means, errors = [], []
                for rho in rho_values:
                    values = np.array([float(r[field]) * multiplier for r in selected if float(r["rho"]) == rho])
                    means.append(float(values.mean())); errors.append(float(values.std(ddof=1)) if len(values)>1 else 0.)
                ax.errorbar(rho_values, means, yerr=errors, fmt="o-", color=color,
                            capsize=2.5, label=label)
        for ax, title, ylabel in zip(axes, ("ADMM solver time", "ADMM rounds to tolerance"),
                                    ("Solver time (ms)", "ADMM rounds")):
            ax.set(xscale="log", yscale="log", xlabel=r"ADMM penalty $\beta$", title=title, ylabel=ylabel)
            ax.set_xticks([.1, 1., 10.]); ax.set_xticklabels(["0.1", "1", "10"])
            ax.xaxis.set_minor_locator(NullLocator()); grid(ax)
        fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center", ncol=1, frameon=False, fontsize=7.8)
        save(fig, "admm_penalty_sensitivity", "ADMM algorithmic-penalty sensitivity (beta, saved as rho in CSV), distinct from the model lambda. Each saved value is the median of three repeated cold starts. Correlated-design points show mean and sample SD across three instance medians; the two original inputs have no across-instance SD. Main comparisons prespecify beta=1.")
    else:
        raise FileNotFoundError(f"Required ADMM sensitivity results are missing: {sensitivity_path}")

    # A compact setup-cost visualization distinguishes factorization from iterations.
    if all("setup_seconds" in r for r in main_rows):
        fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.5), layout="constrained")
        for ax, prefix, title in zip(axes, ("synthetic", "diabetes"),
                                    ("Synthetic: mean of instance medians", "Diabetes fixed split")):
            selected = [r for r in main_rows if r["dataset"].startswith(prefix)]
            for x, method in enumerate(METHODS):
                rows = [r for r in selected if r["method"] == method]
                setup = float(np.mean([float(r["setup_seconds"]) * 1000 for r in rows]))
                total = float(np.mean([float(r["time_seconds"]) * 1000 for r in rows]))
                ax.bar(x, max(0., total - setup), color=COLORS[method], width=.65)
                ax.bar(x, setup, bottom=max(0., total - setup), color=COLORS[method],
                       width=.65, hatch="///", edgecolor="white", linewidth=.6, alpha=.65)
            ax.set(xticks=range(4), xticklabels=METHODS, title=title, ylabel="Solver time (ms)")
            ax.grid(True, axis="y"); ax.set_axisbelow(True)
        from matplotlib.patches import Patch
        fig.legend(handles=[Patch(facecolor="#777777", label="Iterations + monitoring"),
                            Patch(facecolor="#aaaaaa", hatch="///", edgecolor="white", label="Solver setup")],
                   loc="outside upper center", ncol=2, frameon=False)
        save(fig, "setup_cost", "Solver time decomposed into the saved solver-specific setup component and the remainder (iterations and monitoring). Main instance medians are summarized within each dataset family; ADMM setup includes Gram construction and Cholesky factorization.")

    # Provenance lists every numerical input consumed rather than relying on a fixed date.
    def relative(path):
        try: return path.relative_to(ROOT).as_posix()
        except ValueError: return str(path)
    provenance = {
        "generator": "scripts/plot_four_solver_results.py",
        "source_results": relative(source), "methods": list(METHODS), "colors": COLORS,
        "matplotlib_version": matplotlib.__version__, "numpy_version": np.__version__,
        "fit_models": False, "png_dpi": 220,
        "uncertainty": "Sample SD across three independent instance medians where applicable; timing repeats are not independent datasets.",
        "inputs": [{"path": relative(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                   for p in sorted(used)],
        "figures": figures,
    }
    (target / "figure_manifest.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    readme = ("FOUR-SOLVER FIGURES — COMP6704 Group 9\n\n"
              "Generated only from saved numerical records, with no optimizer calls.\n"
              "Run: python scripts/plot_four_solver_results.py\n"
              "Each chart is available as vector PDF/SVG and a 220-dpi PNG.\n"
              "Colors: ISTA blue; FISTA orange; cyclic CD green; ADMM purple.\n"
              "R is the common proximal-gradient stationarity residual for the original Lasso objective.\n"
              "ADMM beta is called rho in the numerical CSVs and is distinct from correlation rho and model lambda.\n"
              "Solver-specific setup and monitoring are included in solver times; shared spectral setup is excluded.\n"
              "Five timing repetitions yield one instance median in the main and extended benchmarks.\n"
              "Error bars show sample SD across three instances where indicated, not timing uncertainty.\n"
              "Sensitivity uses three timing repetitions per instance and beta setting.\n"
              "The machine-readable figure_manifest.json records all consumed input hashes and output hashes.\n\n"
              + "\n".join(f"{f['name']}: {f['description']}" for f in figures) + "\n")
    (target / "README.txt").write_text(readme, encoding="utf-8")
    if not args.no_mirror:
        mirror.mkdir(parents=True, exist_ok=True)
        for record in figures:
            for item in record["files"]: shutil.copy2(target / item["name"], mirror / item["name"])
        for name in ("figure_manifest.json", "README.txt"): shutil.copy2(target / name, mirror / name)
    print(f"Rendered {len(figures)} figure groups to {target}")
    if not args.no_mirror: print(f"Mirrored figures to {mirror}")


if __name__ == "__main__":
    main()
