# LANDSYNC-India Benchmark: Generation Methodology

## 1. Algorithmic Principles & Reproducibility

The LANDSYNC-India Synthetic Benchmark is produced by a modular, configuration-driven generation pipeline implemented in pure Python (`tools/landsync_datasets/`).

### Deterministic State Management
- All random variations are governed by a dedicated pseudo-random number generator instance (`random.Random(seed)`).
- The global Python `random` module state is **never** mutated, guaranteeing isolated and perfectly reproducible generation.
- Default generation seed is `42` under generator version `1.0.0`.
- All generated records carry stable, monotonic synthetic primary keys (`SYN-PARCEL-000001` .. `SYN-PARCEL-010000`).

---

## 2. Fictional Administrative Framework: Karnataka Pilot (`KA_PILOT`)

To ensure zero collision with authentic cadastral properties, the generator operates within a fictionalized administrative envelope:
- **State**: Karnataka (Synthetic Pilot Profile `KA_PILOT`)
- **District**: `SYN-DIST-01` ("Mayura District")
- **Taluk**: `SYN-TALUK-01` ("Kalyana Taluk")
- **Revenue Villages**:
  - `SYN-VIL-01` ("Hemavathi") — Lat: [12.95, 12.99], Lon: [77.56, 77.61]
  - `SYN-VIL-02` ("Kaveri") — Lat: [12.96, 13.00], Lon: [77.61, 77.66]
  - `SYN-VIL-03` ("Sharavathi") — Lat: [12.91, 12.95], Lon: [77.53, 77.58]
  - `SYN-VIL-04` ("Netravathi") — Lat: [13.00, 13.04], Lon: [77.57, 77.62]

All survey numbers (e.g. `101/1`, `145/2A`), plot numbers, and book/page references are procedurally synthesized.

---

## 3. High-Precision Area Normalization & Rule 13 Defense

Area measurements are converted to SI Square Metres using exact `decimal.Decimal` factors based on statutory conversion schedules:
- `1 acre = 40 gunthas = 4,046.8564224 m²`
- `1 hectare = 10,000.0 m²`
- `1 cent = 40.468564224 m²`
- `1 sq ft = 0.09290304 m²`

### Enforcing Rule 13 (Ambiguous Unit Protection)
Regional units such as *bigha*, *biswa*, *katha*, *kanal*, and *marla* vary drastically in size across Northern and Eastern India (ranging from 1,337 m² in parts of West Bengal to over 2,500 m² in Rajasthan). The generator strictly implements **Rule 13 of the LANDSYNC Engineering Constitution**:
- Automated conversion of ambiguous regional units is blocked.
- `normalized_value_sqm` is set to `None`.
- `conversion_rule` is recorded as `RULE_13_AMBIGUOUS_REGIONAL_UNIT`.
- The record is flagged with `is_ambiguous=True`, mandating human officer review.

---

## 4. Geospatial Synthesis & Metric Geodesics

Cadastral boundaries are output as standard GeoJSON Polygons in coordinate reference system `EPSG:4326`.

### Accurate Metric Geometry Calculation
Direct calculation of square metres from latitude/longitude degree deltas is mathematically invalid due to meridian convergence. The geospatial engine projects coordinates at the polygon centroid latitude using WGS84 ellipsoidal parameters:
$$\text{meters\_per\_deg\_lat} = 111132.92 - 559.82 \cos(2\phi) + 1.175 \cos(4\phi)$$
$$\text{meters\_per\_deg\_lon} = 111412.84 \cos(\phi) - 93.5 \cos(3\phi)$$

Projected metric Cartesian coordinates are evaluated via the Shoelace formula to yield true ground metric areas.

### Controlled Cadastral Anomalies
The engine synthesizes intentional topological variations for spatial validation testing:
- **Valid Polygons**: 4- to 7-sided convex parcels matching schedule extents within 0.2% tolerance.
- **Self-Intersecting Bow-Ties**: Swapping non-adjacent vertices to create invalid self-intersecting boundaries.
- **Unclosed Rings**: First and last coordinate mismatching by $10^{-4}$ degrees.
- **Sliver Parcels**: High aspect-ratio (> 50:1) boundary slivers.
- **Area Variance**: Polygons scaled by 25% (area delta ~56%) to test spatial-vs-textual consistency checks.

---

## 5. Document AI Annotation & Optical Degradation

For 5,500 documents, the engine creates 33,000 field annotations with pixel bounding boxes `[ymin, xmin, ymax, xmax]`. Document quality tiers (`PRISTINE`, `CLEAN`, `SCANNED_FAINT`, `OCR_DEGRADED`) drive extraction confidence scores.

Optical degradation simulation models real-world OCR confusion matrices:
- Numeral/character swaps: `0` $\leftrightarrow$ `O`, `1` $\leftrightarrow$ `l`, `8` $\leftrightarrow$ `B`, `5` $\leftrightarrow$ `S`.
- Whitespace and separator noise: duplicate spaces, collapsed spaces, comma/period substitutions.

---

## 6. Group-Aware Split Strategy (Zero Data Leakage)

Random row splitting leads to severe information leakage in relational benchmarks (e.g., training on a deed and testing on the same parcel's RTC extract).

To guarantee leakage-safe evaluation:
1. Every parcel belongs to a `split_group_id` (`GRP-00001` .. `GRP-02000`).
2. All documents, claims, mutation events, geometries, and validation cases belonging to that group are assigned as an indivisible unit to either Train, Validation, or Test.
3. Automated leakage gates verify:
   $$\text{Train}_{\text{parcels}} \cap \text{Val}_{\text{parcels}} = \emptyset, \quad \text{Train}_{\text{parcels}} \cap \text{Test}_{\text{parcels}} = \emptyset, \quad \text{Val}_{\text{parcels}} \cap \text{Test}_{\text{parcels}} = \emptyset$$
