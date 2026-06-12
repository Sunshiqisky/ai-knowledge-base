#!/usr/bin/env python3
"""关联推荐脚本 - 基于标签重叠找关联笔记"""
import os
import re
import sys

def parse_frontmatter(filepath):
    """解析 Markdown frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # 解析标签列表
            if key == 'tags' and value.startswith('['):
                tags = [t.strip() for t in value.strip('[]').split(',')]
                frontmatter[key] = tags
            else:
                frontmatter[key] = value

    return frontmatter

def calculate_similarity(note1_meta, note2_meta):
    """计算两个笔记的相似度（基于标签重叠）"""
    tags1 = set(note1_meta.get('tags', []))
    tags2 = set(note2_meta.get('tags', []))

    if not tags1 or not tags2:
        return 0

    # 计算标签重叠数
    overlap = len(tags1 & tags2)
    return overlap

def find_related(notes_dir, target_note, top_n=3):
    """找出与目标笔记最相关的笔记"""
    target_path = os.path.join(notes_dir, target_note)
    if not os.path.exists(target_path):
        return []

    target_meta = parse_frontmatter(target_path)

    # 计算所有笔记与目标的相似度
    similarities = []
    for f in os.listdir(notes_dir):
        if not f.endswith('.md') or f == target_note:
            continue

        filepath = os.path.join(notes_dir, f)
        meta = parse_frontmatter(filepath)
        score = calculate_similarity(target_meta, meta)

        if score > 0:
            similarities.append((f, score))

    # 按相似度排序
    similarities.sort(key=lambda x: x[1], reverse=True)

    return [note for note, score in similarities[:top_n]]

def main():
    if len(sys.argv) < 2:
        print("用法: python find_related.py <笔记文件名>")
        print("示例: python find_related.py 2026-06-12-AI-Agent.md")
        return

    target = sys.argv[1]
    related = find_related('notes', target)

    if not related:
        print(f"没有找到与 {target} 相关的笔记。")
        return

    print(f"与 {target} 相关的笔记：")
    for r in related:
        print(f"  - {r}")

if __name__ == '__main__':
    main()
