# Data Dictionary & Schema Reference

## 1. Master CSV: `data/ALL_1023_CIRCUITS_RESULTS.csv` (`1,023` Rows)
Each row corresponds to one physical circuit execution (`1,024` shots) on an IBM Heron r2 processor (`ibm_marrakesh`, `ibm_fez`, or `ibm_kingston`):
- `pillar`: Campaign pillar identifier (`Pillar1_Repeat_and_Dispatch`, `Pillar2_Clifford_Mirror`, `Pillar2_SPAM_Control`, `Pillar3_QAOA_Trajectory`, `Pillar4_Fresh_Equal_Budget`).
- `job_id`: Verifiable IBM Quantum Runtime Job ID (`20`-character alphanumeric identifier).
- `backend`: Target IBM Heron processor (`ibm_marrakesh`, `ibm_fez`, `ibm_kingston`).
- `backend_slot`: Assigned slot code (`A` = `ibm_marrakesh`, `B` = `ibm_fez`, `C` = `ibm_kingston`).
- `block`: Execution block index (`1` or `2`).
- `workload_id`: Unique benchmark instance, mirror circuit, SPAM control, or QAOA trajectory stage identifier.
- `family_or_stage`: Algorithm family (`dense`, `bipartite`, `star`, `ising`, `qaoa`, `qft_phase`) or mirror/QAOA stage (`mirror_d1`, `mirror_d2`, `spam_state_prep_readout`, `qaoa_initial`, `qaoa_intermediate`, `qaoa_final`).
- `width`: Number of active logical qubits (`6` to `101`).
- `pipeline`: Compiler pipeline identifier (`sabre_o3`, `tket`, `prometheus_fresh_candidate`, `prometheus_stale_candidate`, `prometheus_candidate`, `sabre_o3_default`, `sabre_o3_matched_budget`, `tket_matched_budget`).
- `shots`: Physical measurement shots executed (`1,024` per circuit).
- `native_2q`: Compiled native two-qubit gate count (`CZ` / `ECR` on Heron ISA).
- `depth`: Compiled native circuit depth on the target processor.
- `circuit_sha256`: Pre-execution SHA-256 cryptographic digest of the compiled physical circuit.
- `squared_hellinger_fidelity_fh`: Squared Hellinger fidelity F_H = (Σ_x √(P_ideal(x) · P_meas(x)))² (or exact target survival for mirror/control circuits, or approximation ratio for Pillar 3 QAOA).
- `bhattacharyya_overlap_fb`: Classical Bhattacharyya distribution overlap F_B = √(F_H) (or P(C ≥ C_{0.9}) for Pillar 3 QAOA).
- `tvd`: Total Variation Distance 0.5 · Σ_x |P_ideal(x) - P_meas(x)| (or |Ratio_meas - Ratio_ideal| for Pillar 3 QAOA).
- `primary_metric_name`: Primary task observable name for the cohort.
- `primary_metric_value`: Measured value of the primary task observable.

## 2. Raw Batch Job Checkpoints: `data/jobs/*.json` (`17` Files)
- `batch_label`: Descriptive batch name.
- `backend`: Target IBM Heron QPU.
- `job_id`: Official IBM Quantum Job ID.
- `submission_timestamp` / `completion_timestamp`: UTC ISO-8601 timestamps.
- `quantum_seconds`: Official IBM `metrics()["usage"]["qpu_charge_time_seconds"]`.
- `circuits_execution_time_seconds`: Official IBM `metrics()["qiskit_quantum_time"]` active QPU execution time.
- `isa_duration_estimate`: Pre-submission additive duration estimate (`total_circuits`, `total_shots`, `repetition_delay_seconds`, `isa_gate_readout_seconds`, `job_init_allowance_seconds`, `total_estimated_seconds`).
- `pub_counts`: Array of raw canonical bitstring count dictionaries (`1,024` shots per PUB) in exact batch execution order.
