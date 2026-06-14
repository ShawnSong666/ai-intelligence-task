"""聚焦快扫 — 只扫已验证可通的源，快速出结果"""
import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetcher import RSSFetcher, Article, keyword_prefilter
from filter import filter_articles

# 已验证从中国大陆可通的源
WORKING_SOURCES = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss", "lang": "en"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/feed/basic/", "type": "rss", "lang": "en"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "rss", "lang": "en"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss", "lang": "en"},
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed", "type": "rss", "lang": "en"},
    {"name": "Machine Learning Mastery", "url": "https://machinelearningmastery.com/feed/", "type": "rss", "lang": "en"},
    {"name": "The Gradient", "url": "https://thegradient.pub/feed/", "type": "rss", "lang": "en"},
    {"name": "Simon Willison", "url": "https://simonwillison.net/atom/entries/", "type": "rss", "lang": "en"},
    {"name": "量子位", "url": "https://www.qbitai.com/rss", "type": "rss", "lang": "zh"},
    {"name": "HN (AI/LLM)", "url": "https://hnrss.org/frontpage?q=AI+OR+LLM+OR+OpenAI+OR+DeepSeek", "type": "rss", "lang": "en"},
]

print("=" * 60)
print("🔍 聚焦快扫：11 个已验证可通源")
print("=" * 60)

rss = RSSFetcher(timeout=15)
all_articles = []

for src in WORKING_SOURCES:
    print(f"📡 [{src['name']}] ...", end=" ", flush=True)
    try:
        articles = rss.fetch(src)
        print(f"✅ {len(articles)} 条")
        all_articles.extend(articles)
    except Exception as e:
        print(f"❌ {e}")
    time.sleep(0.3)

print(f"\n📥 共采集 {len(all_articles)} 条")

# 关键词粗筛
keyword_filtered = [a for a in all_articles if keyword_prefilter(a)]
print(f"🔎 关键词粗筛: {len(keyword_filtered)} / {len(all_articles)}")

if not keyword_filtered:
    print("📭 无相关内容")
    sys.exit(0)

# DeepSeek 精筛
print(f"\n🧠 DeepSeek 语义精筛中...")
print("-" * 60)
filtered = filter_articles(keyword_filtered[:50], verbose=True)  # 最多筛50条

print(f"\n{'='*60}")
print(f"🏆 DeepSeek 精选结果 ({len(filtered)} 条)")
print(f"{'='*60}")

for i, item in enumerate(filtered, 1):
    print(f"\n{'─'*50}")
    print(f"#{i} [{item.get('category','?')}] ⭐{item.get('score','?')}/10")
    print(f"   原文: {item['title'][:80]}")
    print(f"   中文: {item.get('title_cn','')[:80]}")
    print(f"   摘要: {item.get('summary_cn','')[:150]}")
    print(f"   金句: {item.get('key_takeaway','')[:100]}")
    print(f"   来源: {item['source_name']}")
    print(f"   链接: {item['url'][:100]}")

# 保存结果
os.makedirs("data", exist_ok=True)
with open("data/intelligence_output.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)
print(f"\n💾 结果已保存: data/intelligence_output.json")
print("✅ 完成！")
