"""
Evaluate the LSTM Autoencoder on the market dataset.

The autoencoder learns to reconstruct normal price sequences.
High reconstruction error = anomalous / unusual price pattern.

Outputs:
  - Reconstruction error statistics
  - Top anomalous records
  - Distribution plot of reconstruction errors
  - Accuracy proxy: % of records within threshold
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent


def load_model():
    """Load the LSTM autoencoder model."""
    model_path = BASE_DIR / "market_lstm_autoencoder.h5"
    if not model_path.exists():
        sys.exit(f"Model not found: {model_path}")

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(str(model_path), compile=False)
        return model
    except ImportError:
        try:
            from keras.models import load_model as keras_load
            model = keras_load(str(model_path), compile=False)
            return model
        except ImportError:
            sys.exit(
                "Neither tensorflow nor keras is installed.\n"
                "Install with: pip install tensorflow   or   pip install keras"
            )


def load_data() -> pd.DataFrame:
    """Load and clean market dataset."""
    csv_path = BASE_DIR / "clean_market_dataset.csv"
    if not csv_path.exists():
        sys.exit(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    df["ddate"] = pd.to_datetime(df["ddate"], errors="coerce")
    df = df.dropna(subset=["ddate", "model"])  # 'model' column is modal price

    # Ensure numeric
    for col in ["arrivals", "minimum", "maximum", "model"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["model"])
    df = df[df["model"] > 0].copy()

    return df


def prepare_sequences(
    df: pd.DataFrame,
    seq_len: int,
    feature_cols: list[str] | None = None,
) -> tuple[np.ndarray, pd.DataFrame]:
    """
    Create sliding-window sequences for the autoencoder.
    Groups by (district, amcname, commname), sorts by date,
    and builds sequences of length seq_len.
    """
    if feature_cols is None:
        feature_cols = ["model"]  # default: modal price only

    sequences = []
    meta_rows = []

    for (dist, amc, crop), grp in df.groupby(["district", "amcname", "commname"]):
        grp = grp.sort_values("ddate")
        vals = grp[feature_cols].values
        dates = grp["ddate"].values

        if len(vals) < seq_len:
            continue

        for i in range(len(vals) - seq_len + 1):
            seq = vals[i : i + seq_len]
            sequences.append(seq)
            meta_rows.append({
                "district": dist,
                "amcname": amc,
                "commname": crop,
                "start_date": str(dates[i])[:10],
                "end_date": str(dates[i + seq_len - 1])[:10],
            })

    X = np.array(sequences, dtype=np.float32)
    meta = pd.DataFrame(meta_rows)
    return X, meta


def normalize_sequences(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Min-max normalize each sequence to [0,1] for autoencoder input."""
    mins = X.min(axis=1, keepdims=True)
    maxs = X.max(axis=1, keepdims=True)
    ranges = maxs - mins
    ranges[ranges == 0] = 1  # avoid division by zero
    X_norm = (X - mins) / ranges
    return X_norm, mins, ranges


