#!/usr/bin/env python3
"""编译层 - 多篇笔记合并成主题页"""
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

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

def get_note_content(filepath):
    """获取笔记内容（去除 frontmatter）"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return ""

    # 移除 frontmatter
    content = re.sub(r'^---\n.*?\n---\n?', '', content, flags=re.DOTALL)
    return content.strip()

def group_notes_by_tag(notes_dir):
    """按标签分组笔记"""
    if not os.path.exists(notes_dir):
        return {}

    tag_notes = defaultdict(list)

    for filename in os.listdir(notes_dir):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(notes_dir, filename)
        meta = parse_frontmatter(filepath)

        if not meta:
            continue

        title = meta.get('title', filename)
        tags = meta.get('tags', [])
        date = meta.get('date', '')
        content = get_note_content(filepath)

        for tag in tags:
            tag_notes[tag].append({
                'filename': filename,
                'title': title,
                'date': date,
                'tags': tags,
                'content': content
            })

    return tag_notes

def generate_topic_page(tag, notes):
    """生成主题页"""
    date = datetime.now().strftime('%Y-%m-%d')

    # 按日期排序
    notes.sort(key=lambda x: x['date'], reverse=True)

    lines = [
        f'# {tag}',
        '',
        f'> 生成时间: {date}',
        f'> 相关笔记: {len(notes)} 篇',
        '',
        '## 概述',
        '',
        f'本页汇总了所有与「{tag}」相关的笔记。',
        '',
        '## 相关笔记',
        '',
    ]

    # 列出所有相关笔记
    for note in notes:
        lines.append(f'### {note["title"]}')
        lines.append('')
        lines.append(f'- 文件: {note["filename"]}')
        lines.append(f'- 日期: {note["date"]}')
        if note['tags']:
            lines.append(f'- 标签: {", ".join(note["tags"])}')
        lines.append('')

        # 提取摘要
        content = note['content']
        summary_match = re.search(r'## 摘要\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1).strip()
            lines.append(f'> {summary[:200]}...' if len(summary) > 200 else f'> {summary}')
            lines.append('')

    # 提取共同要点
    lines.append('## 核心要点')
    lines.append('')

    # 从所有笔记中提取要点
    all_points = []
    for note in notes:
        content = note['content']
        points_match = re.search(r'## 要点\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if points_match:
            points_text = points_match.group(1).strip()
            points = [p.strip('- ').strip() for p in points_text.split('\n') if p.strip().startswith('-')]
            all_points.extend(points)

    # 去重并显示
    unique_points = list(set(all_points))[:10]
    if unique_points:
        for point in unique_points:
            lines.append(f'- {point}')
    else:
        lines.append('- 暂无要点')

    lines.append('')
    lines.append('## 待探索问题')
    lines.append('')
    lines.append('- （可手动添加待探索的问题）')

    return '\n'.join(lines)

def compile_topics(notes_dir='notes', wiki_dir='wiki', min_notes=2):
    """主函数：编译主题页"""
    print("\n正在分析笔记，生成主题页...\n")

    # 1. 按标签分组
    tag_notes = group_notes_by_tag(notes_dir)

    if not tag_notes:
        print("还没有任何笔记，请先添加笔记。")
        return []

    # 2. 筛选出有多个笔记的标签
    topics_to_compile = [
        (tag, notes) for tag, notes in tag_notes.items()
        if len(notes) >= min_notes
    ]

    if not topics_to_compile:
        print(f"没有找到包含 {min_notes} 篇以上笔记的主题。")
        print(f"当前标签数量: {len(tag_notes)}")
        return []

    # 3. 生成主题页
    os.makedirs(wiki_dir, exist_ok=True)
    generated = []

    for tag, notes in topics_to_compile:
        # 生成主题页内容
        content = generate_topic_page(tag, notes)

        # 保存文件
        safe_tag = re.sub(r'[<>:"/\\|?*]', '', tag)
        filename = f'{safe_tag}.md'
        filepath = os.path.join(wiki_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        generated.append({
            'tag': tag,
            'filename': filename,
            'notes_count': len(notes)
        })

        print(f"[PASS] 生成主题页: {filename} ({len(notes)} 篇笔记)")

    print(f"\n共生成 {len(generated)} 个主题页")
    print(f"保存位置: {os.path.abspath(wiki_dir)}")

    return generated

def main():
    """命令行入口"""
    notes_dir = os.path.join(os.path.dirname(__file__), '..', 'notes')
    wiki_dir = os.path.join(os.path.dirname(__file__), '..', 'wiki')
    compile_topics(notes_dir, wiki_dir)

if __name__ == '__main__':
    main()
