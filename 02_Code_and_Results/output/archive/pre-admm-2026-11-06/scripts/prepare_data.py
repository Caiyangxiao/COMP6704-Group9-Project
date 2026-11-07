"""Prepare inputs only; this script does not fit models or run optimizers."""

from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SOURCE_ROOT = (
    "https://raw.githubusercontent.com/scikit-learn/scikit-learn/"
    "1.9.1/sklearn/datasets/data/"
)


def get_source(filename):
    url = SOURCE_ROOT + filename
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read()
    (DATA / filename).write_bytes(payload)
    array = np.loadtxt(io.BytesIO(gzip.decompress(payload)))
    record = {
        "url": url,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }
    return array, record


def save_dataset(name, X, y, feature_names, seed):
    if X.ndim != 2 or y.shape != (X.shape[0],):
        raise ValueError(f"Inconsistent shape for {name}")
    if not np.isfinite(X).all() or not np.isfinite(y).all():
        raise ValueError(f"Non-finite values in {name}")
    # Split membership is fixed before any preprocessing or optimization.
    rng = np.random.default_rng(seed)
    n_test = int(np.ceil(0.2 * len(y)))
    test_ids = set(rng.permutation(len(y))[:n_test].tolist())
    path = DATA / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["row_id", "split", *feature_names, "target"])
        for i, (row, target) in enumerate(zip(X, y)):
            writer.writerow(
                [i, "test" if i in test_ids else "train", *row, target]
            )
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "samples": len(y),
        "features": X.shape[1],
        "train_samples": len(y) - n_test,
        "test_samples": n_test,
        "split_seed": seed,
        "feature_columns": feature_names,
    }


def main():
    DATA.mkdir(exist_ok=True)
    X, features_source = get_source("diabetes_data_raw.csv.gz")
    y, target_source = get_source("diabetes_target.csv.gz")
    if X.shape != (442, 10) or y.shape != (442,):
        raise ValueError("Downloaded Diabetes data differs from expected shape")
    names = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
    manifest = {
        "purpose": "Prepared input data; no optimizer or model has been run.",
        "prepared_date": datetime.now(ZoneInfo("Asia/Hong_Kong")).date().isoformat(),
        "numpy_version": np.__version__,
        "diabetes_source_version": "scikit-learn 1.9.1",
        "sources": {"features": features_source, "target": target_source},
        "datasets": {"diabetes": save_dataset("diabetes", X, y, names, 0)},
        "synthetic_generation": {
            "samples": 300,
            "features": 50,
            "distribution": "Independent standard-normal features",
            "noise_distribution": "Normal with mean 0 and standard deviation 0.5",
            "true_coefficients": [2.0, -1.5, 1.0, -2.0, 1.5] + [0.0] * 45,
            "intercept": 0.0,
            "seeds": [0, 1, 2],
        },
    }
    w = np.array(manifest["synthetic_generation"]["true_coefficients"])
    for seed in (0, 1, 2):
        rng = np.random.default_rng(seed)
        X_syn = rng.normal(size=(300, 50))
        y_syn = X_syn @ w + rng.normal(scale=0.5, size=300)
        name = f"synthetic_seed{seed}"
        record = save_dataset(name, X_syn, y_syn, [f"x{i}" for i in range(50)], seed)
        record["generation_seed"] = seed
        manifest["datasets"][name] = record
    (DATA / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for name, record in manifest["datasets"].items():
        print(f"{name}: {record['samples']} rows, {record['features']} features; "
              f"train={record['train_samples']}, test={record['test_samples']}")
    print("Input preparation complete. No algorithms were trained.")


if __name__ == "__main__":
    main()
