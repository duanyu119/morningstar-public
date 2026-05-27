# MorningStar 启明星

> Version 0.1: an open-source RSS/news collection and aggregation starter kit.
> 版本 0.1：一个开源的 RSS / 新闻搜集与聚合项目起点。

## What It Is / 这是什么

MorningStar 启明星 is a small, local-first toolkit for collecting public RSS/newsletter feeds into structured JSON packets. It is designed for people who want a repeatable daily reading workflow before adding heavier AI scoring, databases, or dashboards.

MorningStar 启明星 是一个轻量、本地优先的新闻搜集工具，用来把公开 RSS / newsletter 信息源抓取成结构化 JSON 数据包。它适合先跑通稳定的每日阅读工作流，再逐步接入 AI 评分、数据库或仪表盘。

## Why I Built It / 我为什么做

I want a personal intelligence workflow that does three things well:

1. Collect from a known source list instead of doom-scrolling.
2. Preserve original links, source names, timestamps, and extracted text.
3. Produce clean packets that can later be reviewed by humans or AI agents.

我希望有一个个人信息工作流，先做好三件事：

1. 从明确的信息源列表抓取，而不是被推荐流牵着走。
2. 保留原文链接、来源、时间戳和可提取正文。
3. 产出干净的数据包，后续可以交给人或 AI agent 做筛选、摘要和复盘。

## Methodology / 方法论

MorningStar follows a simple pipeline:

1. **Source curation**: keep a small feed list with explicit themes.
2. **Freshness filter**: fetch only recent posts by default.
3. **State tracking**: remember seen links locally so the next run focuses on new items.
4. **Evidence preservation**: keep raw title, URL, author, publication time, description, and extracted article text.
5. **Downstream freedom**: output JSON first, so users can plug in their own ranking, summarization, storage, or publishing layer.

启明星遵循一个简单流程：

1. **信息源策展**：维护一份小而明确的 RSS 列表，并给每个源标注主题。
2. **新鲜度过滤**：默认只抓取近期内容。
3. **状态跟踪**：本地记录已读链接，让下一次运行聚焦新增内容。
4. **证据保留**：保留标题、URL、作者、发布时间、摘要和可提取正文。
5. **下游自由**：先输出 JSON，方便用户自行接入排序、摘要、存储或发布层。

## What Is Included In v0.1 / v0.1 包含什么

- Public RSS feed configuration in `config/feeds.json`.
- A standalone fetcher: `scripts/fetch_newsletter_items.py`.
- Local output under `data/packets/`.
- Local seen-link state under `data/state.json`.
- A minimal unit test for packet parsing and seen-link state.

- `config/feeds.json`：公开 RSS 信息源配置。
- `scripts/fetch_newsletter_items.py`：独立抓取脚本。
- `data/packets/`：本地输出目录。
- `data/state.json`：本地已见链接状态。
- 一个最小单元测试，覆盖 RSS 解析和已见链接状态。

## What Is Not Included / 不包含什么

This public version does not include private databases, Feishu/Lark tables, Cloudflare deployment state, API keys, personal review logs, or generated historical digests.

公开版不包含私有数据库、飞书/Lark 表格配置、Cloudflare 部署状态、API key、个人反馈日志或历史生成日报。

## Quick Start / 快速开始

```bash
git clone https://github.com/duanyu119/news-digest.git
cd news-digest
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/fetch_newsletter_items.py --recent-per-feed 2 --include-seen
```

The script prints the packet path, usually:

脚本会打印输出文件路径，通常是：

```text
data/packets/YYYY-MM-DD_newsletter_items.json
```

To avoid re-reading the same links after a successful review:

如果一次阅读完成后，希望后续不再重复抓取同一批链接：

```bash
python3 scripts/fetch_newsletter_items.py --mark-seen data/packets/YYYY-MM-DD_newsletter_items.json
```

## Configuration / 配置

Edit `config/feeds.json`:

编辑 `config/feeds.json`：

```json
{
  "timezone": "Asia/Shanghai",
  "lookback_days": 2,
  "max_items_per_feed": 5,
  "max_chars_per_item": 18000,
  "feeds": [
    {
      "name": "One Useful Thing",
      "url": "https://www.oneusefulthing.org/feed",
      "themes": ["AI", "work-practice"]
    }
  ]
}
```

Only use public feeds or feeds you have the right to access. Do not commit private RSS tokens.

只使用公开 RSS，或你有权访问的信息源。不要把私有 RSS token 提交到 Git。

## Privacy Boundary / 隐私边界

The repository intentionally ignores runtime data under `data/`, local environment files, deployment artifacts, and private integration configs.

本仓库默认忽略 `data/` 下的运行时数据、本地环境变量、部署产物和私有集成配置。

If you fork this project, check your Git history before making a repository public. Removing files from the latest commit does not remove them from old commits.

如果你 fork 或公开自己的版本，必须检查 Git 历史。只从最新提交删除文件，并不会清除旧提交里已经出现过的敏感内容。

## Development / 开发

```bash
python3 -m unittest
python3 scripts/fetch_newsletter_items.py --recent-per-feed 1 --include-seen --no-html
```

`--no-html` keeps the smoke test fast by using feed content only.

`--no-html` 会只使用 RSS 内正文，适合快速 smoke test。

## Roadmap / 路线图

- v0.1: public RSS collection and JSON packets.
- v0.2: pluggable scoring rules and source health checks.
- v0.3: optional local HTML digest renderer.
- v0.4: optional integrations for databases, LLM evaluators, and publishing.

- v0.1：公开 RSS 抓取与 JSON 数据包。
- v0.2：可插拔评分规则和信息源健康检查。
- v0.3：可选本地 HTML digest renderer。
- v0.4：可选数据库、LLM 评估和发布集成。

## License / 许可证

MIT. See `LICENSE`.

MIT 协议。见 `LICENSE`。
