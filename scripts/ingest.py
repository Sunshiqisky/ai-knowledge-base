#!/usr/bin/env python3
"""Ingest 自动化 - 从链接自动生成笔记"""
import os
import re
import sys
import json
import requests
from datetime import datetime
from urllib.parse import urlparse

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.json')

def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def fetch_webpage(url):
    """抓取网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 简单提取正文（去除 HTML 标签）
        content = response.text

        # 提取标题
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else urlparse(url).netloc

        # 提取正文（简单去除 HTML 标签）
        # 移除 script 和 style
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # 移除 HTML 标签
        content = re.sub(r'<[^>]+>', ' ', content)

        # 清理空白字符
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()

        # 限制长度
        if len(content) > 5000:
            content = content[:5000] + '...'

        return {
            'success': True,
            'title': title,
            'content': content,
            'url': url
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_note_with_ai(title, content, url):
    """使用 AI 生成笔记（调用 Claude API）"""
    config = load_config()
    api_key = config.get('claude_api_key')

    if not api_key:
        # 没有 API key，使用简单模式
        return generate_note_simple(title, content, url)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""请帮我整理这篇文章，生成一篇笔记。

标题：{title}
链接：{url}
内容：
{content[:3000]}

请按以下格式输出：

摘要：（2-3 句话概括）

要点：
- 要点一
- 要点二
- 要点三

标签：（3-5 个标签，用逗号分隔）"""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        ai_response = message.content[0].text

        # 解析 AI 响应
        summary = ""
        points = []
        tags = []

        lines = ai_response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('摘要') or line.startswith('Summary'):
                current_section = 'summary'
                summary = line.split('：')[-1].split(':')[-1].strip()
            elif line.startswith('要点') or line.startswith('Points'):
                current_section = 'points'
            elif line.startswith('标签') or line.startswith('Tags'):
                current_section = 'tags'
                tags_str = line.split('：')[-1].split(':')[-1].strip()
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]
            elif current_section == 'summary' and not summary:
                summary = line
            elif current_section == 'points' and line.startswith('-'):
                points.append(line[1:].strip())

        # 如果解析失败，使用默认值
        if not summary:
            summary = f"这是一篇关于 {title} 的文章。"
        if not points:
            points = ["待补充要点"]
        if not tags:
            tags = ["待分类"]

        return {
            'success': True,
            'summary': summary,
            'points': points,
            'tags': tags,
            'ai_generated': True
        }

    except Exception as e:
        print(f"AI 生成失败: {e}")
        return generate_note_simple(title, content, url)

def generate_note_simple(title, content, url):
    """简单模式生成笔记（无 AI）"""
    # 简单提取前几句话作为摘要
    sentences = content.split('。')
    summary = '。'.join(sentences[:2]) + '。' if len(sentences) > 2 else content[:200]

    # 根据内容猜测标签
    tags = []
    tag_keywords = {
        'AI': ['ai', '人工智能', '机器学习', '深度学习', 'llm', '大模型'],
        'Python': ['python', 'pip', 'django', 'flask'],
        'Agent': ['agent', '智能体', '代理'],
        '编程': ['代码', '编程', '开发', '程序'],
        '工具': ['工具', '软件', '应用', '平台'],
    }

    content_lower = content.lower()
    for tag, keywords in tag_keywords.items():
        for keyword in keywords:
            if keyword in content_lower:
                tags.append(tag)
                break

    if not tags:
        tags = ["未分类"]

    return {
        'success': True,
        'summary': summary[:200] + '...' if len(summary) > 200 else summary,
        'points': ["待补充要点"],
        'tags': tags[:5],
        'ai_generated': False
    }

def save_note(title, url, summary, points, tags, notes_dir='notes'):
    """保存笔记到文件"""
    # 生成日期
    date = datetime.now().strftime('%Y-%m-%d')

    # 生成安全的文件名（去除特殊字符和 HTML 实体）
    safe_title = re.sub(r'&[^;]+;', '', title)  # 移除 HTML 实体
    safe_title = re.sub(r'[<>:"/\\|?*&]', '', safe_title)  # 移除特殊字符
    safe_title = re.sub(r'\s+', '-', safe_title)  # 空格转横线
    safe_title = safe_title[:50]  # 限制长度
    safe_title = safe_title.strip('-')
    filename = f"{date}-{safe_title}.md"
    filepath = os.path.join(notes_dir, filename)

    # 生成笔记内容
    content = f"""---
title: {title}
url: {url}
tags: [{', '.join(tags)}]
date: {date}
---

## 摘要
{summary}

## 要点
"""
    for point in points:
        content += f"- {point}\n"

    # 确保目录存在
    os.makedirs(notes_dir, exist_ok=True)

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath

def ingest_url(url, notes_dir='notes'):
    """主函数：从 URL 生成笔记"""
    print(f"\n正在处理: {url}\n")

    # 1. 抓取网页
    print("1. 抓取网页内容...")
    result = fetch_webpage(url)

    if not result['success']:
        print(f"抓取失败: {result['error']}")
        return None

    print(f"   标题: {result['title']}")

    # 2. 生成笔记
    print("2. 生成笔记...")
    note_data = generate_note_with_ai(
        result['title'],
        result['content'],
        url
    )

    if not note_data['success']:
        print("生成笔记失败")
        return None

    mode = "AI 生成" if note_data.get('ai_generated') else "简单模式"
    print(f"   模式: {mode}")
    print(f"   标签: {', '.join(note_data['tags'])}")

    # 3. 保存笔记
    print("3. 保存笔记...")
    filepath = save_note(
        result['title'],
        url,
        note_data['summary'],
        note_data['points'],
        note_data['tags'],
        notes_dir
    )

    print(f"\n[PASS] 笔记已保存: {filepath}")
    return filepath

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python ingest.py <URL>")
        print("示例: python ingest.py https://example.com/article")
        return

    url = sys.argv[1]

    # 验证 URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    notes_dir = os.path.join(os.path.dirname(__file__), '..', 'notes')
    ingest_url(url, notes_dir)

if __name__ == '__main__':
    main()
