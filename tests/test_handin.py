"""Exercise distribution building in disposable repositories."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class Handin(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copyfile(Path(__file__).resolve().parents[1] / "build_handin.sh",
                        self.root / "build_handin.sh")
        (self.root / "program").mkdir()
        (self.root / "program/CLAUDE.md").write_text("private notes")
        (self.root / "program/example.py").write_text("pass\n")
        (self.root / "main.pdf").write_bytes(b"recorded PDF")
        (self.root / ".gitattributes").write_text("program/CLAUDE.md export-ignore\n")
        (self.root / ".gitignore").write_text("handin/\n.handin-build.*/\nold_stuff/builds/\n")
        self.git("init", "-q")
        self.commit()
        (self.root / "handin").mkdir()
        (self.root / "handin/main.pdf").write_bytes(b"previous PDF")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def commit(self):
        self.git("add", "-A")
        self.git("-c", "user.name=Bundle Test", "-c", "user.email=bundle@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")

    def build(self):
        return subprocess.run(["sh", "build_handin.sh"], cwd=self.root, capture_output=True)

    def test_archive_excludes_notes_and_preserves_old_bundle(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "handin/main.pdf").read_bytes(), b"recorded PDF")
        self.assertFalse((self.root / "handin/program/CLAUDE.md").exists())
        previous = list(self.root.glob("old_stuff/builds/handin.previous.*/handin/main.pdf"))
        self.assertEqual(len(previous), 1)
        self.assertEqual(previous[0].read_bytes(), b"previous PDF")
        self.assertFalse(list(self.root.glob(".handin-build.*")))

    def test_missing_pdf_preserves_existing_bundle(self):
        (self.root / "main.pdf").unlink()
        self.commit()
        self.assertNotEqual(self.build().returncode, 0)
        self.assertEqual((self.root / "handin/main.pdf").read_bytes(), b"previous PDF")

    def test_failed_archive_preserves_existing_bundle(self):
        self.git("rm", "-r", "program")
        self.commit()
        self.assertNotEqual(self.build().returncode, 0)
        self.assertEqual((self.root / "handin/main.pdf").read_bytes(), b"previous PDF")
        self.assertFalse(list(self.root.glob(".handin-build.*")))

    def test_notes_guard_preserves_existing_bundle(self):
        (self.root / "program/TASKS.md").write_text("private tasks")
        self.commit()
        self.assertNotEqual(self.build().returncode, 0)
        self.assertEqual((self.root / "handin/main.pdf").read_bytes(), b"previous PDF")

    def test_dirty_tree_preserves_existing_bundle(self):
        (self.root / "uncommitted.tex").write_text("uncommitted")
        self.assertNotEqual(self.build().returncode, 0)
        self.assertEqual((self.root / "handin/main.pdf").read_bytes(), b"previous PDF")
