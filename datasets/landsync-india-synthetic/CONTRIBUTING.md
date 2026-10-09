# Contributing to LANDSYNC-India Synthetic Benchmark

We welcome contributions from data engineers, geospatial analysts, legal researchers, and Document AI practitioners!

---

## 1. How to Add a New Jurisdiction Profile

Jurisdiction profiles live in `configs/jurisdiction_profiles.yaml`. To propose a new state profile (e.g. Maharashtra or Uttar Pradesh):
1. Create a new profile key (e.g. `MH_PILOT`).
2. Provide official state revenue terminology (`7/12 extract / Satbara`, `Ferfar`, `Dastavej`).
3. Define local survey identifier formats and primary area unit conventions (`hectare`, `are`, `sqm`).
4. Define a fictional study envelope with bounding coordinates.
5. Provide citations to primary state legislation in `rule_register.py`.

---

## 2. Proposing New Validation Scenarios

Scenario quotas are configured in `configs/scenario_quotas.yaml`.
When adding a scenario:
- Specify `count`, `difficulty` (`EASY`, `MEDIUM`, `HARD`, `ADVERSARIAL`), `category`, `expected_outcome` (`MATCH`, `PARTIAL_MATCH`, `MISMATCH`, `MISSING`, `REVIEW_REQUIRED`), and `review_required`.
- Update `SCENARIO_CONFIG_MAPPING` in `tools/landsync_datasets/generators/validation_case_generator.py` with standard reason codes and rule citations.

---

## 3. Running Reproduction & Test Commands

Before opening a pull request, run the full validation suite:

```bash
# 1. Regenerate dataset artifacts
python -m landsync_datasets all --config configs/default.yaml

# 2. Run automated test suite
pytest tests/
```

Verify that all 18 quality gates pass and 0 privacy scan violations are reported.
