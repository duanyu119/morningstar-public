# MorningStar Methodology / 启明星方法论

MorningStar starts from a narrow belief: good information systems should collect evidence before they optimize judgment.

启明星的起点很窄：好的信息系统应该先稳定收集证据，再谈优化判断。

## Principles / 原则

1. **Curate sources deliberately.** A small list of high-signal feeds beats a large undifferentiated stream.
2. **Keep provenance.** Every item should preserve its source, URL, timestamp, and extraction method.
3. **Separate collection from evaluation.** Fetching should not decide importance. Scoring, summarization, and publishing can be separate layers.
4. **Prefer reviewable packets.** JSON packets are easy to inspect, diff, archive, and feed into later tools.
5. **Avoid private-data coupling.** Public code should run without personal databases, browser cookies, or workspace-specific paths.

1. **有意识地策展信息源。** 小而高信号的信息源列表，通常胜过无差别的大流量输入。
2. **保留来源链。** 每条内容都应该保留来源、URL、时间戳和提取方式。
3. **采集和评价分离。** 抓取层不负责判断重要性；评分、摘要、发布可以是后续独立层。
4. **优先生成可复核数据包。** JSON 便于检查、diff、归档，也方便后续交给其他工具。
5. **避免和私有数据耦合。** 公开代码不应依赖个人数据库、浏览器 cookie 或特定本机路径。

## v0.1 Packet Shape / v0.1 数据包结构

Each run writes one packet under `data/packets/`:

每次运行会在 `data/packets/` 下写入一个数据包：

```json
{
  "generated_at": "2026-05-26T00:00:00+00:00",
  "display_date": "2026-05-26",
  "timezone": "Asia/Shanghai",
  "item_count": 1,
  "items": [
    {
      "source": "Example Feed",
      "source_url": "https://example.com/feed",
      "source_themes": ["AI"],
      "title": "Example article",
      "link": "https://example.com/article",
      "author": "Author",
      "published_at": "2026-05-26T00:00:00+00:00",
      "description": "Short feed description",
      "content_text": "Extracted text",
      "content_chars": 14,
      "content_truncated": false,
      "extraction_method": "feed_content"
    }
  ],
  "errors": []
}
```

Downstream tools should treat this packet as input evidence, not as a final digest.

后续工具应把这个数据包当作输入证据，而不是最终日报。
