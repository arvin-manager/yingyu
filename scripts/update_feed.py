#!/usr/bin/env python3
"""Inspect public Release APKs and atomically update a static, token-free feed."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

CHANNELS = {'com.kankan.kankan': 'android-mobile', 'com.kankan.kankan.tv': 'android-tv'}
REPO_URL = 'https://github.com/arvin-manager/yingyu'


def inspect_apk(path, aapt, apksigner, trusted):
    output = subprocess.check_output([aapt, 'dump', 'badging', str(path)], text=True)
    match = re.search(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", output, re.M)
    if not match:
        raise ValueError(f'Cannot read APK identity: {path.name}')
    package, build, version = match.groups()
    if package not in CHANNELS or not 0 < int(build) <= 2147483647:
        raise ValueError(f'Unsupported package or versionCode: {package}/{build}')
    certificates = subprocess.check_output([apksigner, 'verify', '--print-certs', str(path)], text=True)
    signers = set(re.findall(r'Signer #\d+ certificate SHA-256 digest: ([a-fA-F0-9]{64})', certificates))
    expected = set(trusted.get(package, []))
    if not signers or signers != expected:
        raise ValueError(f'APK signing certificate does not match installed versions: {package}')
    with ZipFile(path) as apk:
        names = set(apk.namelist())
        for abi in ['armeabi-v7a', 'arm64-v8a', 'x86_64']:
            for library in ['libapp.so', 'libflutter.so']:
                if f'lib/{abi}/{library}' not in names:
                    raise ValueError(f'Use a universal Flutter release APK, missing {abi}/{library}')
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'version': version, 'build': int(build), 'packageName': package,
            'size': path.stat().st_size, 'sha256': digest}


def generate_feed(feed, release, directory, aapt, apksigner, trusted):
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('Only published, non-prerelease versions may update the stable feed')
    tag = release.get('tag_name', '')
    if not re.fullmatch(r'v[0-9][A-Za-z0-9._-]{0,99}', tag):
        raise ValueError('Use a version tag such as v1.1.10-tv')
    page = f'{REPO_URL}/releases/tag/{tag}'
    if release.get('html_url') != page:
        raise ValueError('Unexpected release repository or URL')
    if feed.get('schemaVersion') != 1 or not isinstance(feed.get('channels'), dict):
        raise ValueError('Unsupported feed format')
    # Work on a copy: a later failed APK must never leave a partially changed feed.
    result = json.loads(json.dumps(feed))
    seen = set()
    for asset in release.get('assets', []):
        name = asset.get('name', '')
        if not name.lower().endswith('.apk'):
            continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*\.apk', name):
            raise ValueError('Unsupported asset filename')
        expected_url = f'{REPO_URL}/releases/download/{tag}/{name}'
        if asset.get('browser_download_url') != expected_url:
            raise ValueError('APK URL must pin the exact release asset')
        path = directory / name
        if path.stat().st_size != asset.get('size'):
            raise ValueError('Downloaded APK size differs from release asset')
        entry = inspect_apk(path, aapt, apksigner, trusted)
        channel = CHANNELS[entry['packageName']]
        if channel in seen:
            raise ValueError(f'Upload only one APK for each channel: {channel}')
        seen.add(channel)
        previous = result['channels'].get(channel)
        if previous:
            if entry['build'] < previous['build']:
                raise ValueError(f'Cannot downgrade {channel}')
            if entry['build'] == previous['build']:
                if entry['sha256'] != previous.get('sha256'):
                    raise ValueError(f'Increase versionCode before replacing {channel}')
                continue  # Idempotent: keep the original version-pinned download URL.
        entry.update(notes=release.get('body') or '', downloadUrl=expected_url, pageUrl=page)
        result['channels'][channel] = entry
    if not seen:
        raise ValueError('Upload at least one universal Android APK before publishing the release')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--aapt', required=True)
    parser.add_argument('--apksigner', required=True)
    parser.add_argument('--feed', type=Path, default=Path('updates.json'))
    parser.add_argument('--certificates', type=Path, default=Path('signing-certificates.json'))
    args = parser.parse_args()
    result = generate_feed(json.loads(args.feed.read_text()), json.loads(args.release.read_text()),
        args.assets, args.aapt, args.apksigner, json.loads(args.certificates.read_text()))
    target = args.feed.with_suffix('.json.tmp')
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    target.replace(args.feed)
    print('Validated update channels: ' + ', '.join(sorted(result['channels'])))


if __name__ == '__main__':
    main()
