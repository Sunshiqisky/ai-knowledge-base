#!/usr/bin/env python3
"""选题推荐 - 基于笔记主题推荐可写选题"""
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

def analyze_notes(notes_dir):
    """分析所有笔记，提取主题和关键词"""
    if not os.path.exists(notes_dir):
        return None

    notes_info = []
    tag_count = Counter()
    tag_notes = defaultdict(list)

    for filename in os.listdir(notes_dir):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(notes_dir, filename)
        meta = parse_frontmatter(filepath)
        content = get_note_content(filepath)

        if not meta:
            continue

        title = meta.get('title', filename)
        tags = meta.get('tags', [])
        date = meta.get('date', '')

        notes_info.append({
            'filename': filename,
            'title': title,
            'tags': tags,
            'date': date,
            'content': content
        })

        # 统计标签
        for tag in tags:
            tag_count[tag] += 1
            tag_notes[tag].append({
                'filename': filename,
                'title': title
            })

    return {
        'notes': notes_info,
        'tag_count': tag_count,
        'tag_notes': tag_notes
    }

def suggest_topics_from_tags(analysis):
    """基于标签推荐选题"""
    suggestions = []
    tag_count = analysis['tag_count']
    tag_notes = analysis['tag_notes']

    # 找出高频标签（出现 2 次以上）
    hot_tags = [tag for tag, count in tag_count.items() if count >= 2]

    for tag in hot_tags:
        related_notes = tag_notes[tag]
        note_titles = [n['title'] for n in related_notes[:3]]

        suggestions.append({
            'type': '主题综合',
            'topic': f'{tag} 主题综合文章',
            'reason': f'有 {len(related_notes)} 篇相关笔记',
            'related_notes': note_titles,
            'priority': len(related_notes)
        })

    return suggestions

def suggest_topics_from_gaps(analysis):
    """基于内容缺口推荐选题"""
    suggestions = []
    notes = analysis['notes']

    # 找出只有摘要没有要点的笔记
    for note in notes:
        content = note['content']
        if '待补充要点' in content or '要点' not in content:
            suggestions.append({
                'type': '补充完善',
                'topic': f'完善笔记: {note["title"]}',
                'reason': '笔记内容不完整，需要补充要点',
                'related_notes': [note['title']],
                'priority': 1
            })

    return suggestions

def suggest_topics_from_combinations(analysis):
    """基于标签组合推荐选题"""
    suggestions = []
    tag_notes = analysis['tag_notes']
    notes = analysis['notes']

    # 找出可以组合的主题
    all_tags = list(analysis['tag_count'].keys())

    # 两两组合
    for i in range(len(all_tags)):
        for j in range(i + 1, len(all_tags)):
            tag1 = all_tags[i]
            tag2 = all_tags[j]

            # 找同时包含两个标签的笔记
            notes_with_both = []
            for note in notes:
                if tag1 in note['tags'] and tag2 in note['tags']:
                    notes_with_both.append(note)

            if len(notes_with_both) >= 1:
                suggestions.append({
                    'type': '交叉主题',
                    'topic': f'{tag1} + {tag2} 交叉主题',
                    'reason': f'有 {len(notes_with_both)} 篇笔记涉及这两个主题',
                    'related_notes': [n['title'] for n in notes_with_both[:2]],
                    'priority': len(notes_with_both)
                })

    return suggestions

def generate_topic_report(analysis, suggestions):
    """生成选题报告"""
    date = datetime.now().strftime('%Y-%m-%d')

    lines = [
        '# 选题推荐报告',
        '',
        f'> 生成时间: {date}',
        f'> 基于 {len(analysis["notes"])} 篇笔记分析',
        '',
        '## 热门主题',
        '',
    ]

    # 热门标签
    tag_count = analysis['tag_count']
    if tag_count:
        for tag, count in tag_count.most_common(5):
            lines.append(f'- **{tag}**: {count} 篇相关笔记')
    else:
        lines.append('- 暂无标签数据')

    lines.append('')
    lines.append('## 选题建议')
    lines.append('')

    # 按优先级排序
    suggestions.sort(key=lambda x: x['priority'], reverse=True)

    if suggestions:
        for i, suggestion in enumerate(suggestions[:10], 1):
            lines.append(f'### {i}. {suggestion["topic"]}')
            lines.append('')
            lines.append(f'- **类型**: {suggestion["type"]}')
            lines.append(f'- **理由**: {suggestion["reason"]}')
            if suggestion['related_notes']:
                lines.append(f'- **相关笔记**: {", ".join(suggestion["related_notes"][:3])}')
            lines.append('')
    else:
        lines.append('暂无选题建议，请先添加更多笔记。')
        lines.append('')

    # 行动建议
    lines.append('## 行动建议')
    lines.append('')

    if not suggestions:
        lines.append('1. 先添加一些笔记到知识库')
        lines.append('2. 使用「从链接导入」功能快速积累素材')
        lines.append('3. 为笔记添加标签，方便后续分析')
    else:
        lines.append('1. 从优先级最高的选题开始')
        lines.append('2. 综合相关笔记的观点，形成自己的见解')
        lines.append('3. 写完后记得更新笔记和索引')

    return '\n'.join(lines)

def suggest_topics(notes_dir='notes', output_path=None):
    """主函数：生成选题推荐"""
    # 1. 分析笔记
    analysis = analyze_notes(notes_dir)

    if not analysis or not analysis['notes']:
        print("还没有任何笔记，请先添加笔记。")
        return None

    print(f"\n正在分析 {len(analysis['notes'])} 篇笔记...\n")

    # 2. 生成选题建议
    suggestions = []
    suggestions.extend(suggest_topics_from_tags(analysis))
    suggestions.extend(suggest_topics_from_gaps(analysis))
    suggestions.extend(suggest_topics_from_combinations(analysis))

    # 去重
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s['topic'] not in seen:
            seen.add(s['topic'])
            unique_suggestions.append(s)

    # 3. 生成报告
    report = generate_topic_report(analysis, unique_suggestions)

    # 4. 输出
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"[PASS] 选题报告已生成: {output_path}")
    else:
        print(report)

    return unique_suggestions

def main():
    """命令行入口"""
    notes_dir = os.path.join(os.path.dirname(__file__), '..', 'notes')
    output_path = os.path.join(os.path.dirname(__file__), '..', 'briefs', f'{datetime.now().strftime("%Y-%m-%d")}-选题推荐.md')

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    suggest_topics(notes_dir, output_path)

if __name__ == '__main__':
    main()
