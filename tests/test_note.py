from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from update_note import parse_feed, save_if_changed

def item(number, date='Tue, 20 Oct 2026 07:00:00 +0900', title='タイトル', image=None):
    image = image or '<media:thumbnail>https://assets.st-note.com/test.png?width=800&amp;fit=bounds</media:thumbnail>'
    return f'<item><title>{title}</title><link>https://note.com/sustella_jp/n/n{number}</link><pubDate>{date}</pubDate>{image}</item>'

def feed(items):
    return ('<rss xmlns:media="http://search.yahoo.com/mrss/"><channel><link>https://note.com/sustella_jp</link>'+items+'</channel></rss>').encode()

class NoteTests(unittest.TestCase):
    def test_latest_three_are_sorted_deduplicated_and_timezone_normalized(self):
        data = parse_feed(feed(item(1, 'Mon, 19 Oct 2026 07:00:00 +0900')+item(2)+item(3, 'Wed, 21 Oct 2026 07:00:00 +0900')+item(4, 'Thu, 22 Oct 2026 07:00:00 +0900')+item(4)))
        self.assertEqual([r['url'].rsplit('/', 1)[-1] for r in data['items']], ['n4','n3','n2'])
        self.assertEqual(data['items'][0]['publishedAt'], '2026-10-21T22:00:00Z')
    def test_note_text_thumbnail_and_xml_entities(self):
        row = parse_feed(feed(item(1, title='宿 &amp; 人')))['items'][0]
        self.assertEqual(row['title'], '宿 & 人')
        self.assertIn('&fit=bounds', row['thumbnail'])
    def test_attribute_thumbnail_and_invalid_image(self):
        self.assertEqual(parse_feed(feed(item(1,image='<media:thumbnail url="https://assets.st-note.com/a.jpg"/>')))['items'][0]['thumbnail'],'https://assets.st-note.com/a.jpg')
        self.assertIsNone(parse_feed(feed(item(1,image='<media:thumbnail>javascript:alert(1)</media:thumbnail>')))['items'][0]['thumbnail'])
    def test_empty_malformed_and_wrong_channel_fail(self):
        for data in [feed(''), b'not XML', feed(item(1)).replace(b'note.com/sustella_jp</link>', b'note.com/other</link>'), b'<!DOCTYPE rss><rss/>']:
            with self.assertRaises(Exception): parse_feed(data)
    def test_invalid_article_url_and_date_are_rejected(self):
        for xml in [feed(item(1)).replace(b'https://note.com/sustella_jp/n/n1',b'javascript:alert(1)'),feed(item(1,date='not a date'))]:
            with self.assertRaises(ValueError): parse_feed(xml)
    def test_unchanged_data_is_not_rewritten_and_failure_preserves_it(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'note.json';data=parse_feed(feed(item(1)))
            self.assertTrue(save_if_changed(data,dest));before=dest.read_bytes();mtime=dest.stat().st_mtime_ns
            self.assertFalse(save_if_changed(data,dest));self.assertEqual(dest.stat().st_mtime_ns,mtime)
            with self.assertRaises(ValueError): save_if_changed(parse_feed(feed('')),dest)
            self.assertEqual(dest.read_bytes(),before)

if __name__=='__main__': unittest.main()
