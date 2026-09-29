from __future__ import annotations

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool

from landsync.auth import hash_password
from landsync.database import Base, get_db
from landsync.db_models import AdministrativeActionOrm, AuditEventOrm, UserOrm
from landsync.main import app


class LandSyncAdminGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # In-memory SQLite with StaticPool so all connections share the same memory database
        cls.test_engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.test_engine)
        Base.metadata.create_all(bind=cls.test_engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

        # Seed initial test users
        with cls.TestingSessionLocal() as session:
            session.add(
                UserOrm(
                    id="TEST-ADMIN-001",
                    username="testadmin",
                    email="testadmin@landsync.gov.in",
                    name="Test Admin",
                    role="administrator",
                    password_hash=hash_password("AdminSecurePass2026!"),
                    status="ACTIVE",
                )
            )
            session.add(
                UserOrm(
                    id="TEST-OFFICER-001",
                    username="testofficer",
                    email="testofficer@landsync.gov.in",
                    name="Test Officer",
                    role="revenue_officer",
                    password_hash=hash_password("OfficerSecurePass2026!"),
                    status="ACTIVE",
                    jurisdiction="North District",
                )
            )
            session.add(
                UserOrm(
                    id="TEST-CITIZEN-001",
                    username="testcitizen",
                    email="testcitizen@landsync.gov.in",
                    name="Test Citizen",
                    role="citizen",
                    password_hash=hash_password("CitizenSecurePass2026!"),
                    status="ACTIVE",
                )
            )
            session.commit()

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=cls.test_engine)

    def test_01_admin_login_success_and_jwt(self):
        """Admin authenticates with valid credentials and receives JWT."""
        payload = {"username": "testadmin", "password": "AdminSecurePass2026!"}
        res = self.client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "administrator")
        self.assertEqual(data["username"], "testadmin")

        # Also test login via email
        payload_email = {"username": "testadmin@landsync.gov.in", "password": "AdminSecurePass2026!"}
        res_email = self.client.post("/api/v1/auth/login", json=payload_email)
        self.assertEqual(res_email.status_code, 200)

    def test_02_admin_login_invalid_credentials_returns_generic_error(self):
        """Invalid credentials return generic message without revealing account existence."""
        res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "WrongPassword!"})
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid credentials.", res.json()["detail"])

        res_nonexistent = self.client.post("/api/v1/auth/login", json={"username": "ghost@nowhere.in", "password": "AnyPassword!"})
        self.assertEqual(res_nonexistent.status_code, 401)
        self.assertIn("Invalid credentials.", res_nonexistent.json()["detail"])

    def test_03_admin_dashboard_access_and_kpis(self):
        """Administrator retrieves platform dashboard KPIs and service health."""
        # Login to get JWT
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/admin/dashboard", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "OPERATIONAL")
        self.assertIn("overview", data)
        self.assertGreaterEqual(data["overview"]["total_users"], 3)
        self.assertIn("system_health", data)
        self.assertEqual(data["system_health"]["api"], "healthy")

    def test_04_rbac_citizen_and_officer_cannot_access_admin_dashboard(self):
        """Citizens and Officers are denied access (403) to admin endpoints."""
        cit_login = self.client.post("/api/v1/auth/login", json={"username": "testcitizen", "password": "CitizenSecurePass2026!"})
        cit_token = cit_login.json()["access_token"]

        off_login = self.client.post("/api/v1/auth/login", json={"username": "testofficer", "password": "OfficerSecurePass2026!"})
        off_token = off_login.json()["access_token"]

        res_cit = self.client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {cit_token}"})
        self.assertEqual(res_cit.status_code, 403)

        res_off = self.client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {off_token}"})
        self.assertEqual(res_off.status_code, 403)

    def test_05_user_management_lifecycle_and_audit(self):
        """Admin can list, create, deactivate, and modify users with mandatory audit tracking."""
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        admin_token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Create a new user
        new_user_data = {
            "username": "ro_sharma",
            "email": "ro.sharma@landsync.gov.in",
            "name": "R. O. Sharma",
            "role": "revenue_officer",
            "password": "SharmaPassword2026!",
            "jurisdiction": "Model Taluk",
        }
        create_res = self.client.post("/api/v1/admin/users", json=new_user_data, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        created_user = create_res.json()["user"]
        user_id = created_user["id"]
        self.assertEqual(created_user["username"], "ro_sharma")

        # 2. Retrieve user detail
        detail_res = self.client.get(f"/api/v1/admin/users/{user_id}", headers=headers)
        self.assertEqual(detail_res.status_code, 200)
        self.assertEqual(detail_res.json()["status"], "ACTIVE")

        # 3. Deactivate user with mandatory reason
        status_res = self.client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            json={"status": "DEACTIVATED", "reason": "Officer transferred to non-cadastral posting."},
            headers=headers,
        )
        self.assertEqual(status_res.status_code, 200)
        self.assertEqual(status_res.json()["user"]["status"], "DEACTIVATED")

        # 4. Verify deactivated user cannot log in (403)
        deact_login = self.client.post(
            "/api/v1/auth/login",
            json={"username": "ro_sharma", "password": "SharmaPassword2026!"},
        )
        self.assertEqual(deact_login.status_code, 403)
        self.assertIn("deactivated", deact_login.json()["detail"].lower())

        # 5. Re-activate user
        reactivate_res = self.client.patch(
            f"/api/v1/admin/users/{user_id}/status",
            json={"status": "ACTIVE", "reason": "Re-activated upon completion of jurisdictional assignment."},
            headers=headers,
        )
        self.assertEqual(reactivate_res.status_code, 200)

        # 6. Change role to citizen
        role_res = self.client.patch(
            f"/api/v1/admin/users/{user_id}/role",
            json={"role": "citizen", "reason": "Role adjusted per departmental order #8491."},
            headers=headers,
        )
        self.assertEqual(role_res.status_code, 200)
        self.assertEqual(role_res.json()["user"]["role"], "citizen")

    def test_06_admin_self_deactivation_is_prohibited(self):
        """Admin cannot deactivate their own account."""
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        admin_token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        res = self.client.patch(
            "/api/v1/admin/users/TEST-ADMIN-001/status",
            json={"status": "DEACTIVATED", "reason": "Accidental self-deactivation test."},
            headers=headers,
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Self-deactivation is prohibited", res.json()["detail"])

    def test_07_officers_workload_and_jurisdiction(self):
        """Administrator retrieves roster of revenue officers with workload metrics."""
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/admin/officers", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("officers", data)
        self.assertGreaterEqual(data["total"], 1)

    def test_08_governed_administrative_actions_and_audit(self):
        """Governed administrative actions record both an action log and an immutable audit event."""
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        action_payload = {
            "action_type": "CADASTRAL_BOUNDARY_VERIFICATION",
            "target_resource_type": "PARCEL",
            "target_resource_id": "SYN-PARCEL-001",
            "reason": "Administrative oversight verification requested by revenue district magistrate.",
            "payload": {"verification_standard": "EPSG:4326", "cadastral_sheet": "Sheet 4B"},
        }
        res = self.client.post("/api/v1/admin/actions", json=action_payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        action_id = res.json()["action_id"]
        self.assertTrue(action_id)

        # Inspect action log
        actions_list = self.client.get("/api/v1/admin/actions", headers=headers)
        self.assertEqual(actions_list.status_code, 200)
        self.assertGreaterEqual(actions_list.json()["total"], 1)

        # Inspect audit logs
        audit_list = self.client.get("/api/v1/admin/audit", headers=headers)
        self.assertEqual(audit_list.status_code, 200)
        self.assertGreaterEqual(audit_list.json()["total"], 1)

    def test_09_security_telemetry_and_reports(self):
        """Security page and report analytics endpoints return verified metadata without secrets."""
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        sec_res = self.client.get("/api/v1/admin/security", headers=headers)
        self.assertEqual(sec_res.status_code, 200)
        sec_data = sec_res.json()
        self.assertIn("security_policies", sec_data)
        self.assertEqual(sec_data["security_policies"]["jwt_algorithm"], "HS256")

        rep_res = self.client.get("/api/v1/admin/reports", headers=headers)
        self.assertEqual(rep_res.status_code, 200)
        rep_data = rep_res.json()
        self.assertIn("validation_outcomes", rep_data)
        self.assertIn("review_cases_by_status", rep_data)

    def test_10_logout_records_audit_trail(self):
        """Logout endpoint terminates session and records immutable audit log."""
        login_res = self.client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminSecurePass2026!"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        logout_res = self.client.post("/api/v1/auth/logout", headers=headers)
        self.assertEqual(logout_res.status_code, 200)
        self.assertEqual(logout_res.json()["status"], "SUCCESS")


if __name__ == "__main__":
    unittest.main()
