"""
Command-Line Interface for LANDSYNC Synthetic Datasets Generator.
Provides reproducible commands: generate, validate, report, export, all.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from landsync_datasets.config.loader import load_config
from landsync_datasets.generators.pipeline import run_pipeline
from landsync_datasets.reports.reporter import run_quality_gates
from landsync_datasets.privacy.scanner import run_privacy_scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="landsync_datasets",
        description="LANDSYNC-India Synthetic Land Record & Cadastral Benchmark Generator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. generate
    gen_parser = subparsers.add_parser("generate", help="Generate synthetic dataset tables")
    gen_parser.add_argument("--config", type=str, default="configs/default.yaml", help="Path to config file")

    # 2. validate
    val_parser = subparsers.add_parser("validate", help="Run automated data quality gates")
    val_parser.add_argument("--path", type=str, default="datasets/landsync-india-synthetic", help="Path to dataset root")

    # 3. report
    rep_parser = subparsers.add_parser("report", help="Generate quality and privacy reports")
    rep_parser.add_argument("--path", type=str, default="datasets/landsync-india-synthetic", help="Path to dataset root")

    # 4. export
    exp_parser = subparsers.add_parser("export", help="Export dataset tables to CSV, Parquet, GeoJSON, and JSONL")
    exp_parser.add_argument("--path", type=str, default="datasets/landsync-india-synthetic", help="Path to dataset root")

    # 5. all
    all_parser = subparsers.add_parser("all", help="Run complete end-to-end generation and verification pipeline")
    all_parser.add_argument("--config", type=str, default="configs/default.yaml", help="Path to config file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in ("generate", "all"):
        print(f"[*] Loading configuration from: {args.config}")
        cfg = load_config(args.config)
        print(f"[*] Running synthetic dataset generator (version {cfg.version}, seed {cfg.seed})...")
        res = run_pipeline(cfg)

        print("\n" + "=" * 60)
        print("GENERATION PIPELINE COMPLETED")
        print("=" * 60)
        for tbl, count in res.counts.items():
            print(f" - {tbl:<28}: {count:>7,d}")
        print(f"Output directory: {res.output_dir.resolve()}")
        print(f"Privacy Scan Status: {res.privacy_report['status']}")
        print(f"Split Leakage Status: {res.leakage_report['status']}")
        print(f"Manifest Total Files: {res.manifest['total_files']}")
        print("=" * 60 + "\n")

        # Run quality gates
        print("[*] Running automated quality gates...")
        q_rep = run_quality_gates(res.output_dir)
        print(f"Quality Gates Status: {q_rep['status']} ({q_rep['passed_checks']}/{q_rep['total_checks']} passed)")

        if q_rep["status"] != "PASS" or res.privacy_report["status"] != "PASS" or res.leakage_report["status"] != "PASS":
            print("[!] Quality gates or safety checks failed!")
            return 1
        return 0

    elif args.command == "validate":
        p = Path(args.path)
        print(f"[*] Validating dataset at: {p.resolve()}")
        q_rep = run_quality_gates(p)
        print(json.dumps(q_rep, indent=2))
        return 0 if q_rep["status"] == "PASS" else 1

    elif args.command == "report":
        p = Path(args.path)
        print(f"[*] Generating report for dataset at: {p.resolve()}")
        q_rep = run_quality_gates(p)
        print("\n" + "=" * 60)
        print(f"DATASET QUALITY REPORT: {q_rep['status']}")
        print(f"Passed: {q_rep['passed_checks']} / {q_rep['total_checks']}")
        print("=" * 60)
        for chk in q_rep["checks"]:
            mark = "PASS" if chk["passed"] else "FAIL"
            print(f" [{mark}] {chk['category']:<12} {chk['check_name']:<35}: {chk['message']}")
        print("=" * 60 + "\n")
        return 0 if q_rep["status"] == "PASS" else 1

    elif args.command == "export":
        print(f"[*] Re-exporting manifests and artifacts at: {args.path}")
        cfg = load_config()
        run_pipeline(cfg)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
