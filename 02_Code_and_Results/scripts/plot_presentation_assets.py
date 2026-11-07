"""Large-label presentation charts rendered only from saved Lasso results.

Usage: python scripts/plot_presentation_assets.py
No optimizer is imported and no model is fitted. Figures use the recorded
2026-11-06 four-solver run; they are distinct from compact report figures.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent.parent
ISOLATED_DEPENDENCIES = WORKSPACE / "work" / "ppt_plot_deps"
if ISOLATED_DEPENDENCIES.is_dir():
    sys.path.insert(0, str(ISOLATED_DEPENDENCIES))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib-presentation"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import NullLocator, ScalarFormatter

METHODS = ("ISTA", "FISTA", "CD", "ADMM")
COLORS = {"ISTA": "#2563A6", "FISTA": "#CF7A26", "CD": "#258365", "ADMM": "#805AB1"}
MARKERS = {"ISTA": "o", "FISTA": "s", "CD": "^", "ADMM": "D"}
STYLES = {"ISTA": "-", "FISTA": "--", "CD": "-.", "ADMM": ":"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default="results/2026-11-06-four-solvers")
    parser.add_argument("--output", default="output/figures/presentation_four_solvers")
    parser.add_argument("--no-mirror", action="store_true")
    args = parser.parse_args()
    source = (ROOT / args.results).resolve()
    target = (ROOT / args.output).resolve()
    mirror = ROOT.parent / "03_Figures" / "presentation_four_solvers"
    target.mkdir(parents=True, exist_ok=True)
    main_dir, extended = source / "main", source / "extended"
    used: set[Path] = set()
    records = []
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 16,
        "axes.labelsize": 16, "axes.titlesize": 16,
        "xtick.labelsize": 14, "ytick.labelsize": 14,
        "legend.fontsize": 13, "axes.spines.top": False,
        "axes.spines.right": False, "axes.edgecolor": "#888888",
        "axes.linewidth": .9, "grid.color": "#d6dbe0",
        "grid.linewidth": .65, "grid.alpha": .7,
        "lines.linewidth": 2.4, "lines.markersize": 7,
        "savefig.dpi": 220, "savefig.facecolor": "white",
        "figure.facecolor": "white", "axes.facecolor": "white",
        "pdf.fonttype": 42, "svg.fonttype": "none",
    })

    def csv_rows(path):
        used.add(path)
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def json_data(path):
        used.add(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def npz_data(path):
        used.add(path)
        with np.load(path) as data:
            return {key: data[key].copy() for key in data.files}

    def trace(path):
        rows = csv_rows(path)
        return {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}

    def save(fig, name, caption):
        item = {"name": name, "caption": caption, "files": []}
        for ext in ("png", "svg", "pdf"):
            path = target / f"{name}.{ext}"
            fig.savefig(path, bbox_inches="tight", pad_inches=.08)
            item["files"].append({"name": path.name, "bytes": path.stat().st_size,
                                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        records.append(item)
        plt.close(fig)

    def grid(ax):
        ax.grid(True)
        ax.set_axisbelow(True)

    def method_handles(methods=METHODS):
        return [Line2D([], [], color=COLORS[m], marker=MARKERS[m],
                       linestyle=STYLES[m], label=m, lw=2.4) for m in methods]

    def method_legend(fig, methods=METHODS):
        fig.legend(handles=method_handles(methods), loc="outside upper center",
                   ncol=len(methods), frameon=False, fontsize=14)

    def figure(two=False, tall=False):
        if two:
            return plt.subplots(1, 2, figsize=(12, 3.7), layout="constrained")
        return plt.subplots(figsize=(6.4, 4.0 if tall else 3.6), layout="constrained")

    summary = json_data(extended / "summary.json")["summary"]
    main_rows = csv_rows(main_dir / "optimization_results.csv")
    repeats = csv_rows(main_dir / "timing_repeats.csv")
    extended_rows = csv_rows(extended / "optimization_results.csv")
    penalties = csv_rows(main_dir / "regularization_results.csv")
    manifest = json_data(ROOT / "data/manifest.json")
    truth = np.array(manifest["synthetic_generation"]["true_coefficients"])
    selected_names = ("synthetic_seed0", "diabetes")
    selected_titles = ("Synthetic seed 0", "Diabetes: fixed split")
    main_traces = {(n, m): trace(main_dir / f"trace_{n}_{m}.csv")
                   for n in selected_names for m in METHODS}

    fig, ax = figure()
    ax.bar(np.arange(len(truth)), truth, width=.8, color=COLORS["ISTA"])
    ax.axhline(0, color="#666666", lw=.8)
    ax.set(xlabel="Feature index", ylabel="Generating coefficient", xlim=(-1, 50),
           xticks=[0, 10, 20, 30, 40, 49])
    ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "truth_support", "Known synthetic generating coefficients: five active variables among fifty candidates. This is data-generation input, not an estimated result.")

    fig, ax = figure()
    x = np.linspace(-2, 2, 401); tau = .5
    y = np.sign(x) * np.maximum(np.abs(x) - tau, 0.)
    ax.plot(x, x, color="#b4bbc2", lw=1.6, label="No penalty")
    ax.plot(x, y, color=COLORS["ISTA"], lw=3, label=r"$\tau=0.5$")
    ax.axvspan(-tau, tau, color=COLORS["ISTA"], alpha=.08)
    ax.axhline(0, color="#777777", lw=.7); ax.axvline(0, color="#777777", lw=.7)
    ax.set(xlabel="Input $v$", ylabel=r"Soft threshold $S_\tau(v)$", xlim=(-2, 2), ylim=(-2, 2))
    ax.legend(frameon=False, loc="upper left", fontsize=13); grid(ax)
    save(fig, "soft_threshold", "Analytic soft-threshold function with tau=0.5, generated directly from its definition rather than experimental fits.")

    fig, axes = figure(two=True)
    for ax, prefix, title in zip(axes, ("synthetic", "diabetes"),
                                 ("Synthetic: three instances", "Diabetes: fixed split")):
        for x, method in enumerate(METHODS):
            rows = [r for r in main_rows if r["dataset"].startswith(prefix) and r["method"] == method]
            vals = np.array([float(r["time_seconds"]) * 1000 for r in rows])
            height = float(vals.mean()); sd = float(vals.std(ddof=1)) if len(vals)>1 else 0.
            ax.bar(x, height, color=COLORS[method], width=.62, alpha=.92)
            if sd: ax.errorbar(x, height, yerr=sd, color="#26313a", fmt="none", capsize=4, lw=1.2)
            if prefix == "diabetes":
                raw = np.array([float(r["time_seconds"]) * 1000 for r in repeats
                                if r["dataset"] == "diabetes" and r["method"] == method])
                ax.scatter(x+np.linspace(-.08, .08, len(raw)), raw, s=20, color="#1f2937", alpha=.5, zorder=4)
            ax.text(x, height + sd + .025 * max(1., height), f"{height:.3f}",
                    ha="center", va="bottom", fontsize=14)
        ax.set(xticks=range(4), xticklabels=METHODS, ylabel="Solver time (ms)", title=title)
        ax.set_ylim(0, ax.get_ylim()[1]*1.13); ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "main_runtime", "All four solvers rerun on the same host. Synthetic bars: mean ± sample SD over three instance medians (five repeats per instance). Diabetes bars: median of five repeats, with all five timing points shown. Solver setup and monitoring are included; shared spectral setup is excluded.")

    for mode in ("convergence", "stationarity"):
        fig, axes = figure(two=True)
        for ax, name, title in zip(axes, selected_names, selected_titles):
            for method in METHODS:
                h = main_traces[(name, method)]
                if mode == "convergence":
                    ax.plot(h["seconds"]*1000, h["objective"], color=COLORS[method], linestyle=STYLES[method])
                else:
                    ax.semilogy(h["round"], np.maximum(h["residual"], 1e-14),
                                color=COLORS[method], linestyle=STYLES[method])
            ax.set_title(title)
            if mode == "convergence":
                ax.set(xlabel="Elapsed solver time (ms)", ylabel="Original objective $F(w)$")
            else:
                ax.axhline(1e-6, color="#666666", lw=1, ls="--")
                ax.set(xlabel="Rounds / complete CD sweeps", ylabel="Normalized stationarity $R$")
                ax.set_yticks([1, 1e-2, 1e-4, 1e-6])
            grid(ax)
        method_legend(fig)
        save(fig, mode, ("Original unsplit objective versus elapsed solver time; median-time repetition on each input. ADMM is evaluated at z, so its displayed value is F(z), not a mixed split objective." if mode == "convergence" else "Common original-objective stationarity versus rounds; median-time repetition. ADMM is evaluated at z. One CD round is a full sweep. Dashed horizontal line: R=1e-6."))

    def aggregate(study, method):
        return sorted([r for r in summary if r["study"] == study and r["method"] == method],
                      key=lambda r: float(r["parameter"]))

    fig, ax = figure(tall=True)
    for method in METHODS:
        rows = aggregate("correlation", method)
        ax.errorbar(range(4), [float(r["time_ms_mean"]) for r in rows],
                    yerr=[float(r["time_ms_sd"]) for r in rows],
                    marker=MARKERS[method], color=COLORS[method], linestyle=STYLES[method], capsize=3, lw=2.3)
    ax.set(xticks=range(4), xticklabels=["0", "0.5", "0.9", "0.99"],
           xlabel=r"Within-block correlation $\rho$", ylabel="Solver time (ms)", yscale="log")
    grid(ax); method_legend(fig)
    save(fig, "correlation_time", "Block-correlation study: means and sample SD across three instance medians, five repeats each. Correlation levels are shown at equally spaced categorical positions. Logarithmic time axis.")

    fig, ax = figure()
    seeds = [10, 11, 12]; width = .31
    for shift, method in ((-.5, "FISTA"), (.5, "ADMM")):
        rows = [next(r for r in extended_rows if r["study"]=="correlation" and
                     float(r["parameter"])==.99 and int(r["seed"])==seed and r["method"]==method) for seed in seeds]
        heights = np.array([float(r["time_ms"]) for r in rows])
        bars = ax.bar(np.arange(3)+shift*width, heights, width=width, color=COLORS[method], label=method)
        for bar, height in zip(bars, heights):
            ax.text(bar.get_x()+bar.get_width()/2, height+.8, f"{height:.1f}",
                    ha="center", va="bottom", fontsize=13)
    ax.set(xticks=range(3), xticklabels=["Seed 10", "Seed 11", "Seed 12"],
           ylabel="Median solver time (ms)")
    ax.set_ylim(0, ax.get_ylim()[1]*1.15); ax.legend(frameon=False, ncol=2, fontsize=14)
    ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "correlation_seed_times", "FISTA and ADMM timing medians for the three individual instances at within-block correlation 0.99. Each bar is one five-repeat median; these bars reveal across-instance variation, not uncertainty within a timing repetition.")

    fig, ax = figure(tall=True)
    dimensions = [50, 100, 300, 600]
    for method in METHODS:
        rows = aggregate("scaling", method)
        ax.errorbar(dimensions, [float(r["time_ms_mean"]) for r in rows],
                    yerr=[float(r["time_ms_sd"]) for r in rows],
                    marker=MARKERS[method], color=COLORS[method], linestyle=STYLES[method], capsize=3)
    ax.set(xscale="log", yscale="log", xticks=dimensions, xlabel="Features $d$", ylabel="Solver time (ms)")
    ax.xaxis.set_major_formatter(ScalarFormatter()); ax.xaxis.set_minor_locator(NullLocator())
    grid(ax); method_legend(fig)
    save(fig, "dimension_time", "Independent-feature dimension study with 800 training samples. Means and sample SD across three instance medians, five repeats each. Both axes are logarithmic. ADMM factorization is included in solver time.")

    fig, ax = figure()
    rows = aggregate("scaling", "ADMM")
    setup = np.array([float(r["setup_ms_mean"]) for r in rows])
    iteration = np.array([float(r["iteration_ms_mean"]) for r in rows])
    ax.bar(range(4), iteration, color=COLORS["ADMM"], width=.62, label="Iterations + monitoring")
    ax.bar(range(4), setup, bottom=iteration, color="#b7a2d1", width=.62,
           hatch="///", edgecolor="white", label="Setup + factorization")
    for i, (a, b) in enumerate(zip(setup, iteration)):
        ax.text(i, a+b+.035*max(setup+iteration), f"{100*a/(a+b):.0f}% setup",
                ha="center", va="bottom", fontsize=12.5)
    ax.set(xticks=range(4), xticklabels=dimensions, xlabel="Features $d$", ylabel="ADMM solver time (ms)")
    ax.set_ylim(0, ax.get_ylim()[1]*1.2)
    ax.legend(frameon=False, fontsize=12, loc="upper left")
    ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "admm_setup", "ADMM mean solver times split into paired saved setup and iteration components across three instance medians. Setup includes Gram construction and Cholesky factorization. Percent labels are the setup share of total time; shared spectral setup remains excluded.")

    sensitivity = csv_rows(source / "sensitivity/sensitivity_results.csv")
    fig, axes = figure(two=True)
    for prefix, label, color, marker in (("synthetic_seed0", "Synthetic seed 0", COLORS["ISTA"], "o"),
                                          ("diabetes", "Diabetes", COLORS["FISTA"], "s"),
                                          ("corr_0.99", r"Correlated ($\rho=0.99$)", COLORS["ADMM"], "D")):
        selected = [r for r in sensitivity if r["dataset"].startswith(prefix)]
        rho_values = sorted(set(float(r["rho"]) for r in selected))
        for ax, field, scale in zip(axes, ("time_seconds", "rounds"), (1000, 1)):
            means, errors = [], []
            for rho in rho_values:
                values = np.array([float(r[field])*scale for r in selected if float(r["rho"])==rho])
                means.append(float(values.mean())); errors.append(float(values.std(ddof=1)) if len(values)>1 else 0.)
            ax.errorbar(rho_values, means, yerr=errors, marker=marker, color=color,
                        capsize=3, label=label)
    for ax, ylabel in zip(axes, ("Solver time (ms)", "ADMM rounds")):
        ax.set(xscale="log", yscale="log", xlabel=r"ADMM penalty $\beta$", ylabel=ylabel,
               xticks=[.1, 1, 10], xticklabels=["0.1", "1", "10"])
        ax.xaxis.set_minor_locator(NullLocator()); grid(ax)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center", ncol=3, frameon=False, fontsize=14)
    save(fig, "admm_beta", "ADMM beta sensitivity, distinct from model lambda and feature-correlation rho. Saved CSVs call beta 'rho'. Each value uses three timing repetitions; correlated points summarize three instance medians with sample SD. Main comparisons fix beta=1 before timing; this panel does not retrospectively tune the main benchmark.")

    synthetic_coef = np.array([npz_data(main_dir / f"coefficients_synthetic_seed{i}_CD.npz")["raw_w"] for i in range(3)])
    diabetes_coef = npz_data(main_dir / "coefficients_diabetes_CD.npz")["standardized_w"]
    fig, axes = figure(two=True)
    x = np.arange(10)
    axes[0].bar(x-.18, truth[:10], width=.36, color="#9ca3af", label="Generating")
    axes[0].bar(x+.18, synthetic_coef.mean(0)[:10], width=.36,
                yerr=synthetic_coef.std(0, ddof=1)[:10], capsize=3,
                color=COLORS["CD"], label="CD mean ± SD")
    axes[0].set(xticks=x, xlabel="Feature index", ylabel="Coefficient: original units", title="Synthetic: selection and shrinkage")
    axes[0].legend(frameon=False, fontsize=12, ncol=2, loc="lower left")
    axes[1].bar(np.arange(len(diabetes_coef)), diabetes_coef, color=COLORS["CD"], width=.65)
    axes[1].set(xticks=range(len(diabetes_coef)),
                xticklabels=manifest["datasets"]["diabetes"]["feature_columns"],
                ylabel="Standardized coefficient", title="Diabetes: fixed split")
    axes[1].tick_params(axis="x", labelrotation=45)
    for ax in axes: ax.axhline(0, color="#777777", lw=.8); ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "coefficient_analysis", "CD coefficients at lambda/lambda_max=0.1. Synthetic: first ten of fifty coefficients, generating values versus mean ± sample SD across three instances in original units. Diabetes: standardized coefficients, with no known true support. The CD fit represents the converged model shared numerically by all four solvers.")

    for prefix, name, color in (("synthetic", "regularization", COLORS["ISTA"]),
                                 ("diabetes", "regularization_diabetes", COLORS["FISTA"])):
        fig, axes = figure(two=True)
        ratios = sorted(set(float(r["lambda_ratio"]) for r in penalties))
        for ax, field, ylabel in zip(axes, ("test_mse", "nonzero"), ("Test MSE", "Nonzero coefficients")):
            means, errors = [], []
            for ratio in ratios:
                values = np.array([float(r[field]) for r in penalties
                                   if r["dataset"].startswith(prefix) and float(r["lambda_ratio"])==ratio])
                means.append(float(values.mean())); errors.append(float(values.std(ddof=1)) if len(values)>1 else 0.)
            ax.errorbar(ratios, means, yerr=errors, fmt="o-", color=color, capsize=4)
            ax.set(xscale="log", xlabel=r"$\lambda/\lambda_{\max}$", ylabel=ylabel,
                   xticks=[.01, .1, 1.], xticklabels=["0.01", "0.1", "1"])
            ax.xaxis.set_minor_locator(NullLocator()); grid(ax)
        save(fig, name, f"CD model-penalty study for {prefix} data at four prespecified ratios. Synthetic values show means and sample SD across three instances; Diabetes uses one fixed split. Test scores describe settings and are not used for tuning lambda.")

    fig, axes = plt.subplots(2, 2, figsize=(12, 6.25), layout="constrained")
    for ax, name, title in zip(axes.flat, ("synthetic_seed0", "synthetic_seed1", "synthetic_seed2", "diabetes"),
                               ("Synthetic seed 0", "Synthetic seed 1", "Synthetic seed 2", "Diabetes: fixed split")):
        for x, method in enumerate(METHODS):
            vals = np.array([float(r["time_seconds"])*1000 for r in repeats
                             if r["dataset"]==name and r["method"]==method])
            ax.scatter(x+np.linspace(-.09,.09,len(vals)), vals, color=COLORS[method], s=40, zorder=3)
            ax.plot([x-.24,x+.24], [np.median(vals)]*2, color="#28323a", lw=2.1)
        ax.set(xticks=range(4), xticklabels=METHODS, ylabel="Solver time (ms)", title=title)
        ax.grid(True, axis="y"); ax.set_axisbelow(True)
    save(fig, "timing_repetitions", "Backup chart retaining all five main timing measurements per instance and solver. Black bars are medians; horizontal jitter only distinguishes repeated measurements. Timing repetitions are not independent datasets.")

    diagnostics = trace(extended / "admm_diagnostics_corr_0.99_seed10.csv")
    h = trace(extended / "trace_corr_0.99_seed10_ADMM.csv")
    fig, axes = figure(two=True)
    keep = diagnostics["round"] > 0
    axes[0].semilogy(diagnostics["round"][keep], np.maximum(diagnostics["primal_l2"][keep],1e-15),
                     color=COLORS["ISTA"], label=r"Primal $\|x-z\|_2$")
    axes[0].semilogy(diagnostics["round"][keep], np.maximum(diagnostics["dual_l2"][keep],1e-15),
                     color=COLORS["FISTA"], label=r"Dual $\beta\|z^k-z^{k-1}\|_2$")
    axes[0].set(xlabel="ADMM rounds", ylabel="Raw split-residual norm", title=r"Split diagnostics: raw $\ell_2$ norms")
    axes[0].legend(frameon=False, fontsize=12)
    axes[1].semilogy(h["round"], np.maximum(h["residual"],1e-15), color=COLORS["ADMM"])
    axes[1].axhline(1e-6, ls="--", color="#666666", lw=1.1, label=r"$10^{-6}$ tolerance")
    axes[1].set(xlabel="ADMM rounds", ylabel="Normalized stationarity $R(z)$", title="Common stopping check")
    axes[1].legend(frameon=False, fontsize=12)
    for ax in axes: grid(ax)
    save(fig, "admm_diagnostics", "Correlation 0.99, seed 10, beta=1. Left: unnormalized Euclidean primal and dual ADMM split residuals, with the zero initialization omitted on the logarithmic axis. Right: separately normalized original-objective stationarity R(z), the common stopping criterion. The raw split norms and R have different definitions and should not be compared numerically.")

    # Formula cutouts are typography assets, not newly computed numerical results.
    formulas = {
        "eq_objective": r"$\min_{w\in\mathbb{R}^{d}}\ F(w)=\frac{1}{2n}\|Xw-y\|_2^2+\lambda\|w\|_1$",
        "eq_kkt": r"$0\in\nabla g(w^\star)+\lambda\,\partial\|w^\star\|_1$",
        "eq_soft": r"$\mathcal{S}_{\tau}(v)=\mathrm{sign}(v)\max\{|v|-\tau,0\}$",
        "eq_ista": r"$w^{k+1}=\mathcal{S}_{\lambda/L}\!\left(w^k-\frac{\nabla g(w^k)}{L}\right)$",
        "eq_fista": (
            r"$w^k=\mathcal{S}_{\lambda/L}\!\left(z^k-\frac{\nabla g(z^k)}{L}\right)$"+"\n"+
            r"$t_{k+1}=\frac{1+\sqrt{1+4t_k^2}}{2}$"+"\n"+
            r"$z^{k+1}=w^k+\frac{t_k-1}{t_{k+1}}(w^k-w^{k-1})$"),
        "eq_cd": r"$r^{(j)}=y-\sum_{\ell\ne j}x_\ell w_\ell,\qquad w_j\leftarrow\frac{\mathcal{S}_{\lambda}(x_j^\top r^{(j)}/n)}{\|x_j\|_2^2/n}$",
        "eq_admm": (
            r"$\left(X^\top X/n+\beta I\right)x^{k+1}=X^\top y/n+\beta(z^k-u^k)$"+"\n"+
            r"$z^{k+1}=\mathcal{S}_{\lambda/\beta}(x^{k+1}+u^k)$"+"\n"+
            r"$u^{k+1}=u^k+x^{k+1}-z^{k+1}$"),
        "eq_residual": (
            r"$G_L(w)=L\!\left[w-\mathcal{S}_{\lambda/L}\!\left(w-\frac{\nabla g(w)}{L}\right)\right]$"+"\n"+
            r"$R(w)=\frac{\|G_L(w)\|_\infty}{\max\{1,\|X^\top y/n\|_\infty\}}\ \leq\ 10^{-6}$"),
        "eq_lmax": r"$\lambda_{\max}=\frac{\|X^\top y\|_\infty}{n},\qquad \lambda=0.1\lambda_{\max}$",
    }
    formula_records = []
    with plt.rc_context({"mathtext.fontset":"dejavuserif","font.family":"DejaVu Serif"}):
        for name, text in formulas.items():
            fig = plt.figure(figsize=(12, 2.5 if "\n" in text else 1.2))
            fig.patch.set_alpha(0)
            fig.text(.5,.5,text,ha="center",va="center",fontsize=28,
                     color="#17232d",linespacing=1.65)
            path=target/f"{name}.png"
            fig.savefig(path,dpi=180,bbox_inches="tight",pad_inches=.08,transparent=True)
            plt.close(fig)
            formula_records.append({"name":name,"file":path.name,"bytes":path.stat().st_size,
                                    "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                                    "transparent_background":True,"dpi":180})

    def rel(path):
        try: return path.relative_to(ROOT).as_posix()
        except ValueError: return str(path)
    provenance = {"generator":"scripts/plot_presentation_assets.py", "results":rel(source),
                  "generator_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "fits_models":False, "methods":list(METHODS), "colors":COLORS,
                  "numpy_version":np.__version__, "matplotlib_version":matplotlib.__version__,
                  "native_font_sizes_pt":{"axes_labels":16,"tick_labels":14,"legends":13},
                  "png_dpi":220,
                  "inputs":[{"path":rel(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(used)],
                  "figures":records,"formulas":formula_records}
    (target/"figure_manifest.json").write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    readme = ("PRESENTATION FOUR-SOLVER ASSETS — COMP6704 Group 9\n\n"
              "Regenerate: python scripts/plot_presentation_assets.py\n"
              "All numerical experiments are read from frozen CSV/JSON/NPZ files; no model is rerun.\n"
              "Large-label figures use 16 pt axis text, 14 pt ticks and 12–14 pt legends.\n"
              "Two-panel figures are approximately 12 x 3.7 in; single figures approximately 6.4 x 3.6 in.\n"
              "White backgrounds; muted blue/orange/green/purple; PNG at 220 dpi plus vector SVG/PDF.\n"
              "R(z) measures stationarity for the original objective. ADMM split residuals are labeled as raw Euclidean norms.\n"
              "ADMM algorithmic beta is recorded as rho in CSV; it differs from feature correlation rho and model lambda.\n"
              "Solver time includes method-specific setup and monitoring; shared spectral setup is excluded.\n"
              "Use caption and provenance records when writing notes and citing statistics.\n"
              "Nine transparent PNG equation assets use DejaVu Serif math text at 28 pt and 180 dpi.\n\n"
              + "\n".join(f"{r['name']}: {r['caption']}" for r in records)+"\n")
    (target/"README.txt").write_text(readme,encoding="utf-8")
    if not args.no_mirror:
        mirror.mkdir(parents=True,exist_ok=True)
        for record in records:
            for f in record["files"]: shutil.copy2(target/f["name"],mirror/f["name"])
        for item in formula_records: shutil.copy2(target/item["file"],mirror/item["file"])
        for name in ("figure_manifest.json","README.txt"): shutil.copy2(target/name,mirror/name)
    print(f"Rendered {len(records)} presentation figure groups and {len(formula_records)} formula cutouts to {target}")
    print(f"Mirror: {mirror}")


if __name__=="__main__":
    main()
