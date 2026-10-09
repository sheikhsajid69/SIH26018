# LANDSYNC-India: Privacy and Synthetic-Data Architecture

## 1. Absolute Synthetic Data Policy

The LANDSYNC-India benchmark operates under an uncompromising privacy policy:
**Every person, identifier, document, event, and boundary is 100% synthetic.**

### Explicit Exclusions & Prohibitions
To protect citizen privacy and uphold data security principles:
1. **Never scrape or copy real landowner identities**: No authentic citizen land registries (e.g. live Bhoomi, Dharani, AnyROR, BanglarBhumi) were scraped or ingested into this release.
2. **Never generate valid authentic identity credentials**:
   - Real 12-digit Aadhaar formats (`^[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}$`) are strictly prohibited.
   - Real 10-character PAN patterns (`^[A-Z]{5}[0-9]{4}[A-Z]{1}$`) are strictly prohibited.
   - Genuine personal telephone numbers and email addresses are prohibited. All emails use reserved testing domains (e.g. `@example.invalid`).
3. **No authentic government seals or signatures**: Document text mocks contain only advisory synthetic text headers and zero scanned official stamps, emblems, or forged bureaucratic signatures.
4. **Fictional benchmark ULPIN tokens**: Identifiers resembling Bhu-Aadhaar / ULPIN are explicitly prefixed with `SYN-ULPIN-` and documented as internal research keys.

---

## 2. Compliance with DPDP Act, 2023 & Fair Information Practices

Under Section 4 and Section 6 of the *Digital Personal Data Protection Act, 2023 (DPDP Act)*, processing of personal data without explicit legal basis and notice is restricted.

By utilizing mathematically generated synthetic data:
- **No re-identification risk**: No natural person's private property status, tax assessment, mortgage balance, or family inheritance dispute is exposed.
- **Open research sharing**: Researchers, data scientists, and engineers worldwide can collaborate, download, and benchmark models on Kaggle without data transfer agreements or privacy clearance bottlenecks.
- **Fair representation**: Personas and family names are generated algorithmically using balanced statistical distributions across regional nomenclature.

---

## 3. Automated Privacy Scan Verification

Prior to exporting the benchmark manifest, the automated scanner (`tools/landsync_datasets/privacy/scanner.py`) audits all generated rows.

### Scanner Specifications
```python
# Prohibited credential regex checks
AADHAAR_PATTERN = r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b"
PAN_PATTERN = r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
INDIAN_MOBILE_PATTERN = r"\b(\+91[\-\s]?)?[6-9]\d{9}\b"
PROHIBITED_EMAIL_DOMAINS = r"@(gmail\.com|yahoo\.com|outlook\.com|nic\.in|gov\.in)\b"
SECRET_PATTERN = r"\b(AKIA[0-9A-Z]{16}|bearer\s+[A-Za-z0-9\-\._~\+\/]+=*)\b"
LOCAL_PATH_PATTERN = r"\b([A-Za-z]:\\[Users|Windows]|/(Users|home)/[a-zA-Z0-9_\-\.]+)\b"
```

In Release v1.0.0, **0 violations** were detected across all 10,000 parcels, 10,000 parties, 5,500 documents, and 2,880 validation cases.

---

## 4. Conspicuous Public Data Declaration

Every published file in this collection carries the immutable advisory notice:

> **"100% SYNTHETIC DATA — NOT AN OFFICIAL LAND RECORD."**
