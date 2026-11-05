# Public Disclosure & Reproducibility Scope

## 1. Verifiable Empirical Artifacts Included in This Repository
This repository provides complete, standalone empirical provenance for the **October 31, 2026 Extended 4-Pillar IBM Heron Hardware Validation Campaign** (`17` sequential IBM Quantum `SamplerV2` batch jobs, `1,023` compiled physical circuits, `1,047,552` physical shots, `326.00 s` verified IBM `qpu_charge_time_seconds` across `ibm_marrakesh`, `ibm_fez`, and `ibm_kingston`):
- **Verifiable Hardware Identifiers:** All `17` October 31 IBM Quantum Job IDs (`dbittfohoj4c73b6u790` through `dbivh4hffo6c73b8j7tg`) plus the `4` October 27 reference Job IDs (`dbghgkdrd2mc73cuo0jg`, `dbghgroiudkc73e4gvig`, `dbghh7ljm0ks73egl000`, `dbgjtecdgr2s73crlre0`).
- **Pre-Execution Cryptographic Commitments:** Pre-submission SHA-256 hashes of every compiled physical circuit and pre-committed cross-QPU dispatch decision locked prior to hardware execution.
- **Unrouted Logical Benchmark Circuits & Reference Distributions:** Portable OpenQASM 2.0 circuits (`*.qasm`), exact statevector reference probability distributions (`*.npz`), deterministic Clifford mirror target bitstrings, and MaxCut graph edge lists in `data/logical_circuits/`.
- **Raw Hardware Measurement Counts:** Canonical bitstring histograms (`1,024` shots per circuit execution) in `data/jobs/*.json` and `data/pillar1_repeat_and_dispatch/results_p1_raw.json`.
- **Standalone Offline Verification:** `scripts/verify_campaign.py` recomputes all fidelity, TVD, mirror polarization, and QAOA cut metrics directly from the raw measurement counts using only standard open-source Python (`numpy`).

## 2. Intellectual Property Boundary
To protect Prometheus Dynamics proprietary compiler and execution-selection intellectual property while preserving 100% empirical verifiability of the hardware outcomes:
- Internal compiler routing heuristics, multi-objective scoring weights, structural Pareto selection rules, internal policy ablations, candidate-origin metadata, and proprietary synthesis pass implementations are withheld from this public repository.
- All baseline comparisons (`Qiskit SABRE O3` default and matched-budget multi-seed search, `Quantinuum TKET` default and matched-budget multi-seed search, and `ST` gate-count/depth baseline selection) and all `Prometheus` compiled circuit structural metrics (`Native 2Q Gates`, `Compiled Circuit Depth`, `SHA-256` circuit commitments, and classical wall-clock compilation times) are reported in full.
