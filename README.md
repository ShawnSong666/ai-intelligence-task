# 🤖 AI 全球情报雷达

> 30+ 权威 AI 信息源 | DeepSeek 智能筛选 | 7×24 自动推送

一个运行在 GitHub Actions 上的免费 AI 情报采集系统，自动从全球 30+ 信息源抓取最新 AI 动态，利用 DeepSeek 进行语义级筛选，只保留「使用技巧、新工具、技术突破」相关内容，并推送到你选择的终端。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🌍 **30+ 信息源** | Reddit、HN、官方博客、中文媒体、GitHub、arXiv |
| 🧠 **智能筛选** | DeepSeek API 语义分析，精准过滤噪音 |
| 🔄 **自动去重** | SQLite 缓存，绝不重复推送 |
| 📡 **多通道推送** | Telegram / 飞书 / 钉钉 / Email / Notion / JSON |
| ⏰ **定时执行** | GitHub Actions 每 6 小时自动触发 |
| 🆓 **完全免费** | GitHub Actions 免费额度 + DeepSeek 免费 API |
| 🌐 **中英双语** | 自动翻译英文内容为中文摘要 |

---

## 🚀 三步部署

### 1. Fork 本仓库

点击右上角 **Fork** → 创建你自己的副本。

### 2. 设置 Secrets

进入 Fork 后的仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**：

| Secret 名称 | 说明 | 是否必须 |
|-------------|------|----------|
| `DEEPSEEK_API_KEY` | [DeepSeek 开放平台](https://platform.deepseek.com) API Key | ✅ 必须 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（[@BotFather](https://t.me/BotFather) 创建） | 按需 |
| `TELEGRAM_CHAT_ID` | Telegram 接收人 Chat ID | 按需 |
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook URL | 按需 |
| `DINGTALK_WEBHOOK` | 钉钉机器人 Webhook URL | 按需 |
| `SENDGRID_API_KEY` | SendGrid API Key（邮件推送） | 按需 |
| `EMAIL_FROM` | 发件人邮箱 | 按需 |
| `EMAIL_TO` | 收件人邮箱 | 按需 |
| `NOTION_API_KEY` | Notion Integration Token | 按需 |
| `NOTION_DATABASE_ID` | Notion 数据库 ID | 按需 |

你也可以在 **Variables** 中设置默认推送模式：

| Variable | 默认值 | 可选值 |
|----------|--------|--------|
| `PUSH_MODE` | `json` | `telegram`, `feishu`, `dingtalk`, `email`, `notion`, `json`, `all` |

### 3. 启动！

进入 **Actions** 标签 → 选择 **AI 全球情报扫描** → **Run workflow** → 手动触发第一次。

几分钟后，你配置的终端就会收到第一批 AI 情报！

---

## 📂 项目结构

```
ai-intelligence-task/
├── .github/workflows/
│   └── ai-intelligence-scan.yml   # 定时触发器（每6小时）
├── scripts/
│   ├── main.py                     # 主调度脚本
│   ├── sources.py                  # 30+ 信息源配置
│   ├── fetcher.py                  # RSS/爬虫采集引擎
│   ├── filter.py                   # DeepSeek 智能筛选
│   ├── notify.py                   # 多通道推送
│   └── requirements.txt            # Python 依赖
├── data/
│   ├── cache.db                    # SQLite 去重缓存（自动生成）
│   └── intelligence_output.json    # 情报输出（自动生成）
├── .env.example                    # 环境变量模板
├── .gitignore
└── README.md
```

---

## 📡 信息源一览

### 社交 & 论坛（10 源）
| 源 | 类型 |
|----|------|
| r/OpenAI | Reddit RSS |
| r/deepseek | Reddit RSS |
| r/MachineLearning | Reddit RSS |
| r/singularity | Reddit RSS |
| r/LocalLLaMA | Reddit RSS |
| r/ChatGPT | Reddit RSS |
| r/PromptEngineering | Reddit RSS |
| r/ArtificialIntelligence | Reddit RSS |
| r/Anthropic | Reddit RSS |
| r/StableDiffusion | Reddit RSS |

### 科技媒体（4 源）
| 源 | 类型 |
|----|------|
| Hacker News (AI/LLM) | RSS |
| Hacker News (Prompt) | RSS |
| The Verge AI | RSS |
| TechCrunch AI | RSS |

### 官方博客（7 源）
| 源 | 类型 |
|----|------|
| OpenAI Blog | RSS |
| Google DeepMind | RSS |
| Anthropic Blog | RSS |
| Meta AI Blog | RSS |
| Mistral AI Blog | RSS |
| Hugging Face Blog | RSS |
| Stability AI Blog | RSS |

### 中文媒体（4 源）
| 源 | 类型 |
|----|------|
| 机器之心 | RSS |
| 量子位 | RSS |
| 少数派 AI | RSS |
| 知乎 AI 话题 | RSS |

### 工具发现（3 源）
| 源 | 类型 |
|----|------|
| Product Hunt AI | 爬虫 |
| There's an AI For That | 爬虫 |
| GitHub Trending | 爬虫 |

### 技术博客（6 源）
| 源 | 类型 |
|----|------|
| Towards Data Science | RSS |
| Machine Learning Mastery | RSS |
| The Gradient | RSS |
| Simon Willison's Blog | RSS |
| Lilian Weng's Blog | RSS |
| Andrej Karpathy's Blog | RSS |

### 学术（3 源）
| 源 | 类型 |
|----|------|
| arXiv cs.AI | RSS |
| arXiv cs.CL | RSS |
| Product Hunt AI | 爬虫 |

---

## 🧪 本地运行

```bash
# 1. 克隆仓库
git clone <your-repo-url>
cd ai-intelligence-task

# 2. 安装依赖
pip install -r scripts/requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 4. 运行
source .env  # Linux/Mac
# 或 Windows: set 命令逐行设置
python scripts/main.py

# 快速测试（只扫3个源）
python scripts/main.py --quick-test

# 干跑不推送
python scripts/main.py --dry-run

# 指定推送模式
python scripts/main.py --mode telegram
```

---

## 🔧 自定义

### 添加/删除信息源

编辑 `scripts/sources.py`，按格式添加：

```python
{"name": "你的源名称", "url": "RSS地址", "type": "rss", "lang": "zh"},
```

### 调整执行频率

编辑 `.github/workflows/ai-intelligence-scan.yml` 中的 cron：

```yaml
schedule:
  # 北京时间 8:00, 14:00, 20:00, 02:00
  - cron: "0 0,6,12,18 * * *"
```

### 调整筛选灵敏度

编辑 `scripts/filter.py`，修改 `score` 阈值（默认 >= 5）：

```python
if parsed.get("relevant") and parsed.get("score", 0) >= 5:
```

---

## ⚠️ 注意事项

1. **DeepSeek API 免费额度**：注册即送，足够日常使用。如果额度耗尽，筛选会降级为关键词模式
2. **GitHub Actions 限制**：免费仓库每月 2000 分钟，本任务每次约 5-10 分钟，每天 4 次完全够用
3. **Reddit RSS**：有时会限速，如果某源持续失败可以暂时注释掉
4. **隐私**：API Key 通过 GitHub Secrets 管理，不会暴露在代码中

---

## 📜 License

MIT — 随意 Fork、修改、使用。

---

> 🎯 **不卖课，只给干货。** 让机器替你刷遍全球 AI 前沿，你只负责吸收精华。
