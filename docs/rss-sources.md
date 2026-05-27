# RSS Sources / RSS 信息源

The default v0.1 feed list is intentionally small and public. It is a starter set, not a universal recommendation engine.

v0.1 默认信息源刻意保持小而公开。它是一个起步列表，不是通用推荐系统。

## Included Feeds / 已包含信息源

| Source | URL | Themes |
|---|---|---|
| One Useful Thing | `https://www.oneusefulthing.org/feed` | AI, work practice |
| Scaling Biotech | `https://scalingbiotech.substack.com/feed` | AI4Bio, biotech |
| Physiologically Speaking | `https://www.physiologicallyspeaking.com/feed` | Health, exercise science |
| ChinaTalk | `https://www.chinatalk.media/feed` | US-China, tech policy |
| Ahead of AI | `https://magazine.sebastianraschka.com/feed` | AI, ML, papers |
| Decoding Science | `https://decodingscience.substack.com/feed` | AI4S, scientific discovery |
| Citrini Research | `https://www.citriniresearch.com/feed` | VC, macro, semiconductors |

## Adding A Feed / 添加信息源

Add an object to `config/feeds.json`:

在 `config/feeds.json` 里新增一项：

```json
{
  "name": "Example",
  "url": "https://example.com/feed",
  "themes": ["AI", "science"]
}
```

Do not commit private tokenized feed URLs. If a feed URL contains a private token, keep it in a local ignored config.

不要提交带私有 token 的 RSS URL。如果某个 RSS URL 含私人 token，应放在本地 ignored 配置中。
