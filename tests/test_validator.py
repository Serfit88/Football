from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_site import validate


class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.html = '<!doctype html><html lang="ru"><head><title>Test</title><link rel="stylesheet" href="style.css"></head><body><main id="main"><img src="photo.jpg" alt="Test"></main><script src="main.js"></script></body></html>'
        self.write('index.html', self.html)
        self.write('style.css', 'body{color:black}')
        self.write('main.js', 'console.log("ok");')
        (self.root / 'photo.jpg').write_bytes(b'fixture')

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        (self.root / name).write_text(data, encoding='utf-8')

    def test_valid_site_is_accepted(self):
        self.assertEqual(validate(self.root), [])

    def test_missing_image_is_rejected(self):
        (self.root / 'photo.jpg').unlink()
        self.assertTrue(any('missing local resource' in e for e in validate(self.root)))

    def test_duplicate_id_is_rejected(self):
        self.write('index.html', self.html.replace('</main>', '<p id="main">Duplicate</p></main>'))
        self.assertTrue(any('duplicate id' in e for e in validate(self.root)))

    def test_unclosed_tag_is_rejected(self):
        self.write('index.html', self.html.replace('</main>', ''))
        self.assertTrue(any('unclosed HTML' in e for e in validate(self.root)))

    def test_invalid_css_is_rejected(self):
        self.write('style.css', 'body{color:black')
        self.assertTrue(any('unbalanced CSS' in e for e in validate(self.root)))


if __name__ == '__main__':
    unittest.main()
