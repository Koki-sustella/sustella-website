"""Refresh note RSS without dependencies; never replace good data with an empty feed."""
import argparse
import json
import os
from pathlib import Path
import tempfile
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from email.utils import parsedate_to_datetime
from datetime import timezone
import xml.etree.ElementTree as ET

FEED = 'https://note.com/sustella_jp/rss'
SOURCE = 'https://note.com/sustella_jp'
DESTINATION = Path(__file__).resolve().parents[1] / 'site/data/note.json'
MAX_BYTES = 2_000_000

def thumbnail_url(value):
    value = (value or '').strip()
    parsed = urlparse(value)
    return value if parsed.scheme == 'https' and parsed.hostname == 'assets.st-note.com' and not parsed.username else None

def parse_feed(xml, limit=3):
    if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():
        raise ValueError('Unsupported XML declaration')
    root = ET.fromstring(xml)
    channel = root.find('channel')
    if channel is None or (channel.findtext('link') or '').rstrip('/') != SOURCE:
        raise ValueError('Unexpected RSS channel')
    result, seen = [], set()
    for item in channel.findall('item'):
        title = ' '.join((item.findtext('title') or '').split())
        url = (item.findtext('link') or '').strip()
        parsed = urlparse(url)
        if not title or parsed.scheme != 'https' or parsed.hostname != 'note.com' or parsed.username or not parsed.path.startswith('/sustella_jp/n/'):
            continue
        if url in seen:
            continue
        try:
            published = parsedate_to_datetime(item.findtext('pubDate') or '')
            if published.tzinfo is None:
                continue
            published = published.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        except (TypeError, ValueError, OverflowError):
            continue
        thumb = item.find('{http://search.yahoo.com/mrss/}thumbnail')
        image = thumbnail_url((thumb.get('url') or thumb.text) if thumb is not None else None)
        if not image:
            content = item.find('{http://search.yahoo.com/mrss/}content')
            image = thumbnail_url(content.get('url') if content is not None else None)
        result.append({'title': title, 'url': url, 'publishedAt': published, 'thumbnail': image})
        seen.add(url)
    if not result:
        raise ValueError('RSS has no valid articles; retaining previous JSON')
    result.sort(key=lambda row: row['publishedAt'], reverse=True)
    return {'source': SOURCE, 'items': result[:limit]}

def save_if_changed(data, destination):
    content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if destination.exists() and destination.read_text(encoding='utf-8') == content:
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=destination.parent, delete=False)
    try:
        with handle:
            handle.write(content)
        os.replace(handle.name, destination)
    finally:
        if os.path.exists(handle.name):
            os.unlink(handle.name)
    return True

def download():
    for attempt in range(3):
        try:
            request = Request(FEED, headers={'User-Agent': 'SUSTELLA-website-note-feed/1.0', 'Accept': 'application/rss+xml, application/xml'})
            with urlopen(request, timeout=25) as response:
                content = response.read(MAX_BYTES + 1)
            if len(content) > MAX_BYTES:
                raise ValueError('RSS exceeds size limit')
            return content
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, help='Optional local RSS fixture for verification')
    parser.add_argument('--output', type=Path, default=DESTINATION)
    args = parser.parse_args()
    content = args.input.read_bytes() if args.input else download()
    if len(content) > MAX_BYTES:
        raise ValueError('RSS exceeds size limit')
    data = parse_feed(content)
    changed = save_if_changed(data, args.output)
    print(f'Updated {len(data["items"])} note articles.' if changed else 'No article changes.')

if __name__ == '__main__':
    main()
