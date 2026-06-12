#!/usr/bin/env python3
"""往回织机制 - 新资料自动更新相关主题"""
import os
import re
import sys
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

    content = re.sub(r'^---\n.*?\n---\n?', '', content, flags=re.DOTALL)
    return content.strip()

def find_related_topic_pages(note_tags, wiki_dir):
    """查找相关的主题页"""
    if not os.path.exists(wiki_dir):
        return []

    related_pages = []

    for filename in os.listdir(wiki_dir):
        if not filename.endswith('.md'):
            continue

        # 从文件名提取主题
        topic = filename.replace('.md', '')

        # 检查是否匹配
        if topic in note_tags:
            filepath = os.path.join(wiki_dir, filename)
            related_pages.append({
                'topic': topic,
                'filename': filename,
                'filepath': filepath
            })

    return related_pages

def update_topic_page(page_info, new_note_info, wiki_dir):
    """更新主题页，添加新笔记"""
    filepath = page_info['filepath']

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return False

    # 检查是否已经包含这个笔记
    if new_note_info['filename'] in content:
        return False

    # 找到「相关笔记」部分，在末尾添加
    insert_marker = '## 核心要点'
    if insert_marker in content:
        # 在「核心要点」之前插入
        new_entry = f"""### {new_note_info['title']}

- 文件: {new_note_info['filename']}
- 日期: {new_note_info['date']}
- 标签: {', '.join(new_note_info['tags'])}

> {new_note_info.get('summary', '待补充摘要')}

"""
        content = content.replace(insert_marker, new_entry + insert_marker)

        # 更新笔记数量
        count_match = re.search(r'相关笔记: (\d+) 篇', content)
        if count_match:
            old_count = int(count_match.group(1))
            new_count = old_count + 1
            content = content.replace(
                f'相关笔记: {old_count} 篇',
                f'相关笔记: {new_count} 篇'
            )

        # 写回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return True

    return False

def check_contradictions(new_note_info, existing_notes):
    """检查新笔记与现有笔记的矛盾"""
    contradictions = []

    # 简单的矛盾检测：查找相反的关键词
    new_content = new_note_info.get('content', '').lower()

    contradiction_pairs = [
        ('推荐', '不推荐'),
        ('优点', '缺点'),
        ('优势', '劣势'),
        ('应该', '不应该'),
        ('可以', '不可以'),
        ('好', '坏'),
    ]

    for note in existing_notes:
        note_content = note.get('content', '').lower()

        for pos, neg in contradiction_pairs:
            if pos in new_content and neg in note_content:
                contradictions.append({
                    'new_note': new_note_info['title'],
                    'existing_note': note['title'],
                    'topic': pos + '/' + neg
                })
            elif neg in new_content and pos in note_content:
                contradictions.append({
                    'new_note': new_note_info['title'],
                    'existing_note': note['title'],
                    'topic': pos + '/' + neg
                })

    return contradictions

def weave_back(new_note_path, notes_dir='notes', wiki_dir='wiki'):
    """主函数：往回织"""
    print(f"\n正在处理新笔记: {os.path.basename(new_note_path)}\n")

    # 1. 解析新笔记
    new_meta = parse_frontmatter(new_note_path)
    if not new_meta:
        print("无法解析笔记")
        return False

    new_note_info = {
        'filename': os.path.basename(new_note_path),
        'title': new_meta.get('title', ''),
        'tags': new_meta.get('tags', []),
        'date': new_meta.get('date', ''),
        'content': get_note_content(new_note_path)
    }

    # 提取摘要
    content = new_note_info['content']
    summary_match = re.search(r'## 摘要\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if summary_match:
        new_note_info['summary'] = summary_match.group(1).strip()[:200]

    print(f"标题: {new_note_info['title']}")
    print(f"标签: {', '.join(new_note_info['tags'])}")

    # 2. 查找相关主题页
    related_pages = find_related_topic_pages(new_note_info['tags'], wiki_dir)

    if not related_pages:
        print("\n没有找到相关的主题页。")
        print("提示: 先运行「编译层」生成主题页。")
        return False

    print(f"\n找到 {len(related_pages)} 个相关主题页：")

    # 3. 更新主题页
    updated_count = 0
    for page in related_pages:
        print(f"  - {page['topic']}", end="")

        # 获取现有笔记
        try:
            with open(page['filepath'], 'r', encoding='utf-8') as f:
                page_content = f.read()
        except:
            print(" [跳过]")
            continue

        # 更新主题页
        if update_topic_page(page, new_note_info, wiki_dir):
            print(" [已更新]")
            updated_count += 1
        else:
            print(" [已存在]")

    # 4. 检查矛盾（可选）
    print(f"\n更新完成: {updated_count} 个主题页已更新")

    if updated_count > 0:
        print("\n提示: 请检查更新后的主题页，确认内容准确性。")

    return updated_count > 0

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python weave_back.py <笔记文件路径>")
        print("示例: python weave_back.py notes/2026-06-12-新笔记.md")
        return

    note_path = sys.argv[1]

    if not os.path.exists(note_path):
        print(f"文件不存在: {note_path}")
        return

    notes_dir = os.path.join(os.path.dirname(__file__), '..', 'notes')
    wiki_dir = os.path.join(os.path.dirname(__file__), '..', 'wiki')

    weave_back(note_path, notes_dir, wiki_dir)

if __name__ == '__main__':
    main()
