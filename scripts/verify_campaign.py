"""
Standalone offline verification script for:
  IBM-Heron-Extended-Validation-1023-Circuits
Verifies:
  1. All 17 raw IBM Quantum batch job checkpoints in data/jobs/*.json (1,023 circuits,
     1,047,552 physical shots, 326.00 s total IBM qpu_charge_time_seconds).
  2. Exact recomputation of Pillar 1 (F_H, F_B, TVD from raw bitstring counts and .npz references).
  3. Scored summary ledger and aggregate assertion verification for Pillar 2 (252 Clifford mirrors + 27 SPAM controls),
     Pillar 3 (216 QAOA trajectory circuits), Pillar 4 (96 equal-budget generalization circuits), and ALL_1023_CIRCUITS_RESULTS.csv.
  6. Cryptographic SHA-256 integrity of all files listed in REPOSITORY_SHA256SUMS.txt.
"""

from __future__ import annotations
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256_manifest() -> None:
    manifest_path = REPO_ROOT / "REPOSITORY_SHA256SUMS.txt"
    if not manifest_path.exists():
        raise FileNotFoundError("Missing REPOSITORY_SHA256SUMS.txt")
    lines = [ln.strip() for ln in manifest_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for ln in lines:
        expected_hash, rel_path = ln.split("  ", 1)
        target = REPO_ROOT / rel_path
        actual_hash = sha256_file(target)
        if actual_hash != expected_hash:
            raise AssertionError(f"SHA-256 mismatch on {rel_path}: expected {expected_hash}, got {actual_hash}")
    print(f"[PASS] Verified SHA-256 cryptographic hashes for all {len(lines)} repository files.")


def verify_raw_jobs() -> None:
    job_files = sorted((DATA_DIR / "jobs").glob("*.json"))
    assert len(job_files) == 17, f"Expected 17 job files, found {len(job_files)}"
    total_circs = 0
    total_shots = 0
    total_charge = 0.0
    total_exec = 0.0
    for jf in job_files:
        jd = json.loads(jf.read_text(encoding="utf-8"))
        pubs = jd["pub_counts"]
        total_circs += len(pubs)
        for pc in pubs:
            s = sum(pc.values())
            assert s == 1024, f"Expected 1024 shots per PUB in {jf.name}, got {s}"
            total_shots += s
        total_charge += float(jd["quantum_seconds"])
        total_exec += float(jd.get("circuits_execution_time_seconds", 0.0))
    assert total_circs == 1023, f"Expected 1023 total circuits, got {total_circs}"
    assert total_shots == 1047552, f"Expected 1047552 total shots, got {total_shots}"
    assert abs(total_charge - 326.0) < 1e-6, f"Expected 326.0s total QPU charge time, got {total_charge}"
    print(f"[PASS] Verified 17 IBM Quantum batch jobs: {total_circs} circuits, {total_shots:,} physical shots, {total_charge:.2f}s QPU charge time ({total_exec:.2f}s active execution).")


def verify_pillar1_from_raw_counts() -> None:
    raw_list = json.loads((DATA_DIR / "pillar1_repeat_and_dispatch" / "results_p1_raw.json").read_text(encoding="utf-8"))
    scored_list = json.loads((DATA_DIR / "pillar1_repeat_and_dispatch" / "results_p1_scored.json").read_text(encoding="utf-8"))
    assert len(raw_list) == 432 and len(scored_list) == 432
    ref_dir = DATA_DIR / "logical_circuits" / "pillar1_18_workloads"
    ref_cache = {}
    for item in json.loads((ref_dir / "manifest.json").read_text(encoding="utf-8"))["instances"]:
        ref_fname = item.get("reference_file") or item.get("reference_path")
        npz = np.load(ref_dir / Path(ref_fname).name, allow_pickle=True)
        arr = npz["ideal_probabilities"] if "ideal_probabilities" in npz else npz["ideal_probs"]
        ref_cache[item["instance_id"]] = np.asarray(arr, dtype=float)

    scored_map = {(r["instance_id"], r["backend"], r["block"], r["pipeline"]): r for r in scored_list}
    max_fh_err = 0.0
    max_tvd_err = 0.0
    for raw in raw_list:
        iid = raw["instance_id"]
        ideal_probs = ref_cache[iid]
        n = int(round(math.log2(len(ideal_probs))))
        shots = int(raw["shots"])
        meas_probs = np.zeros_like(ideal_probs)
        for bs, c in raw["counts"].items():
            meas_probs[int(bs, 2)] += c / shots
        fb = float(np.sum(np.sqrt(ideal_probs * meas_probs)))
        fh = fb * fb
        tvd = 0.5 * float(np.sum(np.abs(ideal_probs - meas_probs)))
        sc = scored_map[(iid, raw["backend"], raw["block"], raw["pipeline"])]
        max_fh_err = max(max_fh_err, abs(fh - float(sc["squared_hellinger_fidelity"])))
        max_tvd_err = max(max_tvd_err, abs(tvd - float(sc["tvd"])))

    assert max_fh_err < 1e-9 and max_tvd_err < 1e-9, f"Pillar 1 recomputation mismatch: {max_fh_err}, {max_tvd_err}"
    for pipe, expected_mean in [("sabre_o3", 0.6121), ("tket", 0.5259), ("prometheus_fresh_candidate", 0.6453)]:
        vals = [r["squared_hellinger_fidelity"] for r in scored_list if r["pipeline"] == pipe]
        mean_val = float(np.mean(vals))
        assert abs(mean_val - expected_mean) < 1e-3, f"Pillar 1 {pipe} mean F_H {mean_val:.4f} != {expected_mean}"
    print(f"[PASS] Verified Pillar 1 (432 circuits) from raw bitstring counts: max |dF_H| = {max_fh_err:.2e}, max |dTVD| = {max_tvd_err:.2e}.")


def verify_pillars_2_3_4_and_csv() -> None:
    p2 = json.loads((DATA_DIR / "pillar2_clifford_mirror_8q_101q" / "results_p2_mirror_scored.json").read_text(encoding="utf-8"))
    p2_ctrl = json.loads((DATA_DIR / "pillar2_clifford_mirror_8q_101q" / "results_p2_spam_controls_scored.json").read_text(encoding="utf-8"))
    p3 = json.loads((DATA_DIR / "pillar3_qaoa_trajectory" / "results_p3_qaoa_scored.json").read_text(encoding="utf-8"))
    p4 = json.loads((DATA_DIR / "pillar4_fresh_equal_budget_challenge" / "results_p4_fresh_challenge_scored.json").read_text(encoding="utf-8"))
    assert len(p2) == 252 and len(p2_ctrl) == 27 and len(p3) == 216 and len(p4) == 96

    # Check Pillar 2 101Q d=1 polarization
    pol_101_s = np.mean([r["mirror_metrics"]["zero_centered_polarization"] for r in p2 if r["width"] == 101 and r["depth_passes"] == 1 and r["pipeline"] == "sabre_o3"])
    pol_101_p = np.mean([r["mirror_metrics"]["zero_centered_polarization"] for r in p2 if r["width"] == 101 and r["depth_passes"] == 1 and r["pipeline"] == "prometheus_candidate"])
    assert abs(pol_101_s - 0.3801) < 1e-3 and abs(pol_101_p - 0.5379) < 1e-3

    # Check Pillar 3 Stage 3 Final COBYLA approximation ratio
    r3_s = np.mean([r["qaoa_metrics"]["approx_ratio"] for r in p3 if r["stage"] == "final_cobyla_solution" and r["pipeline"] == "sabre_o3"])
    r3_p = np.mean([r["qaoa_metrics"]["approx_ratio"] for r in p3 if r["stage"] == "final_cobyla_solution" and r["pipeline"] == "prometheus_candidate"])
    assert abs(r3_s - 0.6393) < 1e-3 and abs(r3_p - 0.6444) < 1e-3

    # Check Pillar 4 Equal-Budget F_H
    p4_s_bud = np.mean([r["metrics"]["squared_hellinger_fidelity"] for r in p4 if r["pipeline"] == "sabre_o3_matched_budget"])
    p4_t_bud = np.mean([r["metrics"]["squared_hellinger_fidelity"] for r in p4 if r["pipeline"] == "tket_matched_budget"])
    p4_prom = np.mean([r["metrics"]["squared_hellinger_fidelity"] for r in p4 if r["pipeline"] == "prometheus_candidate"])
    assert abs(p4_s_bud - 0.2849) < 1e-3 and abs(p4_t_bud - 0.2763) < 1e-3 and abs(p4_prom - 0.2953) < 1e-3

    # Check Master CSV
    with open(DATA_DIR / "ALL_1023_CIRCUITS_RESULTS.csv", "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1023, f"Expected 1023 rows in ALL_1023_CIRCUITS_RESULTS.csv, got {len(rows)}"
    print(f"[PASS] Verified Pillar 2 (252 mirrors + 27 SPAM controls), Pillar 3 (216 QAOA runs), Pillar 4 (96 equal-budget runs), and ALL_1023_CIRCUITS_RESULTS.csv (1,023 rows).")


if __name__ == "__main__":
    verify_raw_jobs()
    verify_pillar1_from_raw_counts()
    verify_pillars_2_3_4_and_csv()
    verify_sha256_manifest()
    print("\nALL VERIFICATION CHECKS PASSED (17 IBM Quantum Jobs, 1,023 Circuits, 1,047,552 Physical Shots).")
