"""Run the complete benchmark pipeline from the CLI."""
import sys
import os

# Run from the project root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
import json
from pathlib import Path

from backend.app.config import settings
from backend.app.models import RunConfig
from backend.app.pipeline import start_pipeline


def main():
    parser = argparse.ArgumentParser(description="NoiseProof – Run benchmark pipeline")
    parser.add_argument("--calls", type=int, default=2, help="Number of synthetic calls (default: 2)")
    parser.add_argument("--noise", nargs="+", default=["street","crowd","wind","white","market"])
    parser.add_argument("--snr", nargs="+", default=["clean","20","10","5","0"])
    parser.add_argument("--dry-run", action="store_true", help="Use mock responses (no credits)")
    parser.add_argument("--output", type=str, default=None, help="Save results JSON to file")
    args = parser.parse_args()

    if args.dry_run:
        settings.dry_run = True
        print("🟢 DRY RUN mode – no API credits will be consumed")

    print(f"📊 Starting pipeline: {args.calls} calls × {len(args.snr)} SNR levels × {len(args.noise)} noise types")
    print(f"   = {args.calls * len(args.snr) * len(args.noise)} variants\n")

    config = RunConfig(
        num_calls=args.calls,
        snr_levels=args.snr,
        noise_types=args.noise,
        dry_run=args.dry_run,
    )

    def on_progress(p):
        bar = "█" * int(p.pct / 5) + "░" * (20 - int(p.pct / 5))
        print(f"\r[{bar}] {p.pct:.0f}%  {p.current_step[:50]:<50}", end="", flush=True)

    run_id = start_pipeline(config, progress_cb=on_progress)
    print(f"\n\n✓ Run {run_id} complete!")

    # Print summary
    results_dir = settings.results_dir
    agg_file = results_dir / f"run_{run_id}_aggregated.json"
    if agg_file.exists():
        with open(agg_file) as f:
            agg = json.load(f)
        print("\nAggregated Results:")
        print(f"{'SNR':<8} {'WER':>8} {'Recall':>10} {'Score':>8} {'Lat(ms)':>10}")
        print("-" * 48)
        for row in agg:
            snr = "Clean" if row["snr"] == "clean" else f"{row['snr']} dB"
            print(f"{snr:<8} {row['wer_mean']*100:>7.1f}% {row['key_fact_recall_mean']*100:>9.1f}% {row['summary_score_mean']:>8.2f} {row['latency_ms_mean']:>9.0f}")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(agg, f, indent=2)
            print(f"\n→ Results saved to {args.output}")


if __name__ == "__main__":
    main()
