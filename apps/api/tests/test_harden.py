import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from fastapi.testclient import TestClient
from landsync.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from landsync.extraction import MockDocumentProvider, TextAndPdfDocumentProvider
from landsync.gis import bbox_iou, compare_geometries, polygon_area_sqm
from landsync.main import app
from landsync.models import Role
from landsync.storage import LocalEvidenceStorage, StorageTamperError


class LandSyncHardenedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_bcrypt_password_hashing(self):
        """Verify bcrypt password hashing and verification."""
        password = "SecureGovAdminPassword@2026"
        hashed = hash_password(password)
        self.assertTrue(hashed.startswith("$2"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_generation_and_validation(self):
        """Verify HS256 JWT access token encoding and claims decoding."""
        token = create_access_token("officer-42", Role.OFFICER.value)
        user_id, role = decode_access_token(token)
        self.assertEqual(user_id, "officer-42")
        self.assertEqual(role, Role.OFFICER)

    def test_jwt_auth_header_endpoint_access(self):
        """Verify API endpoints accept cryptographically signed JWT tokens."""
        token = create_access_token("officer-42", Role.OFFICER.value)
        headers = {"Authorization": f"Bearer {token}"}
        res = self.client.get("/api/v1/review-cases", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_health_probes(self):
        """Verify liveness and readiness probes for cloud deployment."""
        res_live = self.client.get("/health/live")
        self.assertEqual(res_live.status_code, 200)
        self.assertEqual(res_live.json()["status"], "alive")

        res_ready = self.client.get("/health/ready")
        self.assertEqual(res_ready.status_code, 200)
        self.assertEqual(res_ready.json()["status"], "ready")

    def test_storage_tamper_immutability_defense(self):
        """Rule 5: Verify WORM (Write Once, Read Many) raises StorageTamperError on content alteration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = LocalEvidenceStorage(tmp_dir)
            key, digest = store.save("SYN-PARCEL-001", b"original authentic title deed")
            
            # Idempotent write with identical content succeeds
            key2, digest2 = store.save("SYN-PARCEL-001", b"original authentic title deed")
            self.assertEqual(key, key2)
            self.assertEqual(digest, digest2)

            # Altering the content under the existing key raises StorageTamperError
            target_path = store.root / key
            target_path.write_bytes(b"tampered content")
            with self.assertRaises(StorageTamperError):
                store.save("SYN-PARCEL-001", b"original authentic title deed")

    def test_text_and_pdf_document_provider(self):
        """Verify text/PDF parsing with Indian land record regex heuristics."""
        provider = TextAndPdfDocumentProvider()
        sample_doc = (
            "GOVERNMENT OF KARNATAKA - REVENUE DEPARTMENT\n"
            "RECORD OF RIGHTS (RTC)\n"
            "Owner: Suresh Kumar Rao\n"
            "Survey Number: 45/3A\n"
            "Plot Number: 12-C\n"
            "Total Area: 3.50 acre\n"
            "Village: Sampurna\n"
            "Land Use: Agricultural\n"
        ).encode("utf-8")

        ext = provider.extract("rtc_record.txt", sample_doc, "text/plain", "demo-parcel")
        extracted_fields = {f.field_name: f.extracted_value for f in ext.fields}
        self.assertEqual(extracted_fields.get("owner"), "Suresh Kumar Rao")
        self.assertEqual(extracted_fields.get("survey_number"), "45/3A")
        self.assertEqual(extracted_fields.get("area"), "3.50 acre")
        self.assertEqual(extracted_fields.get("village"), "Sampurna")

    def test_gis_spatial_metrics_rule_14(self):
        """Rule 14: Verify polygon geodesic area and IoU calculation with EPSG:4326 advisory."""
        # 1-acre square approximate coordinates near Bangalore (12.97, 77.59)
        poly_coords = [
            [77.5944, 12.9716],
            [77.5950, 12.9716],
            [77.5950, 12.9721],
            [77.5944, 12.9721],
            [77.5944, 12.9716],
        ]
        area_sqm = polygon_area_sqm(poly_coords)
        self.assertGreater(area_sqm, 2000.0)
        self.assertLess(area_sqm, 5000.0)

        geom_a = {"type": "Polygon", "coordinates": [poly_coords]}
        comparison = compare_geometries(geom_a, geom_a)
        self.assertEqual(comparison["status"], "CONSISTENT")
        self.assertEqual(comparison["crs"], "EPSG:4326 (WGS84)")
        self.assertAlmostEqual(comparison["iou_score"], 1.0, places=2)
        self.assertIn("SPATIAL ADVISORY", comparison["advisory_disclaimer"])

    def test_observability_middleware_headers(self):
        """Verify X-Request-ID and X-Response-Time-Ms headers are present on all API responses."""
        res = self.client.get("/health")
        self.assertIn("x-request-id", res.headers)
        self.assertIn("x-response-time-ms", res.headers)
        duration_ms = float(res.headers["x-response-time-ms"])
        self.assertGreaterEqual(duration_ms, 0.0)
