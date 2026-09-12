import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.services import LocalEvidenceStore, MockDocumentProvider, validate


class DemoPipelineTests(unittest.TestCase):
    def test_area_difference_routes_to_review(self):
        results = validate(MockDocumentProvider().extract(), DemoAuthorityAdapter().parcel("demo-parcel"))
        area = next(result for result in results if result.field == "area")
        self.assertEqual(area.result, "REVIEW_REQUIRED")

    def test_store_uses_hash_not_client_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            key, digest = LocalEvidenceStore(directory).save("demo-parcel", b"evidence")
        self.assertIn(digest, key)
        self.assertNotIn("../../", key)


if __name__ == "__main__":
    unittest.main()
