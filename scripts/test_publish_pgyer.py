import unittest
from publish_pgyer import pgyer_entry

class PgyerTests(unittest.TestCase):
    def test_pinned_page_accepts_only_identical_signed_bytes(self):
        d={'version':'1.1.14','build':5016,'sha256':'a'*64}
        page='https://www.pgyer.com/app/build/'+'b'*32
        self.assertEqual(pgyer_entry(d,'a'*64,page,'更新')['downloadUrl'],page)
        with self.assertRaises(ValueError):pgyer_entry(d,'c'*64,page,'更新')

    def test_mutable_shortlink_and_signed_oss_url_are_not_permanent_manifests(self):
        for page in ['https://www.pgyer.com/yingyutv','https://oss.pgyer.com/file.apk?auth_key=secret','https://unrelated.example/app/build/'+'b'*32]:
            with self.assertRaises(ValueError):pgyer_entry({'sha256':'a'*64},'a'*64,page,'更新')
