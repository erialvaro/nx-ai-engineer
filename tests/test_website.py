"""The stdlib-only website generator builds a static site from the repo docs."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "website"))

import generate  # noqa: E402


class TestWebsiteGenerator(unittest.TestCase):
    def test_build_produces_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = generate.build(Path(tmp))
            index = out / "index.html"
            self.assertTrue(index.exists())
            html = index.read_text(encoding="utf-8")
            self.assertIn("<nav>", html)
            self.assertIn("nx-ai-engineer", html)
            # packages page is generated and lists the 8 packages
            pkgs = (out / "packages.html").read_text(encoding="utf-8")
            for name in ("nx-core", "nx-cli", "nx-knowledge", "nx-runtime"):
                self.assertIn(name, pkgs)

    def test_markdown_subset_renders(self):
        md = "# Title\n\nA **bold** word and `code`.\n\n- one\n- two\n\n```\nx=1\n```\n"
        out = generate.md_to_html(md)
        self.assertIn("<h1>Title</h1>", out)
        self.assertIn("<strong>bold</strong>", out)
        self.assertIn("<code>code</code>", out)
        self.assertIn("<li>one</li>", out)
        self.assertIn("<pre><code>", out)


if __name__ == "__main__":
    unittest.main()
