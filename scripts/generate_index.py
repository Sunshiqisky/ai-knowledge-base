#!/usr/bin/env python3
"""索引生成脚本 - 生成笔记目录"""
import os
import re
import sys
from datetime import datetime

def parse_frontmatter(filepath):
    """解析 Markdown frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    frontmatter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter

def generate_index(notes_dir='notes', output_path='INDEX.md'):
    """生成索引文件"""
    if not os.path.exists(notes_dir):
        print(f"目录 {notes_dir} 不存在")
        return

    # 收集所有笔记信息
    notes_info = []
    for f in sorted(os.listdir(notes_dir)):
        if not f.endswith('.md'):
            continue

        filepath = os.path.join(notes_dir, f)
        meta = parse_frontmatter(filepath)

        notes_info.append({
            'filename': f,
            'title': meta.get('title', f),
            'tags': meta.get('tags', '[]'),
            'date': meta.get('date', '未知')
        })

    # 生成索引内容
    lines = [
        '# 笔记索引',
        '',
        f'> 自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        '',
        f'共 {len(notes_info)} 条笔记',
        '',
        '## 按时间排序',
        '',
    ]

    for note in notes_info:
        lines.append(f"- [{note['title']}]({note['filename']}) - {note['date']}")

    lines.append('')
    lines.append('## 按标签分类')
    lines.append('')

    # 按标签分组
    tag_groups = {}
    for note in notes_info:
        tags_str = note['tags']
        if tags_str.startswith('['):
            tags = [t.strip() for t in tags_str.strip('[]').split(',')]
        else:
            tags = [tags_str]

        for tag in tags:
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(note)

    for tag in sorted(tag_groups.keys()):
        lines.append(f'### {tag}')
        lines.append('')
        for note in tag_groups[tag]:
            lines.append(f"- [{note['title']}]({note['filename']})")
        lines.append('')

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"索引已生成: {output_path}")
    print(f"共收录 {len(notes_info)} 条笔记")

def main():
    notes_dir = sys.argv[1] if len(sys.argv) > 1 else 'notes'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'INDEX.md'
    generate_index(notes_dir, output_path)

if __name__ == '__main__':
    main()
