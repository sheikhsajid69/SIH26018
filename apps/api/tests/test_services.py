import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.blueprint import MockBlueprintProvider
from landsync.models import ExtractedField, Extraction, ValidationState
from landsync.services import LocalEvidenceStore, MockDocumentProvider, validate
from landsync.units import normalize_land_unit, parse_area_string


class LandSyncPipelineTests(unittest.TestCase):
    def setUp(self):
        self.adapter = DemoAuthorityAdapter()
        self.doc_provider = MockDocumentProvider()
        self.blueprint_provider = MockBlueprintProvider()

    def test_area_difference_routes_to_review(self):
        """Rule 8: Area discrepancy (2.31 vs 2.40 acre) must yield MISMATCH and require human review."""
        results = validate(self.doc_provider.extract(), self.adapter.parcel("demo-parcel"))
        area = next(result for result in results if result.field == "area")
        self.assertEqual(area.result, ValidationState.MISMATCH)
        self.assertEqual(area.severity, "MEDIUM")
        self.assertIn("Human verification required", area.explanation)

    def test_unit_normalization_standard_units(self):
        """Rule 13: Area must normalize to square meters while preserving formula and original units."""
        conv = normalize_land_unit(2.5, "acre")
        self.assertFalse(conv.is_ambiguous)
        self.assertAlmostEqual(conv.normalized_area_sqm, 2.5 * 4046.8564224, places=2)
        self.assertIn("4046.8564", conv.formula)

    def test_ambiguous_unit_defense_rule_13(self):
        """Rule 13: Regional units like 'bigha' or 'katha' must never be silently converted."""
        conv = normalize_land_unit(3.0, "bigha")
        self.assertTrue(conv.is_ambiguous)
        self.assertIsNone(conv.normalized_area_sqm)
        self.assertIn("cannot be automated safely", conv.advisory_notice)

    def test_store_uses_hash_and_prevents_traversal(self):
        """Rule 5: Filenames are never trusted; content addressing SHA-256 is enforced."""
        with tempfile.TemporaryDirectory() as directory:
            store = LocalEvidenceStore(directory)
            key, digest = store.save("demo-parcel", b"verified_content")
            self.assertIn(digest, key)
            self.assertNotIn("..", key)
            content = store.get(key)
            self.assertEqual(content, b"verified_content")
            # Ensure path traversal is blocked
            self.assertIsNone(store.get("../../etc/passwd"))

    def test_owner_name_validation_states(self):
        """Verify MATCH, PARTIAL_MATCH, and MISMATCH logic for holder names."""
        auth_data = self.adapter.parcel("demo-parcel")

        # 1. Exact match
        exact_ext = Extraction(
            provider="test",
            model_version="1.0",
            fields=[
                ExtractedField(
                    field_name="owner",
                    extracted_value="Ramesh Kumar",
                    normalized_value="ramesh kumar",
                    confidence=0.98,
                    source_location="test",
                    extraction_method="test",
                )
            ],
        )
        res = validate(exact_ext, auth_data)
        self.assertEqual(res[0].result, ValidationState.MATCH)

        # 2. Partial match
        partial_ext = Extraction(
            provider="test",
            model_version="1.0",
            fields=[
                ExtractedField(
                    field_name="owner",
                    extracted_value="Ramesh Kumar S/o Suresh",
                    normalized_value="ramesh kumar s/o suresh",
                    confidence=0.95,
                    source_location="test",
                    extraction_method="test",
                )
            ],
        )
        res = validate(partial_ext, auth_data)
        self.assertEqual(res[0].result, ValidationState.PARTIAL_MATCH)

        # 3. Direct mismatch
        mismatch_ext = Extraction(
            provider="test",
            model_version="1.0",
            fields=[
                ExtractedField(
                    field_name="owner",
                    extracted_value="Vikram Sharma",
                    normalized_value="vikram sharma",
                    confidence=0.96,
                    source_location="test",
                    extraction_method="test",
                )
            ],
        )
        res = validate(mismatch_ext, auth_data)
        self.assertEqual(res[0].result, ValidationState.MISMATCH)

    def test_blueprint_mock_provider_boundary(self):
        """Phase 6: Blueprint computer vision provider extracts advisory dimensions and geometry."""
        analysis = self.blueprint_provider.analyze("sketch.png", b"fake_raster_bytes")
        self.assertTrue(analysis.is_mock)
        self.assertGreaterEqual(analysis.confidence, 0.8)
        self.assertGreater(len(analysis.detected_dimensions), 0)
        self.assertIn("advisory only", analysis.advisory_disclaimer.lower())

    def test_authority_adapter_rich_models(self):
        """Verify typed domain models: LandParcel, Ownership, and MutationHistory."""
        parcel = self.adapter.parcel_model("demo-parcel")
        self.assertEqual(parcel.survey_number, "124/2")
        self.assertEqual(parcel.ulpin, "DEMO-ULPIN-27-000-124-2")

        ownership = self.adapter.ownership("demo-parcel")
        self.assertEqual(len(ownership), 1)
        self.assertEqual(ownership[0].holder_name, "Ramesh Kumar")

        history = self.adapter.mutation_history("demo-parcel")
        self.assertGreaterEqual(len(history), 3)
        self.assertEqual(history[0].event_type, "PARTITION")
        self.assertEqual(history[1].event_type, "SUCCESSION")


if __name__ == "__main__":
    unittest.main()
