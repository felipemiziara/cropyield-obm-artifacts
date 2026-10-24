# Ontology-Based Metamodeling and OCL Rules as Semantic Contracts for Crop Yield Calculation in Farm Management Systems — Replication Package

This repository contains the open-science executable artifacts and verification scripts accompanying the paper:

> **Ontology-Based Metamodeling and OCL Rules as Semantic Contracts for Crop Yield Calculation in Farm Management Systems**

---

## Repository Structure

### 1. Executable Metamodel & OCL Verification (`models/`)
- [`models/cropyield.use`](models/cropyield.use) — Executable specification of the **CropYieldOBM** Ontology-Based Metamodel at the M2 level, including all 6 metaclasses anchored in the FAO AGROVOC thesaurus (`Farm`, `FieldPlot`, `Season`, `Crop`, `HarvestOperation`, `YieldMeasurement`), 5 structural associations/compositions, and **7 OCL 2.4 well-formedness invariants** annotated with their four engineering origins (`[Origin 1..4]`):
  1. `YieldMeasurement::positivePhysicalQuantities` (`[Origin 1: Physical definition]`)
  2. `YieldMeasurement::validMoistureRange` (`[Origin 4: FMIS premise]`)
  3. `YieldMeasurement::biologicalYieldLimit` (`[Origin 3: Sudduth MAXY/MINY]`)
  4. `YieldMeasurement::standardizedYieldConsistency` (`[Origin 2: MAPA IN 11/60]`)
  5. `HarvestOperation::temporalSeasonContainment` (`[Origin 4: FMIS premise]`)
  6. `FieldPlot::positiveCadastralArea` (`[Origin 1: Physical definition]`)
  7. `YieldMeasurement::spatialPlotContainment` (`[Origin 3: Sudduth POS]`)
- [`models/scenarios.soil`](models/scenarios.soil) — Instantiation and fault-injection script in the USE `.soil` language representing the three M1 validation scenarios evaluated in Section V of the paper (Table III):
  - **Scenario A (Valid Control):** Conforming commercial soybean (*Glycine max*, AGROVOC `c_3301`) harvest in `talhao04` ($85.5\text{ ha}$, $13.5\%$ harvested moisture standardized to $14.0\%$ reference moisture under MAPA IN 11/2007, yielding $3822.09\text{ kg/ha}$).
  - **Scenario B (Sensor & Temporal Faults):** Negative test injecting a capacitive moisture sensor drop (`moistureContent = 0.0%`), a header-overlap yield surge (`rawYield = 32000.0 kg/ha > 8000.0`), and an off-season operation date (`2024-06-20`).
  - **Scenario C (Cadastro, Stop & Formula Faults):** Negative test (after `reset`) injecting a degenerate plot (`talhao05.cadastralArea = 0.0 ha`), a combine stop with zero harvested area (`harvestedArea = 0.0 m²`), and an unstandardized wet yield stored as dry yield (`3800.0` vs. expected `3822.09 kg/ha`, a $22.09\text{ kg/ha}$ discrepancy).
- [`models/use_check_output.txt`](models/use_check_output.txt) — Literal execution trace produced by the **USE (UML-based Specification Environment) v7.5.0** model checker (`use -nogui models/cropyield.use models/scenarios.soil`), confirming 0 violations on Scenario A and deterministic isolation of the 3 targeted invariant violations on Scenarios B and C.
- [`models/agrovoc_anchors.csv`](models/agrovoc_anchors.csv) — Canonical ontological traceability registry linking each M2 metaclass, attribute, and reference crop species to its official FAO AGROVOC SKOS-XL concept URI (`http://aims.fao.org/aos/agrovoc/c_XXXX`) and bilingual preferred labels (`prefLabel_en`, `prefLabel_pt`).

### 2. Automated Ontological Audit (`scripts/`)
- [`scripts/check_agrovoc.py`](scripts/check_agrovoc.py) — Python verification script that audits every AGROVOC concept code (`c_XXXX`) referenced across `models/cropyield.use` and `models/scenarios.soil` against the canonical ontological anchor table [`models/agrovoc_anchors.csv`](models/agrovoc_anchors.csv) (and optionally against a full FAO AGROVOC SKOS-XL CSV dump via `--dump`).

### 3. Visual Architecture (`figures/`)
- [`figures/metamodelo_obm_en.png`](figures/metamodelo_obm_en.png) — UML class diagram of the **CropYield** Ontology-Based Metamodel (M2 layer) displaying the `<<agrovoc>>` stereotypes, structural multiplicities, and attached OCL invariants.

---

## Reproducing the Verification

### 1. Re-running the USE 7.5.0 OCL Verification
With [USE v7.5.0](https://sourceforge.net/projects/useocl/) installed on your `PATH`, execute from the repository root:

```bash
use -nogui models/cropyield.use models/scenarios.soil
```

Expected output matches [`models/use_check_output.txt`](models/use_check_output.txt):
- **Scenario A:** `checked 7 invariants in 0.011s, 0 failures.`
- **Scenario B:** `checked 7 invariants in 0.004s, 3 failures` (`HarvestOperation::temporalSeasonContainment`, `YieldMeasurement::biologicalYieldLimit`, `YieldMeasurement::validMoistureRange`).
- **Scenario C:** `checked 7 invariants in 0.003s, 3 failures` (`FieldPlot::positiveCadastralArea`, `YieldMeasurement::positivePhysicalQuantities`, `YieldMeasurement::standardizedYieldConsistency`).

### 2. Re-running the AGROVOC Anchor Audit
With Python 3.9+ installed, execute from the repository root:

```bash
python3 scripts/check_agrovoc.py
```

Expected output:
```text
OK: 17 canonical AGROVOC concepts verified across 2 executable model files (0 divergences).
```

---

## License

This replication package is released under the MIT License (see [`LICENSE`](LICENSE)) to support open science and reproducibility in agricultural software engineering.
