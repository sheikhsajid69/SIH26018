# LANDSYNC-India Benchmark: Legal Scope and Governance Register

> **ADVISORY LEGAL DISCLAIMER:**  
> This document and the accompanying synthetic dataset represent an engineering and data-science benchmark designed for testing software systems. They **do NOT constitute legal advice**, convey legal title, or replace certified title verification by a licensed legal practitioner.

---

## 1. Governance Principles & Legal Traceability

Land administration in the Republic of India is a constitutional State subject (List II, Seventh Schedule, Constitution of India). While substantive property laws (such as the Transfer of Property Act, 1882, the Indian Easements Act, 1882, and the Registration Act, 1908) are central enactments, revenue administration, land records, survey settlement, and agricultural land reforms are strictly state-specific.

The LANDSYNC-India benchmark adheres to four core governance principles:
1. **Legal Traceability**: Every validation check is linked to an identifiable statutory provision, technical standard, or explicit heuristic assumption.
2. **Four-Tier Rule Categorization**: Mandates derived directly from primary statutory sources are strictly distinguished from configurable data-quality rules, synthetic benchmark assumptions, and legal interpretations requiring qualified review.
3. **Neutral Discrepancy Findings**: The benchmark engine produces neutral observational labels (`RECORD_MISMATCH`, `DOCUMENT_MISSING`, `SPATIAL_INCONSISTENCY`, `CHRONOLOGY_CONFLICT`, `REVIEW_REQUIRED`) rather than claiming fraud or illegal title.
4. **Zero-PII Synthetic Mandate**: Zero authentic citizen records, Aadhaar numbers, PAN cards, or confidential property disputes are included.

---

## 2. Four-Tier Rule Taxonomy

To maintain legal integrity, all 17 rules in `rule_catalogue` are categorized into one of four distinct categories:

| Category | Description | Authority / Weight | Example Rules |
| :--- | :--- | :--- | :--- |
| **Category A** | **Directly Verified Procedural Mandate** | Established directly from India Code gazette text or official state acts. | `RULE-REG-1908-SEC17`, `RULE-TPA-1882-SEC54`, `RULE-KLRA-1964-SEC128` |
| **Category B** | **Configurable Data-Quality Rule** | Engineering tolerance or operational data-cleansing threshold. | `RULE-AREA-TOL-001`, `RULE-AMBIGUOUS-UNIT-R13`, `RULE-SPATIAL-IOU-001` |
| **Category C** | **Synthetic Benchmark Assumption** | Standardizing convention established for benchmark tractability. | `RULE-DILRMP-ULPIN-STD` |
| **Category D** | **Legal Interpretation Requiring Qualified Review** | Complex statutory questions involving judicial discretion or soil scheduling. | `RULE-KLRA-1961-SEC63` |

---

## 3. Statutory Instruments and Researched References

### 3.1 Central Statutes (India Code Primary Sources)

1. **Registration Act, 1908 (Act No. 16 of 1908)**
   - *Section 17(1)(b)*: Compulsory registration of non-testamentary instruments transferring rights to immovable property of value >= Rs 100.
   - *Section 49*: Effect of non-registration. Documents required to be registered under Section 17 do not affect property or serve as transaction evidence unless registered.
   - *Official Source*: [https://www.indiacode.nic.in/handle/123456789/2261](https://www.indiacode.nic.in/handle/123456789/2261)
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

2. **Transfer of Property Act, 1882 (Act No. 4 of 1882)**
   - *Section 54*: Definition of sale; requirement that conveyance of tangible immovable property >= Rs 100 must be by registered instrument.
   - *Section 58 & 100*: Mortgages and statutory charges on immovable property.
   - *Official Source*: [https://www.indiacode.nic.in/handle/123456789/2338](https://www.indiacode.nic.in/handle/123456789/2338)
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

3. **Indian Easements Act, 1882 (Act No. 5 of 1882)**
   - *Section 4 & 15*: Dominant and servient heritage rights; acquisition of prescriptive right of way through 20 years uninterrupted enjoyment.
   - *Official Source*: [https://www.indiacode.nic.in/handle/123456789/2311](https://www.indiacode.nic.in/handle/123456789/2311)
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

4. **Hindu Succession Act, 1956 (Act No. 30 of 1956, as amended by Act 39 of 2005)**
   - *Section 6*: Equal devolution of coparcenary property interest; daughters hold equal coparcenary rights by birth. Confirmed retroactively by Supreme Court in *Vineeta Sharma v. Rakesh Sharma (2020)*.
   - *Official Source*: [https://www.indiacode.nic.in/handle/123456789/1715](https://www.indiacode.nic.in/handle/123456789/1715)
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

5. **Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013**
   - *Section 11(4)*: Prohibition of private transactions and encumbrances on lands notified under preliminary acquisition notices without prior sanction.
   - *Official Source*: [https://www.indiacode.nic.in/handle/123456789/2121](https://www.indiacode.nic.in/handle/123456789/2121)
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

6. **Digital Personal Data Protection Act, 2023 (Act No. 22 of 2023)**
   - *Section 4 & 6*: Lawful basis of processing; complete isolation of benchmark datasets through synthetic generation to eliminate re-identification risks.
   - *Official Source*: [https://www.meity.gov.in/content/digital-personal-data-protection-act-2023](https://www.meity.gov.in/content/digital-personal-data-protection-act-2023)
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

---

### 3.2 State Statutes: Karnataka Pilot Profile

1. **Karnataka Land Revenue Act, 1964 (Karnataka Act 12 of 1964)**
   - *Section 128*: Mandatory reporting of acquisition of rights within 3 months to revenue authorities.
   - *Section 129*: Register of mutations; mandatory 30-day statutory notice and objection period prior to certification.
   - *Section 95*: Conversion / diversion of agricultural land for non-agricultural use.
   - *Official Source*: Department of Parliamentary Affairs & Legislation, Karnataka Gazette.
   - *Verification Status*: `VERIFIED_PRIMARY_SOURCE`.

2. **Karnataka Land Reforms Act, 1961 (Karnataka Act 10 of 1962)**
   - *Section 63*: Ceiling limits on agricultural land holdings calculated in standard units.
   - *Official Source*: Karnataka Gazette repository.
   - *Verification Status*: `NEEDS_LEGAL_REVIEW` (soil classification schedules require agricultural soil survey calibration).

---

## 4. Engineering Constitution Rules

1. **Rule 13 (Ambiguous Unit Protection)**:
   Land units like *bigha*, *biswa*, and *katha* vary across states and tehsils (e.g., standard bigha vs pakka bigha vs kachha bigha). Rule 13 mandates that such units must **never** be silently normalized. The raw string and value are preserved, and a `REVIEW_REQUIRED` state is triggered.
2. **Rule 8 (Low-Confidence Escalation)**:
   Any automated extraction where field confidence falls below 0.80 must automatically escalate to human revenue officer review, regardless of whether the extracted string matches reference records.
