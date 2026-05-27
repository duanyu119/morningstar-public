import json
import tempfile
import unittest
from pathlib import Path

from scripts.fetch_newsletter_items import FeedConfig, mark_seen, parse_rss_items


class FetchNewsletterItemsTest(unittest.TestCase):
    def test_parse_rss_items_keeps_provenance(self):
        raw = b"""<?xml version="1.0"?>
        <rss version="2.0">
          <channel>
            <title>Example</title>
            <item>
              <title>Example Article</title>
              <link>https://example.com/article</link>
              <author>editor@example.com</author>
              <pubDate>Tue, 26 May 2026 10:00:00 GMT</pubDate>
              <description><![CDATA[<p>Hello <b>world</b>.</p>]]></description>
            </item>
          </channel>
        </rss>"""
        feed = FeedConfig("Example Feed", "https://example.com/feed", ["AI"])

        items = parse_rss_items(feed, raw, max_chars=1000)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["source"], "Example Feed")
        self.assertEqual(items[0]["source_url"], "https://example.com/feed")
        self.assertEqual(items[0]["source_themes"], ["AI"])
        self.assertEqual(items[0]["link"], "https://example.com/article")
        self.assertIn("Hello world", items[0]["description"])
        self.assertEqual(items[0]["extraction_method"], "feed_content")

    def test_mark_seen_appends_unique_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "packet.json"
            state_path = Path(tmp) / "state.json"
            packet_path.write_text(
                json.dumps(
                    {
                        "items": [
                            {"link": "https://example.com/a"},
                            {"link": "https://example.com/a"},
                            {"link": "https://example.com/b"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            mark_seen(packet_path, state_path)

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["seen_links"], ["https://example.com/a", "https://example.com/b"])
            self.assertIn("updated_at", state)


if __name__ == "__main__":
    unittest.main()
