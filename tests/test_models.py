import json
import tempfile
import unittest
from pathlib import Path

from kpa.models import coerce_listing, load_listings


class ModelTests(unittest.TestCase):
    def test_coerce_minimal_listing(self):
        item = coerce_listing({"title": "A", "price": "10", "description": "B"})
        self.assertEqual(item.title, "A")
        self.assertEqual(item.price, "10")
        self.assertEqual(item.condition, "Gut")

    def test_rejects_sensitive_keys(self):
        with self.assertRaisesRegex(ValueError, "forbidden"):
            coerce_listing({"title": "A", "price": "10", "description": "B", "password": "no"})

    def test_load_json_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.json"
            path.write_text(json.dumps([{"title": "A", "price": "10", "description": "B"}]), encoding="utf-8")
            items = load_listings(path)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "item-001")

    def test_category_string_split(self):
        item = coerce_listing({"title": "A", "price": "10", "description": "B", "category_path": "A > B > C"})
        self.assertEqual(item.category_path, ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
