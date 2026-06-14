"""
DeepSeek 智能筛选引擎
利用 DeepSeek API 对采集到的文章进行语义级筛选，
只保留「AI 使用技巧、新工具、技术突破」相关内容。
"""

import json
import os
import time
from typing import Optional

import requests

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# 批量处理：一次 API 调用处理多条
BATCH_SIZE = 5


def is_relevant(article_title: str, article_summary: str, source_name: str, max_retries: int = 3) -> Optional[dict]:
    """
    使用 DeepSeek 判断内容相关度，返回结构化结果或 None（跳过）
    
    返回格式：
    {
        "relevant": True/False,
        "category": "技巧|新工具|技术突破|官方更新|开源项目|论文解读",
        "title_cn": "中文标题",
        "summary_cn": "120字以内中文摘要",
        "key_takeaway": "核心要点（一句话）",
    }
    """
    if not API_KEY:
        print("  ⚠️ 未设置 DEEPSEEK_API_KEY，跳过 DeepSeek 筛选")
        return None

    prompt = f"""你是顶级 AI 情报分析师。请分析以下内容，判断是否属于值得推送的「AI 情报」。
值得推送的类型：
- AI 使用技巧、提示词技巧、实用教程
- 新 AI 工具发布或重大更新
- 模型隐藏功能、高级用法
- 前沿技术突破、重要论文
- 官方重要公告

不值得推送的类型：
- 纯吐槽/情绪帖
- 无实质内容的新闻简讯
- 低质量营销
- 与 AI 无关的内容

标题：{article_title}
内容片段：{article_summary[:800]}
来源：{source_name}

请用 JSON 格式回复（不要用 markdown 包裹）：
{{"relevant": true或false, "category": "类型", "title_cn": "中文标题(如果是英文则翻译)", "summary_cn": "中文摘要不超过120字", "key_takeaway": "一句话核心要点", "score": 1-10}}
"""

    for attempt in range(max_retries):
        try:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "system", "content": "你是 AI 情报分析师。只输出 JSON，不要 markdown 代码块。"},
                             {"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 300,
            }

            resp = requests.post(DEEPSEEK_API, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()

            content = result["choices"][0]["message"]["content"].strip()

            # 清理可能的 markdown 代码块包裹
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            parsed = json.loads(content)

            if parsed.get("relevant") and parsed.get("score", 0) >= 5:
                return parsed
            return None

        except json.JSONDecodeError:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            print(f"  ⚠️ DeepSeek 返回非 JSON，跳过: {content[:100]}")
            return None
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait = (attempt + 1) * 2
                print(f"  ⏳ API 异常，{wait}s 后重试... ({e})")
                time.sleep(wait)
                continue
            print(f"  ❌ DeepSeek API 失败: {e}")
            return None
        except Exception as e:
            print(f"  ❌ 未知异常: {e}")
            return None

    return None


def filter_articles(articles: list, verbose: bool = True) -> list[dict]:
    """
    对采集到的文章列表进行智能筛选
    
    返回：筛选后的文章列表，每条包含原始信息 + DeepSeek 分析结果
    """
    if not API_KEY:
        print("⚠️ 无 DeepSeek API Key，使用关键词粗筛")
        from fetcher import keyword_prefilter
        results = []
        for article in articles:
            if keyword_prefilter(article):
                results.append({
                    "title": article.title,
                    "title_cn": article.title,
                    "url": article.url,
                    "summary": article.summary[:200],
                    "summary_cn": article.summary[:200],
                    "source_name": article.source_name,
                    "lang": article.lang,
                    "published_at": article.published_at,
                    "category": "未分类",
                    "key_takeaway": "",
                    "score": 3,
                })
        return results

    results = []
    total = len(articles)
    passed = 0
    
    for i, article in enumerate(articles):
        if verbose and i % 10 == 0:
            print(f"🔍 筛选进度: {i}/{total} ({passed} 通过)")

        analysis = is_relevant(article.title, article.summary or article.content_snippet, article.source_name)
        if analysis:
            passed += 1
            results.append({
                "title": article.title,
                "title_cn": analysis.get("title_cn", article.title),
                "url": article.url,
                "summary": article.summary[:300],
                "summary_cn": analysis.get("summary_cn", ""),
                "source_name": article.source_name,
                "lang": article.lang,
                "published_at": article.published_at,
                "category": analysis.get("category", "未分类"),
                "key_takeaway": analysis.get("key_takeaway", ""),
                "score": analysis.get("score", 5),
            })
        
        time.sleep(0.3)  # 控制 API 调用频率

    # 按分数降序排列
    results.sort(key=lambda x: x["score"], reverse=True)
    
    if verbose:
        print(f"✅ 筛选完成: {total} → {len(results)} 条 (通过率 {len(results)/max(total,1)*100:.1f}%)")

    return results


if __name__ == "__main__":
    # 快速测试
    test_title = "10 hidden ChatGPT features you didn't know about in 2026"
    test_summary = "Discover 10 powerful ChatGPT features that most users overlook, including memory management, custom instructions tricks, and advanced data analysis capabilities."
    result = is_relevant(test_title, test_summary, "r/ChatGPT")
    print(json.dumps(result, ensure_ascii=False, indent=2))
