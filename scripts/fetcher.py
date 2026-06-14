"""
RSS & 爬虫采集引擎
支持 RSS/Atom 解析 + 简单 HTML 抓取
"""

import time
import hashlib
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass, field

import feedparser
import requests
from bs4 import BeautifulSoup

# 北京时间
TZ_SHANGHAI = timezone(timedelta(hours=8))

HEADERS = {
    "User-Agent": "AI-Intelligence-Bot/2.0 (Contact: github.com/your-repo)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


@dataclass
class Article:
    title: str
    url: str
    summary: str
    source_name: str
    lang: str
    published_at: str  # ISO 8601
    content_snippet: str = ""
    source_category: str = ""

    @property
    def fingerprint(self) -> str:
        """唯一标识：URL 的 SHA256"""
        return hashlib.sha256(self.url.encode()).hexdigest()


class DedupCache:
    """SQLite 去重缓存"""

    def __init__(self, db_path: str = "data/cache.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS seen (
                fingerprint TEXT PRIMARY KEY,
                url TEXT,
                fetched_at TEXT,
                pushed INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def is_new(self, fingerprint: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM seen WHERE fingerprint = ?", (fingerprint,)
        ).fetchone()
        return row is None

    def mark_seen(self, article: Article):
        self.conn.execute(
            "INSERT OR IGNORE INTO seen (fingerprint, url, fetched_at) VALUES (?, ?, ?)",
            (article.fingerprint, article.url, datetime.now(TZ_SHANGHAI).isoformat()),
        )
        self.conn.commit()

    def mark_pushed(self, article: Article):
        self.conn.execute(
            "UPDATE seen SET pushed = 1 WHERE fingerprint = ?",
            (article.fingerprint,),
        )
        self.conn.commit()

    def stats(self) -> dict:
        total = self.conn.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
        pushed = self.conn.execute("SELECT COUNT(*) FROM seen WHERE pushed = 1").fetchone()[0]
        return {"total_seen": total, "total_pushed": pushed}

    def cleanup(self, keep_days: int = 30):
        cutoff = (datetime.now(TZ_SHANGHAI) - timedelta(days=keep_days)).isoformat()
        self.conn.execute("DELETE FROM seen WHERE fetched_at < ?", (cutoff,))
        self.conn.commit()


class RSSFetcher:
    """RSS / Atom 源抓取器"""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def fetch(self, source: dict) -> list[Article]:
        articles = []
        try:
            resp = requests.get(source["url"], headers=HEADERS, timeout=self.timeout)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)

            for entry in feed.entries[:30]:  # 每个源最多取30条
                title = entry.get("title", "").strip()
                url = entry.get("link", "").strip()
                summary = (entry.get("summary", "") or entry.get("description", "")).strip()

                if not title or not url:
                    continue

                # 清理 HTML 标签
                soup = BeautifulSoup(summary, "html.parser")
                clean_summary = soup.get_text(separator=" ", strip=True)[:500]

                published = entry.get("published", "") or entry.get("updated", "")
                try:
                    dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) if entry.get("published_parsed") else datetime.now(timezone.utc)
                    published_iso = dt.astimezone(TZ_SHANGHAI).isoformat()
                except Exception:
                    published_iso = datetime.now(TZ_SHANGHAI).isoformat()

                articles.append(Article(
                    title=title,
                    url=url,
                    summary=clean_summary,
                    source_name=source["name"],
                    lang=source.get("lang", "en"),
                    published_at=published_iso,
                    content_snippet=clean_summary,
                ))

        except requests.RequestException as e:
            print(f"  ⚠️ [{source['name']}] 抓取失败: {e}")
        except Exception as e:
            print(f"  ⚠️ [{source['name']}] 解析异常: {e}")

        return articles


class ScrapeFetcher:
    """通用网页爬虫（用于非 RSS 源）"""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def fetch(self, source: dict) -> list[Article]:
        articles = []
        try:
            resp = requests.get(source["url"], headers=HEADERS, timeout=self.timeout)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            now = datetime.now(TZ_SHANGHAI).isoformat()

            # GitHub Trending 特殊处理
            if "github.com/trending" in source["url"]:
                repos = soup.select("article.Box-row")[:20]
                for repo in repos:
                    h2 = repo.select_one("h2")
                    desc = repo.select_one("p")
                    if h2:
                        title = h2.get_text(strip=True).replace("\n", " ").replace("  ", " ")
                        url = "https://github.com" + (h2.select_one("a")["href"] if h2.select_one("a") else "")
                        desc_text = desc.get_text(strip=True) if desc else ""
                        articles.append(Article(
                            title=f"[GitHub Trending] {title}",
                            url=url,
                            summary=desc_text[:300],
                            source_name=source["name"],
                            lang="en",
                            published_at=now,
                            content_snippet=desc_text[:300],
                        ))
            else:
                # 通用抓取：提取页面中的链接和描述
                for link in soup.select("a[href]")[:50]:
                    url = link.get("href", "")
                    if not url.startswith("http"):
                        continue
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    articles.append(Article(
                        title=title[:200],
                        url=url,
                        summary=title[:300],
                        source_name=source["name"],
                        lang=source.get("lang", "en"),
                        published_at=now,
                        content_snippet=title[:300],
                    ))

        except requests.RequestException as e:
            print(f"  ⚠️ [{source['name']}] 抓取失败: {e}")
        except Exception as e:
            print(f"  ⚠️ [{source['name']}] 解析异常: {e}")

        return articles


def keyword_prefilter(article: Article) -> bool:
    """关键词粗筛：快速剔除明显不相关的内容"""
    from sources import KEYWORDS, ANTI_KEYWORDS
    
    text = f"{article.title} {article.summary}".lower()

    # 反关键词检查
    for kw in ANTI_KEYWORDS:
        if kw.lower() in text:
            return False

    # 正关键词检查
    for kw in KEYWORDS:
        if kw.lower() in text:
            return True

    return False  # 没有命中任何关键词的也不收


def fetch_all_sources(verbose: bool = True) -> list[Article]:
    """遍历所有源，采集文章"""
    from sources import SOURCES

    rss = RSSFetcher()
    scrape = ScrapeFetcher()
    all_articles = []

    for source in SOURCES:
        if verbose:
            print(f"📡 [{source['name']}] 正在抓取...")
        try:
            if source["type"] == "rss":
                articles = rss.fetch(source)
            elif source["type"] == "scrape":
                articles = scrape.fetch(source)
            else:
                continue
            if verbose:
                print(f"   ✅ 获取 {len(articles)} 条")
            all_articles.extend(articles)
        except Exception as e:
            if verbose:
                print(f"   ❌ 异常: {e}")
        time.sleep(0.5)  # 礼貌间隔

    return all_articles


if __name__ == "__main__":
    articles = fetch_all_sources()
    print(f"\n📊 共采集 {len(articles)} 条原始数据")
    for a in articles[:5]:
        print(f"  - [{a.source_name}] {a.title[:80]}")