def main() -> None:
    print("=" * 60)
    print("LSTM Autoencoder Evaluation — Market Anomaly Detection")
    print("=" * 60)

    # Load
    model = load_model()
    df = load_data()
    print(f"\nDataset: {len(df):,} records")
    print(f"Date range: {df['ddate'].min().date()} to {df['ddate'].max().date()}")
    print(f"Districts: {df['district'].nunique()}")
    print(f"Crops: {df['commname'].nunique()}")

    # Inspect model input shape
    input_shape = model.input_shape
    print(f"\nModel input shape: {input_shape}")

    # Determine sequence length from model architecture
    if isinstance(input_shape, list):
        # multi-input model
        seq_len = input_shape[0][1] if input_shape[0][1] is not None else 30
        n_features = input_shape[0][2] if len(input_shape[0]) > 2 else 1
    else:
        seq_len = input_shape[1] if input_shape[1] is not None else 30
        n_features = input_shape[2] if len(input_shape) > 2 and input_shape[2] is not None else 1

    print(f"Sequence length: {seq_len}")
    print(f"Features per timestep: {n_features}")

    # Build feature columns
    if n_features == 1:
        feature_cols = ["model"]
    elif n_features == 4:
        feature_cols = ["arrivals", "minimum", "maximum", "model"]
    else:
        # fallback: try using modal price only
        feature_cols = ["model"]
        print(f"[WARN] unexpected n_features={n_features}, using modal price only")

    # Create sequences
    print(f"\nBuilding sequences (len={seq_len})...")
    X, meta = prepare_sequences(df, seq_len=seq_len, feature_cols=feature_cols)
    if len(X) == 0:
        sys.exit("No valid sequences could be created. Check data coverage.")
    print(f"Sequences created: {len(X):,}")

    # Reshape if needed
    if len(X.shape) == 2:
        X = X.reshape(X.shape[0], X.shape[1], 1)

    # Normalize
    orig_shape = X.shape
    X_flat = X.reshape(X.shape[0], -1)
    X_norm, mins, ranges = normalize_sequences(X_flat)
    X_norm = X_norm.reshape(orig_shape)

    # Predict (reconstruct)
    print("Running autoencoder reconstruction...")
    batch_size = min(512, len(X_norm))
    X_reconstructed = model.predict(X_norm, batch_size=batch_size, verbose=0)

    # If output shape differs from input, attempt reshape
    if X_reconstructed.shape != X_norm.shape:
        try:
            X_reconstructed = X_reconstructed.reshape(X_norm.shape)
        except ValueError:
            print(f"[WARN] Output shape {X_reconstructed.shape} != input shape {X_norm.shape}")
            print("Attempting to compare flattened...")
            X_norm_flat = X_norm.reshape(X_norm.shape[0], -1)
            X_recon_flat = X_reconstructed.reshape(X_reconstructed.shape[0], -1)
            mse_per_seq = np.mean((X_norm_flat - X_recon_flat) ** 2, axis=1)
            meta["reconstruction_error"] = mse_per_seq
            _report(meta)
            return

    # Compute reconstruction error per sequence
    mse_per_seq = np.mean((X_norm - X_reconstructed) ** 2, axis=(1, 2))
    meta["reconstruction_error"] = mse_per_seq

    _report(meta)


def _report(meta: pd.DataFrame) -> None:
    """Print evaluation report."""
    errs = meta["reconstruction_error"]

    print("\n" + "=" * 60)
    print("RECONSTRUCTION ERROR STATISTICS")
    print("=" * 60)
    print(f"  Mean:   {errs.mean():.6f}")
    print(f"  Median: {errs.median():.6f}")
    print(f"  Std:    {errs.std():.6f}")
    print(f"  Min:    {errs.min():.6f}")
    print(f"  Max:    {errs.max():.6f}")
    print(f"  P95:    {errs.quantile(0.95):.6f}")
    print(f"  P99:    {errs.quantile(0.99):.6f}")

    # Threshold-based classification
    threshold_p95 = errs.quantile(0.95)
    threshold_p99 = errs.quantile(0.99)

    normal_95 = (errs <= threshold_p95).sum()
    normal_99 = (errs <= threshold_p99).sum()

    print(f"\n  Normal (≤P95 threshold {threshold_p95:.6f}): {normal_95:,} / {len(errs):,} ({100*normal_95/len(errs):.1f}%)")
    print(f"  Normal (≤P99 threshold {threshold_p99:.6f}): {normal_99:,} / {len(errs):,} ({100*normal_99/len(errs):.1f}%)")

    # Top anomalies
    print("\n" + "-" * 60)
    print("TOP 20 MOST ANOMALOUS SEQUENCES")
    print("-" * 60)
    top_anom = meta.nlargest(20, "reconstruction_error")
    print(top_anom.to_string(index=False))

    # Per-crop anomaly rate
    print("\n" + "-" * 60)
    print("ANOMALY RATE BY CROP (top 15 by rate, P95 threshold)")
    print("-" * 60)
    meta["is_anomaly"] = meta["reconstruction_error"] > threshold_p95
    crop_anom = (
        meta.groupby("commname")
        .agg(total=("is_anomaly", "count"), anomalies=("is_anomaly", "sum"))
        .assign(rate=lambda x: x["anomalies"] / x["total"])
        .sort_values("rate", ascending=False)
        .head(15)
    )
    print(crop_anom.to_string())

    # Save results
    out_path = BASE_DIR / "autoencoder_evaluation_results.csv"
    meta.to_csv(out_path, index=False)
    print(f"\n✅ Full results saved to: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
