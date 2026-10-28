import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from update_feed import generate_feed, inspect_apk, REPO_URL, certificate_fingerprints


class FeedTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        (self.path / 'yingyu-tv.apk').write_bytes(b'apk-fixture')
        self.feed = {'schemaVersion': 1, 'channels': {'android-mobile': {'build': 5001, 'sha256': 'b' * 64}}}
        self.release = {'tag_name': 'v1.1.10-tv', 'html_url': f'{REPO_URL}/releases/tag/v1.1.10-tv',
            'body': '修复播放错误', 'draft': False, 'prerelease': False, 'assets': [
                {'name': 'yingyu-tv.apk', 'size': 11,
                 'browser_download_url': f'{REPO_URL}/releases/download/v1.1.10-tv/yingyu-tv.apk'}]}
        self.entry = {'version': '1.1.10', 'build': 5012, 'packageName': 'com.kankan.kankan.tv', 'size': 11, 'sha256': 'a' * 64}

    def generate(self, feed=None):
        with patch('update_feed.inspect_apk', return_value=copy.deepcopy(self.entry)):
            return generate_feed(feed or self.feed, self.release, self.path, 'aapt', 'apksigner', {})

    def test_tv_release_preserves_mobile_and_pins_download(self):
        result = self.generate()
        self.assertEqual(result['channels']['android-mobile'], self.feed['channels']['android-mobile'])
        self.assertEqual(result['channels']['android-tv']['build'], 5012)
        self.assertEqual(result['channels']['android-tv']['downloadUrl'], self.release['assets'][0]['browser_download_url'])
        self.assertNotIn('android-tv', self.feed['channels'])

    def test_pre_release_and_draft_rejected(self):
        for flag in ['draft', 'prerelease']:
            with self.subTest(flag=flag):
                self.release[flag] = True
                with self.assertRaises(ValueError):
                    self.generate()
                self.release[flag] = False

    def test_same_apk_idempotent_but_replacing_same_build_rejected(self):
        result = self.generate()
        self.assertEqual(self.generate(result), result)
        result['channels']['android-tv']['sha256'] = 'c' * 64
        with self.assertRaisesRegex(ValueError, 'Increase versionCode'):
            self.generate(result)

    def test_downgrade_rejected(self):
        result = self.generate()
        result['channels']['android-tv']['build'] = 5013
        with self.assertRaisesRegex(ValueError, 'downgrade'):
            self.generate(result)

    def test_missing_apk_duplicate_and_wrong_download_url_rejected(self):
        original = copy.deepcopy(self.release)
        self.release['assets'] = []
        with self.assertRaisesRegex(ValueError, 'Upload at least'):
            self.generate()
        self.release = copy.deepcopy(original)
        self.release['assets'].append(copy.deepcopy(self.release['assets'][0]))
        with self.assertRaisesRegex(ValueError, 'one APK'):
            self.generate()
        self.release = original
        self.release['assets'][0]['browser_download_url'] = 'https://example.com/apk'
        with self.assertRaisesRegex(ValueError, 'pin the exact'):
            self.generate()

    def test_incorrect_download_size_rejected(self):
        self.release['assets'][0]['size'] = 12
        with self.assertRaisesRegex(ValueError, 'size differs'):
            self.generate()

    def test_wrong_signer_rejected_before_archive_parsing(self):
        metadata = "package: name='com.kankan.kankan.tv' versionCode='5012' versionName='1.1.10'"
        signature = 'Signer #1 certificate SHA-256 digest: ' + 'c' * 64
        with patch('update_feed.subprocess.check_output', side_effect=[metadata, signature]):
            with self.assertRaisesRegex(ValueError, 'signing certificate'):
                inspect_apk(self.path / 'yingyu-tv.apk', 'aapt', 'apksigner', {'com.kankan.kankan.tv': ['a' * 64]})

    def test_certificate_output_supports_new_sdk_range_annotations(self):
        for prefix in ['Signer #1', 'Signer (minSdkVersion=24, maxSdkVersion=2147483647) #1']:
            with self.subTest(prefix=prefix):
                self.assertEqual(certificate_fingerprints(prefix + ' certificate SHA-256 digest: ' + 'AB' * 32), {'ab' * 32})
        self.assertEqual(certificate_fingerprints('Source Stamp Signer certificate SHA-256 digest: ' + 'a' * 64), set())

    def test_unknown_package_rejected(self):
        with patch('update_feed.subprocess.check_output', return_value="package: name='other.app' versionCode='1' versionName='1.0'"):
            with self.assertRaisesRegex(ValueError, 'Unsupported package'):
                inspect_apk(self.path / 'yingyu-tv.apk', 'aapt', 'apksigner', {})


if __name__ == '__main__':
    unittest.main()
