#!/usr/bin/env python3
"""Publish a verified public-page APK for parser-capable clients only."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from update_feed import inspect_apk, CHANNELS


def pgyer_entry(metadata, downloaded_digest, page, notes):
    url = urlsplit(page)
    if url.scheme != 'https' or url.netloc != 'www.pgyer.com' or url.query or url.fragment or not re.fullmatch(r'/app/build/[a-f0-9]{32}', url.path):
        raise ValueError('Use a version-pinned Pgyer public build page')
    if metadata['sha256'] != downloaded_digest:
        raise ValueError('Downloaded Pgyer APK differs from the signed local APK')
    return {**metadata, 'downloadUrl': page, 'pageUrl': page, 'notes': notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path, required=True)
    parser.add_argument('--downloaded-apk', type=Path, required=True)
    parser.add_argument('--page', required=True)
    parser.add_argument('--notes-file', type=Path, required=True)
    parser.add_argument('--aapt', required=True)
    parser.add_argument('--apksigner', required=True)
    args = parser.parse_args()
    metadata = inspect_apk(args.apk, args.aapt, args.apksigner, json.loads(Path('signing-certificates.json').read_text()))
    with args.downloaded_apk.open('rb') as stream:
        downloaded_digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    entry = pgyer_entry(metadata, downloaded_digest, args.page, args.notes_file.read_text())
    target = Path('updates.json')
    feed = json.loads(target.read_text())
    channel = CHANNELS[metadata['packageName']]
    current = feed.get('pgyerChannels', {}).get(channel)
    if current and (current['build'] > entry['build'] or (current['build'] == entry['build'] and current['sha256'] != entry['sha256'])):
        raise ValueError('Cannot downgrade or replace an existing versionCode')
    # Older installed clients still read channels; do not hand HTML to them.
    feed.setdefault('pgyerChannels', {})[channel] = entry
    target.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + '\n')
    print('Published Pgyer-capable channel:', channel, entry['version'], entry['build'])


if __name__ == '__main__':
    main()
