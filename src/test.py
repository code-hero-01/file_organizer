import tempfile
import unittest
from pathlib import Path

from classifier import Classifier
from file_organizer import organize_files
from file_scanner import file_scanner
from models import FileInfo, Rule, Status


class Tests(unittest.TestCase):
    def test_classifier_assigns_with_one_matching_rule(self):
        classifier = Classifier([Rule("images", [], ["png"])])
        file = FileInfo(Path("sample.png"), "sample", "png", ("sample",))
        result = classifier.classify(file)
        self.assertEqual(result.status, Status.ASSIGNED)
        self.assertEqual(result.folder, "images")

    def test_classifier_returns_unknown_when_nothing_matches(self):
        classifier = Classifier([
            Rule("pics", ["photo"], ["png"]),
            Rule("docs", ["report"], ["pdf"]),
        ])
        file = FileInfo(Path("mystery.xyz"), "mystery", "xyz", ("mystery",))
        self.assertEqual(classifier.classify(file).status, Status.UNKNOWN)

    def test_scanner_preserves_paths_and_extensionless_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README").write_text("text", encoding="utf-8")
            (root / "holiday photo.png").write_text("image", encoding="utf-8")

            scanned = file_scanner(root)

            self.assertEqual(len(scanned), 2)
            readme = next(item for item in scanned if item.path.name == "README")
            self.assertEqual(readme.extension, "")
            photo = next(item for item in scanned if item.path.name.endswith(".png"))
            self.assertIn("holiday", photo.tokens)

    def test_organizer_moves_selected_file_and_skips_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            move_me = root / "move.txt"
            keep_me = root / "keep.txt"
            move_me.write_text("move", encoding="utf-8")
            keep_me.write_text("keep", encoding="utf-8")

            report = organize_files({
                move_me: root / "docs",
                keep_me: None,
            })

            self.assertTrue((root / "docs" / "move.txt").exists())
            self.assertFalse(move_me.exists())
            self.assertTrue(keep_me.exists())
            self.assertEqual(len(report["moved"]), 1)
            self.assertEqual(len(report["skipped"]), 1)

    def test_organizer_does_not_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "report.txt"
            destination = root / "docs"
            source.write_text("new", encoding="utf-8")
            destination.mkdir()
            (destination / "report.txt").write_text("old", encoding="utf-8")

            report = organize_files({source: destination})

            self.assertTrue(source.exists())
            self.assertEqual((destination / "report.txt").read_text(encoding="utf-8"), "old")
            self.assertEqual(len(report["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
