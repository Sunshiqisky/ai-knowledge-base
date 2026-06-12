#!/usr/bin/env python3
"""周报生成 - 每周梳理入库内容"""
import os
import re
import sys
from datetime import datetime, timedelta
from collections import Counter, defaultdict

def parse_frontmatter(filepath):
    """解析 Markdown frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return {}

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if key == 'tags' and value.startswith('['):
                tags = [t.strip() for t in value.strip('[]').split(',')]
                frontmatter[key] = tags
            else:
                frontmatter[key] = value

    return frontmatter

def get_notes_this_week(notes_dir):
    """获取本周添加的笔记"""
    if not os.path.exists(notes_dir):
        return []

    # 获取本周的日期范围
    today = datetime.now()
    # 本周一是几天前
    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    week_notes = []

    for filename in os.listdir(notes_dir):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(notes_dir, filename)

        # 从文件名提取日期
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            try:
                note_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                if note_date >= monday:
                    meta = parse_frontmatter(filepath)
                    if meta:
                        week_notes.append({
                            'filename': filename,
                            'title': meta.get('title', filename),
                            'tags': meta.get('tags', []),
                            'date': date_match.group(1),
                            'url': meta.get('url', '')
                        })
            except:
                pass

    # 按日期排序
    week_notes.sort(key=lambda x: x['date'], reverse=True)
    return week_notes

def analyze_week_notes(week_notes):
    """分析本周笔记"""
    if not week_notes:
        return {
            'count': 0,
            'tags': [],
            'hot_tags': [],
            'sources': []
        }

    # 统计标签
    tag_count = Counter()
    for note in week_notes:
        for tag in note['tags']:
            tag_count[tag] += 1

    # 统计来源
    sources = []
    for note in week_notes:
        if note['url']:
            domain = re.search(r'https?://([^/]+)', note['url'])
            if domain:
                sources.append(domain.group(1))

    source_count = Counter(sources)

    return {
        'count': len(week_notes),
        'tags': list(tag_count.keys()),
        'hot_tags': tag_count.most_common(5),
        'sources': source_count.most_common(3)
    }

def generate_report(week_notes, analysis):
    """生成周报"""
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    lines = [
        f'# 知识库周报',
        '',
        f'> {week_start.strftime("%Y-%m-%d")} ~ {week_end.strftime("%Y-%m-%d")}',
        f'> 生成时间: {today.strftime("%Y-%m-%d %H:%M")}',
        '',
        '## 本周概览',
        '',
        f'- 新增笔记: **{analysis["count"]}** 篇',
        f'- 涉及主题: **{len(analysis["tags"])}** 个',
        '',
    ]

    # 热门主题
    if analysis['hot_tags']:
        lines.append('## 热门主题')
        lines.append('')
        for tag, count in analysis['hot_tags']:
            lines.append(f'- **{tag}**: {count} 篇')
        lines.append('')

    # 来源统计
    if analysis['sources']:
        lines.append('## 内容来源')
        lines.append('')
        for source, count in analysis['sources']:
            lines.append(f'- {source}: {count} 篇')
        lines.append('')

    # 笔记列表
    if week_notes:
        lines.append('## 本周笔记')
        lines.append('')
        for note in week_notes:
            tags_str = ', '.join(note['tags']) if note['tags'] else '无标签'
            lines.append(f'- **{note["title"]}**')
            lines.append(f'  - 日期: {note["date"]}')
            lines.append(f'  - 标签: {tags_str}')
            if note['url']:
                lines.append(f'  - 来源: {note["url"]}')
            lines.append('')
    else:
        lines.append('## 本周笔记')
        lines.append('')
        lines.append('本周暂无新增笔记。')
        lines.append('')

    # 行动建议
    lines.append('## 下周建议')
    lines.append('')

    if analysis['count'] == 0:
        lines.append('1. 本周没有新增笔记，下周要加油！')
        lines.append('2. 使用「从链接导入」快速积累素材')
        lines.append('3. 每天花 10 分钟阅读并记录')
    elif analysis['count'] < 5:
        lines.append('1. 本周笔记较少，可以增加阅读量')
        lines.append('2. 尝试使用「选题推荐」找到写作方向')
        lines.append('3. 整理本周笔记，补充要点和摘要')
    else:
        lines.append('1. 本周产出不错，继续保持！')
        lines.append('2. 可以尝试写一篇综合文章')
        lines.append('3. 使用「选题推荐」找到下一个写作主题')

    return '\n'.join(lines)

def generate_weekly_report(notes_dir='notes', output_dir='briefs'):
    """主函数：生成周报"""
    print("\n正在生成周报...\n")

    # 1. 获取本周笔记
    week_notes = get_notes_this_week(notes_dir)

    # 2. 分析笔记
    analysis = analyze_week_notes(week_notes)

    # 3. 生成报告
    report = generate_report(week_notes, analysis)

    # 4. 保存报告
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    filename = f'{week_start.strftime("%Y-%m-%d")}-周报.md'
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"[PASS] 周报已生成: {output_path}")
    print(f"\n本周新增: {analysis['count']} 篇笔记")

    if analysis['hot_tags']:
        print(f"热门主题: {', '.join([t[0] for t in analysis['hot_tags'][:3]])}")

    return output_path

def main():
    """命令行入口"""
    notes_dir = os.path.join(os.path.dirname(__file__), '..', 'notes')
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'briefs')
    generate_weekly_report(notes_dir, output_dir)

if __name__ == '__main__':
    main()
