import io
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from fastapi.testclient import TestClient
from landsync.main import app


class LandSyncAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["mode"], "DEMO_SYNTHETIC_ONLY")

    def test_unauthorized_access(self):
        res = self.client.get("/api/v1/parcels/demo-parcel")
        self.assertEqual(res.status_code, 401)

    def test_citizen_can_read_parcel_and_history(self):
        headers = {"Authorization": "Bearer demo-citizen"}
        res = self.client.get("/api/v1/parcels/demo-parcel", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["record"]["survey_number"], "124/2")

        res_hist = self.client.get("/api/v1/parcels/demo-parcel/history", headers=headers)
        self.assertEqual(res_hist.status_code, 200)
        self.assertGreaterEqual(len(res_hist.json()["mutation_history"]), 3)

    def test_citizen_cannot_decide_review_case(self):
        """Rule: Citizen must never be allowed to record an officer decision."""
        headers = {"Authorization": "Bearer demo-citizen"}
        payload = {"resolution": "REQUIRES_DOCUMENT", "notes": "Citizen trying to decide."}
        res = self.client.post("/api/v1/review-cases/demo-case/decision", json=payload, headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_officer_can_decide_and_creates_audit(self):
        """Officer decision succeeds and creates immutable audit record."""
        headers = {"Authorization": "Bearer demo-officer"}
        payload = {
            "resolution": "REQUIRES_DOCUMENT",
            "notes": "Original register inspection needed for 0.09 acre variance.",
        }
        res = self.client.post("/api/v1/review-cases/demo-case/decision", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        case_data = res.json()
        self.assertEqual(case_data["status"], "RESOLVED")
        self.assertEqual(case_data["assigned_officer"], "demo-officer")

        # Verify audit event
        audit_res = self.client.get("/api/v1/audit", headers=headers)
        self.assertEqual(audit_res.status_code, 200)
        events = audit_res.json()["events"]
        decision_event = next(e for e in events if e["action"] == "REVIEW_DECISION_RECORDED")
        self.assertEqual(decision_event["actor_id"], "demo-officer")

    def test_admin_health_endpoint_rbac(self):
        """Admin can access system health; citizen is blocked."""
        citizen_headers = {"Authorization": "Bearer demo-citizen"}
        admin_headers = {"Authorization": "Bearer demo-admin"}

        res_cit = self.client.get("/api/v1/admin/health", headers=citizen_headers)
        self.assertEqual(res_cit.status_code, 403)

        res_adm = self.client.get("/api/v1/admin/health", headers=admin_headers)
        self.assertEqual(res_adm.status_code, 200)
        self.assertEqual(res_adm.json()["system"], "LANDSYNC AI Core")

    def test_upload_and_validation_pipeline(self):
        """Uploading deed triggers mock extraction and consistency validation."""
        headers = {"Authorization": "Bearer demo-citizen"}
        fake_pdf = io.BytesIO(b"%PDF-1.4 demo deed stream")
        files = {"file": ("registered_sale_deed_124_2.pdf", fake_pdf, "application/pdf")}

        res = self.client.post("/api/v1/parcels/demo-parcel/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("document", data)
        self.assertIn("validation", data)
        self.assertIn("review_case", data)

        # Check SHA-256 hash preservation
        sha = data["document"]["sha256"]
        self.assertEqual(len(sha), 64)

    def test_consistency_report_endpoint(self):
        """Report endpoint returns comprehensive digital land profile report."""
        headers = {"Authorization": "Bearer demo-citizen"}
        res = self.client.get("/api/v1/parcels/demo-parcel/report", headers=headers)
        self.assertEqual(res.status_code, 200)
        report = res.json()
        self.assertIn("parcel", report)
        self.assertIn("validation_summary", report)
        self.assertIn("mutation_history", report)
        self.assertIn("ADVISORY NOTICE", report["disclaimer"])


if __name__ == "__main__":
    unittest.main()
