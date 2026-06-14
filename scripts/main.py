#!/usr/bin/env python3
"""
🤖 AI Intelligence Task — 主调度脚本
全球 30+ 权威AI信息源 → 采集 → DeepSeek筛选 → 多通道推送

用法:
    python main.py                    # 完整流程
    python main.py --dry-run          # 只采集不推送
    python main.py --mode telegram     # 覆盖 PUSH_MODE
"""

import sys
import os
import json
import time
import argparse
from datetime import datetime, timezone, timedelta

# 确保 scripts 目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sources import SOURCES, CATEGORIES
from fetcher import fetch_all_sources, keyword_prefilter, DedupCache, Article
from filter import filter_articles, is_relevant
from notify import dispatch

TZ_SHANGHAI = timezone(timedelta(hours=8))


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║     🤖 AI 全球情报雷达 v2.0                  ║
║  30+ 信息源 | DeepSeek 智能筛选 | 多通道推送  ║
╚══════════════════════════════════════════════╝
    """)


def print_stats(cache: DedupCache, total_fetched: int, after_keyword: int, final_count: int):
    stats = cache.stats()
    print(f"""
┌──────────────────────────────────────────────┐
│ 📊 运行统计                                  │
├──────────────────────────────────────────────┤
│  信息源数量    : {len(SOURCES):>4}                         │
│  原始采集      : {total_fetched:>4} 条                      │
│  关键词粗筛    : {after_keyword:>4} 条                      │
│  DeepSeek精选  : {final_count:>4} 条                      │
│  历史累计      : {stats['total_seen']:>4} 条                      │
│  历史推送      : {stats['total_pushed']:>4} 条                      │
└──────────────────────────────────────────────┘
    """)


def run_pipeline(dry_run: bool = False, verbose: bool = True, override_mode: str = None):
    """
    完整情报流水线
    
    1. 遍历所有信息源采集原始数据
    2. 去重（SQLite）
    3. 关键词粗筛
    4. DeepSeek 语义精筛
    5. 格式化 + 多通道推送
    """
    start_time = time.time()
    print_banner()

    # 全局模式覆盖
    if override_mode:
        os.environ["PUSH_MODE"] = override_mode

    # ===== 1. 采集 =====
    print("📡 阶段 1/4: 采集全球信息源...")
    raw_articles = fetch_all_sources(verbose=verbose)
    total_fetched = len(raw_articles)
    print(f"\n📥 共采集 {total_fetched} 条原始数据")

    if not raw_articles:
        print("❌ 未采集到任何数据，请检查网络或信息源配置")
        return

    # ===== 2. 去重 =====
    print(f"\n🔍 阶段 2/4: 去重检查...")
    cache = DedupCache()
    new_articles = []
    for article in raw_articles:
        if cache.is_new(article.fingerprint):
            new_articles.append(article)
            cache.mark_seen(article)

    print(f"   新文章: {len(new_articles)} / {total_fetched} (去重 {total_fetched - len(new_articles)} 条)")

    if not new_articles:
        print("📭 无新文章，跳过后续阶段")
        cache.cleanup()
        return

    # ===== 3. 关键词粗筛 =====
    print(f"\n🔎 阶段 3/4: 关键词粗筛...")
    keyword_filtered = [a for a in new_articles if keyword_prefilter(a)]
    print(f"   通过: {len(keyword_filtered)} / {len(new_articles)}")

    if not keyword_filtered:
        print("📭 关键词粗筛后无剩余")
        return

    # ===== 4. DeepSeek 精筛 =====
    print(f"\n🧠 阶段 4/4: DeepSeek 语义精筛...")
    filtered = filter_articles(keyword_filtered, verbose=verbose)
    final_count = len(filtered)

    # 打印 Top 5
    if filtered:
        print(f"\n🏆 精选 Top 5:")
        for i, item in enumerate(filtered[:5], 1):
            print(f"  {i}. [{item.get('category','未分类')}] {item['title_cn'][:60]}")
            print(f"     {item.get('summary_cn','')[:80]}...")
            print(f"     📍 {item['source_name']} | ⭐ {item.get('score','?')}/10")

    # ===== 统计 =====
    print_stats(cache, total_fetched, len(keyword_filtered), final_count)

    # ===== 推送 =====
    if not dry_run:
        print("📤 开始推送...")
        dispatch(filtered, verbose=verbose)

        # 标记已推送
        for item in filtered:
            # 找对应的 Article 对象
            for article in new_articles:
                if article.url == item["url"]:
                    cache.mark_pushed(article)
                    break

    # ===== 清理 =====
    cache.cleanup()

    elapsed = time.time() - start_time
    print(f"\n⏱️ 总耗时: {elapsed:.1f}s")
    print("✅ 情报扫描完成！")

    return filtered


def run_quick_test():
    """快速测试：只抓取少量源，验证流程"""
    print("🧪 快速测试模式")
    print("=" * 40)

    from fetcher import RSSFetcher
    rss = RSSFetcher()

    # 只测 3 个源
    test_sources = [
        {"name": "r/OpenAI", "url": "https://www.reddit.com/r/OpenAI/.rss", "type": "rss", "lang": "en"},
        {"name": "HN (AI/LLM)", "url": "https://hnrss.org/frontpage?q=AI+OR+LLM+OR+OpenAI+OR+DeepSeek", "type": "rss", "lang": "en"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "type": "rss", "lang": "zh"},
    ]

    all_arts = []
    for src in test_sources:
        print(f"📡 [{src['name']}] 抓取中...")
        arts = rss.fetch(src)
        print(f"   ✅ {len(arts)} 条")
        all_arts.extend(arts)
        time.sleep(1)

    print(f"\n共 {len(all_arts)} 条")

    # 测试 DeepSeek 筛选
    if os.environ.get("DEEPSEEK_API_KEY"):
        print("\n🧠 测试 DeepSeek 筛选...")
        if all_arts:
            test_article = all_arts[0]
            result = is_relevant(test_article.title, test_article.summary, test_article.source_name)
            if result:
                print(f"   ✅ 相关！分类: {result.get('category')}")
                print(f"   摘要: {result.get('summary_cn', '')[:120]}")
            else:
                print(f"   ⏭️ 不相关，已跳过")
    else:
        print("\n⚠️ 无 DeepSeek API Key，跳过筛选测试")

    print("\n✅ 快速测试完成")


def main():
    parser = argparse.ArgumentParser(description="AI Intelligence Task — 全球 AI 情报雷达")
    parser.add_argument("--dry-run", action="store_true", help="只采集筛选，不推送")
    parser.add_argument("--mode", type=str, default=None,
                        choices=["telegram", "feishu", "dingtalk", "email", "notion", "json", "all"],
                        help="覆盖推送模式")
    parser.add_argument("--quick-test", action="store_true", help="快速测试模式")
    parser.add_argument("--quiet", action="store_true", help="减少输出")
    args = parser.parse_args()

    if args.quick_test:
        run_quick_test()
    else:
        run_pipeline(
            dry_run=args.dry_run,
            verbose=not args.quiet,
            override_mode=args.mode,
        )


if __name__ == "__main__":
    main()
