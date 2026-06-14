"""
AI 情报源矩阵 —— 覆盖全球 30+ 权威信息源
最后更新: 2026-06
"""

SOURCES = [
    # ===== Reddit — 技巧/小道消息最密集 =====
    {"name": "r/OpenAI", "url": "https://www.reddit.com/r/OpenAI/.rss", "type": "rss", "lang": "en"},
    {"name": "r/deepseek", "url": "https://www.reddit.com/r/deepseek/.rss", "type": "rss", "lang": "en"},
    {"name": "r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/.rss", "type": "rss", "lang": "en"},
    {"name": "r/singularity", "url": "https://www.reddit.com/r/singularity/.rss", "type": "rss", "lang": "en"},
    {"name": "r/LocalLLaMA", "url": "https://www.reddit.com/r/LocalLLaMA/.rss", "type": "rss", "lang": "en"},
    {"name": "r/ChatGPT", "url": "https://www.reddit.com/r/ChatGPT/.rss", "type": "rss", "lang": "en"},
    {"name": "r/PromptEngineering", "url": "https://www.reddit.com/r/PromptEngineering/.rss", "type": "rss", "lang": "en"},
    {"name": "r/ArtificialIntelligence", "url": "https://www.reddit.com/r/artificial/.rss", "type": "rss", "lang": "en"},
    {"name": "r/Anthropic", "url": "https://www.reddit.com/r/Anthropic/.rss", "type": "rss", "lang": "en"},
    {"name": "r/StableDiffusion", "url": "https://www.reddit.com/r/StableDiffusion/.rss", "type": "rss", "lang": "en"},

    # ===== Hacker News — AI 顶会论文、新工具首发 =====
    {"name": "HN (AI/LLM)", "url": "https://hnrss.org/frontpage?q=AI+OR+LLM+OR+OpenAI+OR+DeepSeek+OR+GPT+OR+Claude", "type": "rss", "lang": "en"},
    {"name": "HN (Prompt)", "url": "https://hnrss.org/frontpage?q=prompt+engineering+OR+fine-tuning+OR+RAG", "type": "rss", "lang": "en"},

    # ===== 官方博客 =====
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss", "lang": "en"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/feed/basic/", "type": "rss", "lang": "en"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/blog/rss.xml", "type": "rss", "lang": "en"},
    {"name": "Meta AI Blog", "url": "https://ai.meta.com/blog/feed/", "type": "rss", "lang": "en"},
    {"name": "Mistral AI Blog", "url": "https://mistral.ai/news/rss.xml", "type": "rss", "lang": "en"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "type": "rss", "lang": "en"},
    {"name": "Stability AI Blog", "url": "https://stability.ai/blog/rss", "type": "rss", "lang": "en"},

    # ===== 中文源 =====
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "type": "rss", "lang": "zh"},
    {"name": "量子位", "url": "https://www.qbitai.com/rss", "type": "rss", "lang": "zh"},
    {"name": "少数派 AI", "url": "https://sspai.com/tag/AI/feed", "type": "rss", "lang": "zh"},
    {"name": "知乎 AI 话题", "url": "https://www.zhihu.com/rss/topic/19551275", "type": "rss", "lang": "zh"},

    # ===== Product Hunt / 工具发现 =====
    {"name": "Product Hunt AI", "url": "https://www.producthunt.com/feed?category=ai", "type": "scrape", "lang": "en", "selector": "div.styles_item__"},
    
    # ===== GitHub Trending =====
    {"name": "GitHub Trending AI", "url": "https://github.com/trending?since=weekly&spoken_language_code=en", "type": "scrape", "lang": "en"},

    # ===== 更多技术博客 =====
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed", "type": "rss", "lang": "en"},
    {"name": "Machine Learning Mastery", "url": "https://machinelearningmastery.com/feed/", "type": "rss", "lang": "en"},
    {"name": "The Gradient", "url": "https://thegradient.pub/feed/", "type": "rss", "lang": "en"},
    {"name": "Simon Willison's Blog", "url": "https://simonwillison.net/atom/entries/", "type": "rss", "lang": "en"},
    {"name": "Lilian Weng's Blog", "url": "https://lilianweng.github.io/feed.xml", "type": "rss", "lang": "en"},
    {"name": "Andrej Karpathy's Blog", "url": "https://karpathy.ai/feed.xml", "type": "rss", "lang": "en"},

    # ===== 学术/产经 =====
    {"name": "ArXiv CS.AI", "url": "https://rss.arxiv.org/rss/cs.AI", "type": "rss", "lang": "en"},
    {"name": "ArXiv cs.CL", "url": "https://rss.arxiv.org/rss/cs.CL", "type": "rss", "lang": "en"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "rss", "lang": "en"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss", "lang": "en"},

    # ===== 专用 AI 工具导航 =====
    {"name": "There's an AI For That", "url": "https://theresanaiforthat.com/", "type": "scrape", "lang": "en"},
]


# 分类标记，便于后续按类别筛选
CATEGORIES = {
    "social_forum": ["r/OpenAI", "r/deepseek", "r/MachineLearning", "r/singularity", "r/LocalLLaMA",
                      "r/ChatGPT", "r/PromptEngineering", "r/ArtificialIntelligence", "r/Anthropic",
                      "r/StableDiffusion"],
    "tech_news": ["HN (AI/LLM)", "HN (Prompt)", "The Verge AI", "TechCrunch AI"],
    "official_blog": ["OpenAI Blog", "Google DeepMind", "Anthropic Blog", "Meta AI Blog",
                      "Mistral AI Blog", "Hugging Face Blog", "Stability AI Blog"],
    "chinese_sources": ["机器之心", "量子位", "少数派 AI", "知乎 AI 话题"],
    "tool_discovery": ["Product Hunt AI", "There's an AI For That", "GitHub Trending AI"],
    "tech_blogs": ["Towards Data Science", "Machine Learning Mastery", "The Gradient",
                   "Simon Willison's Blog", "Lilian Weng's Blog", "Andrej Karpathy's Blog"],
    "academic": ["ArXiv CS.AI", "ArXiv cs.CL"],
}

# 关键字过滤（辅助：在 DeepSeek 筛选之前先做粗筛，降低 API 调用量）
KEYWORDS = [
    "prompt", "技巧", "tutorial", "how to", "guide", "tips", "tricks",
    "release", "launch", "new tool", "新工具", "updated", "突破",
    "hidden feature", "隐藏功能", "secret", "workflow", "效率",
    "benchmark", "最佳实践", "best practice", "deepseek", "DeepSeek",
    "GPT", "Claude", "Gemini", "LLaMA", "Mixtral", "Qwen",
    "fine-tuning", "微调", "RAG", "agent", "智能体",
    "open source", "开源", "免费", "free",
    "multimodal", "多模态", "reasoning", "推理",
]

# 反关键词（标题中包含这些词的直接跳过）
ANTI_KEYWORDS = [
    "eli5", "rant", "complaint", "吐槽", "骂",
    "shitpost", "meme", "funny", "搞笑",
]
