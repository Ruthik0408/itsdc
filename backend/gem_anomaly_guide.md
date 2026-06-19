### dak

This source plan for `dak` is designed to detect anomalies in the GEM_BILLS payment flow at the root level. It focuses on identity, date, amount, and structural integrity of DAKs, ensuring they belong to valid GEM sections, have correct identifiers, and follow expected chronology. Features are prioritized for flow integrity, duplicate detection, and outlier behavior. All features are deterministic, numeric, and explainable to auditors. This plan serves as the foundation for downstream GEM bill and product-level anomaly detection.

### gem_bill

This source plan extracts deterministic, audit-ready forensic features from `gem_bill` for Isolation Forest. It focuses on GEM payment flow integrity, duplicate detection, amount consistency, date logic, and approval contradictions. All features are derived from visible columns, obey the contract, and align with GEM_BILLS rules. Use `fk_section IN (113, 127, 128, 129, 219, 348)` for filtering.

### cheque_slip

Cheque_slip is a critical downstream stage in the GEM payment flow. This source plan focuses on detecting flow breaks, approval anomalies, timing issues, and payment pattern inconsistencies. Features are designed to be deterministic, numeric, and auditable, with strong grounding in GEM_BILLS workflow and gem_feature_rules. All features use only visible columns and obey the feature_contract.

### punching_medium

This source plan focuses on punching_medium as a critical downstream stage in the GEM payment flow. It ensures PMs are properly linked to dak, follow correct chronology, have valid approval trails, and align with downstream stages like schedule3 and ecs. Features detect flow breaks, approval contradictions, amount mismatches, and duplicate or batched processing patterns. All features are deterministic, numeric, and explainable to auditors.

### schedule3

schedule3 is the final stage in the GEM payment flow. This source plan focuses on detecting approval anomalies, amount mismatches, date contradictions, and outlier behavior. All features are deterministic, numeric, and grounded in visible columns. Use `fk_dak` and `section_code` for grouping. Avoid raw identifiers in Isolation Forest; use only numeric, explainable features.

### ecs

ECS is the final stage in the GEM payment flow. This source plan focuses on validating payment completion, detecting duplicate UTRs/references, amount mismatches with upstream stages, reverse chronology, and patterns of round amounts or off-hour processing. All features are deterministic, numeric, and audit-explainable.
