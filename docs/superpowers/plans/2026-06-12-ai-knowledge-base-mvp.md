# AI 知识库 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个最小可用的本地 AI 知识库，支持链接抓取、自动整理、智能搜索

**Architecture:** 
- 语义活（理解、判断、打标签）交给 AI，写入 CLAUDE.md 规则
- 机械活（搜索、索引、关联）写成 Python 脚本
- 纯 Markdown 文件存储，零数据库

**Tech Stack:** Python 3, Claude API, Markdown

---

## 文件结构

```
my-knowledge-base/
├── CLAUDE.md                 # AI 工作流规则
├── ARCHITECTURE.md           # 架构文档
├── notes/                    # 笔记存储目录
├── scripts/
│   ├── search.py            # 搜索脚本
│   ├── find_related.py      # 关联推荐脚本
│   └── generate_index.py    # 索引生成脚本
└── tests/
    ├── test_search.py       # 搜索测试
    ├── test_find_related.py # 关联测试
    └── test_generate_index.py # 索引测试
```

---

## Task 1: 项目初始化

**Files:**
- Create: `setup_project.py`

- [ ] **Step 1: 创建项目初始化脚本**

```python
#!/usr/bin/env python3
"""项目初始化脚本 - 创建目录结构"""
import os

def setup():
    """创建项目目录结构"""
    dirs = ['notes', 'raw', 'wiki', 'briefs', 'scripts', 'tests']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}/")
    
    # 创建 __init__.py 让 tests 成为包
    with open('tests/__init__.py', 'w') as f:
        pass
    
    print("\n项目初始化完成！")

if __name__ == '__main__':
    setup()
```

- [ ] **Step 2: 运行初始化脚本**

Run: `python setup_project.py`
Expected:
```
Created directory: notes/
Created directory: raw/
Created directory: wiki/
Created directory: briefs/
Created directory: scripts/
Created directory: tests/

项目初始化完成！
```

- [ ] **Step 3: Commit**

```bash
git add setup_project.py
git commit -m "feat: add project setup script"
```

---

## Task 2: 搜索功能（最小版本）

**Files:**
- Create: `scripts/search.py`
- Create: `tests/test_search.py`

- [ ] **Step 1: 写失败的测试**

```python
#!/usr/bin/env python3
"""搜索功能测试"""
import os
import sys
import tempfile
import shutil

# 添加 scripts 目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def test_list_all_notes():
    """测试列出所有笔记"""
    from search import list_notes
    
    # 创建临时目录和测试文件
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试笔记
        test_notes = [
            '2026-06-12-AI-Agent入门.md',
            '2026-06-11-Python基础.md',
            '2026-06-10-机器学习.md'
        ]
        for note in test_notes:
            with open(os.path.join(tmpdir, note), 'w') as f:
                f.write(f"---\ntitle: {note}\n---\n\n内容")
        
        # 测试列出功能
        result = list_notes(tmpdir)
        assert len(result) == 3, f"期望 3 条笔记，实际 {len(result)}"
        print("✓ test_list_all_notes 通过")

def test_search_by_keyword():
    """测试按关键词搜索"""
    from search import search_notes
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试笔记
        notes_content = {
            '2026-06-12-AI-Agent入门.md': '---\ntitle: AI Agent入门\ntags: [AI, Agent]\n---\n\n这是关于AI Agent的文章',
            '2026-06-11-Python基础.md': '---\ntitle: Python基础\ntags: [Python]\n---\n\n这是关于Python的文章',
        }
        for name, content in notes_content.items():
            with open(os.path.join(tmpdir, name), 'w') as f:
                f.write(content)
        
        # 测试搜索
        result = search_notes(tmpdir, 'AI')
        assert len(result) == 1, f"期望 1 条结果，实际 {len(result)}"
        assert 'AI-Agent' in result[0], f"结果应包含 AI-Agent"
        print("✓ test_search_by_keyword 通过")

if __name__ == '__main__':
    test_list_all_notes()
    test_search_by_keyword()
    print("\n所有测试通过！")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python tests/test_search.py`
Expected: ImportError (因为 search.py 还不存在)

- [ ] **Step 3: 写最小实现**

```python
#!/usr/bin/env python3
"""搜索脚本 - 列出和搜索笔记"""
import os
import re
import sys

def list_notes(notes_dir='notes'):
    """列出所有笔记文件"""
    if not os.path.exists(notes_dir):
        return []
    
    notes = []
    for f in os.listdir(notes_dir):
        if f.endswith('.md'):
            notes.append(f)
    return sorted(notes)

def search_notes(notes_dir='notes', keyword=None):
    """搜索笔记（按关键词）"""
    if not keyword:
        return list_notes(notes_dir)
    
    results = []
    for f in os.listdir(notes_dir):
        if not f.endswith('.md'):
            continue
        
        filepath = os.path.join(notes_dir, f)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # 搜索标题、标签、摘要
        if keyword.lower() in content.lower():
            results.append(f)
    
    return sorted(results)

def main():
    if len(sys.argv) < 2:
        # 列出所有笔记
        notes = list_notes()
        if not notes:
            print("还没有任何笔记。")
            return
        print(f"共有 {len(notes)} 条笔记：")
        for note in notes:
            print(f"  - {note}")
    else:
        # 搜索
        keyword = sys.argv[1]
        results = search_notes(keyword=keyword)
        if not results:
            print(f"没有找到包含 '{keyword}' 的笔记。")
            return
        print(f"找到 {len(results)} 条：")
        for r in results:
            print(f"  - {r}")

if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python tests/test_search.py`
Expected:
```
✓ test_list_all_notes 通过
✓ test_search_by_keyword 通过

所有测试通过！
```

- [ ] **Step 5: Commit**

```bash
git add scripts/search.py tests/test_search.py
git commit -m "feat: add basic search functionality"
```

---

## Task 3: 关联推荐功能

**Files:**
- Create: `scripts/find_related.py`
- Create: `tests/test_find_related.py`

- [ ] **Step 1: 写失败的测试**

```python
#!/usr/bin/env python3
"""关联推荐测试"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def test_find_related_by_tags():
    """测试按标签找关联"""
    from find_related import find_related
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试笔记
        notes = {
            '2026-06-12-AI-Agent.md': '---\ntitle: AI Agent\ntags: [AI, Agent, 工作流]\n---\n\n内容',
            '2026-06-11-Python.md': '---\ntitle: Python\ntags: [Python, 编程]\n---\n\n内容',
            '2026-06-10-Agent框架.md': '---\ntitle: Agent框架\ntags: [AI, Agent, 框架]\n---\n\n内容',
        }
        for name, content in notes.items():
            with open(os.path.join(tmpdir, name), 'w') as f:
                f.write(content)
        
        # 测试找关联
        result = find_related(tmpdir, '2026-06-12-AI-Agent.md')
        assert len(result) > 0, "应该找到关联笔记"
        assert '2026-06-10-Agent框架.md' in result, "应该找到 Agent框架"
        print("✓ test_find_related_by_tags 通过")

if __name__ == '__main__':
    test_find_related_by_tags()
    print("\n所有测试通过！")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python tests/test_find_related.py`
Expected: ImportError

- [ ] **Step 3: 写最小实现**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python tests/test_find_related.py`
Expected:
```
✓ test_find_related_by_tags 通过

所有测试通过！
```

- [ ] **Step 5: Commit**

```bash
git add scripts/find_related.py tests/test_find_related.py
git commit -m "feat: add related notes recommendation"
```

---

## Task 4: 索引生成功能

**Files:**
- Create: `scripts/generate_index.py`
- Create: `tests/test_generate_index.py`

- [ ] **Step 1: 写失败的测试**

```python
#!/usr/bin/env python3
"""索引生成测试"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def test_generate_index():
    """测试生成索引"""
    from generate_index import generate_index
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试笔记
        notes = {
            '2026-06-12-AI-Agent.md': '---\ntitle: AI Agent入门\ntags: [AI, Agent]\ndate: 2026-06-12\n---\n\n内容',
            '2026-06-11-Python.md': '---\ntitle: Python基础\ntags: [Python]\ndate: 2026-06-11\n---\n\n内容',
        }
        for name, content in notes.items():
            with open(os.path.join(tmpdir, name), 'w') as f:
                f.write(content)
        
        # 生成索引
        index_path = os.path.join(tmpdir, 'INDEX.md')
        generate_index(tmpdir, index_path)
        
        # 验证索引文件存在
        assert os.path.exists(index_path), "索引文件应该存在"
        
        # 验证内容
        with open(index_path, 'r') as f:
            content = f.read()
        assert 'AI Agent' in content, "索引应包含 AI Agent"
        assert 'Python' in content, "索引应包含 Python"
        print("✓ test_generate_index 通过")

if __name__ == '__main__':
    test_generate_index()
    print("\n所有测试通过！")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python tests/test_generate_index.py`
Expected: ImportError

- [ ] **Step 3: 写最小实现**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python tests/test_generate_index.py`
Expected:
```
✓ test_generate_index 通过

所有测试通过！
```

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_index.py tests/test_generate_index.py
git commit -m "feat: add index generation"
```

---

## Task 5: 集成测试

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: 写集成测试**

```python
#!/usr/bin/env python3
"""集成测试 - 测试完整工作流"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def test_full_workflow():
    """测试完整工作流：创建笔记 -> 搜索 -> 找关联 -> 生成索引"""
    from search import search_notes, list_notes
    from find_related import find_related
    from generate_index import generate_index
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. 创建测试笔记
        notes = {
            '2026-06-12-AI-Agent.md': '---\ntitle: AI Agent入门\ntags: [AI, Agent]\ndate: 2026-06-12\n---\n\nAI Agent 是一种能够自主决策的智能体',
            '2026-06-11-Agent框架.md': '---\ntitle: Agent框架对比\ntags: [AI, Agent, 框架]\ndate: 2026-06-11\n---\n\n对比各种 Agent 框架',
            '2026-06-10-Python.md': '---\ntitle: Python基础\ntags: [Python, 编程]\ndate: 2026-06-10\n---\n\nPython 基础教程',
        }
        for name, content in notes.items():
            with open(os.path.join(tmpdir, name), 'w') as f:
                f.write(content)
        
        # 2. 测试列出
        all_notes = list_notes(tmpdir)
        assert len(all_notes) == 3, f"应有 3 条笔记，实际 {len(all_notes)}"
        print("✓ 列出笔记成功")
        
        # 3. 测试搜索
        ai_notes = search_notes(tmpdir, 'AI')
        assert len(ai_notes) == 2, f"应有 2 条 AI 相关笔记，实际 {len(ai_notes)}"
        print("✓ 搜索功能成功")
        
        # 4. 测试关联
        related = find_related(tmpdir, '2026-06-12-AI-Agent.md')
        assert len(related) > 0, "应找到关联笔记"
        print("✓ 关联推荐成功")
        
        # 5. 测试索引
        index_path = os.path.join(tmpdir, 'INDEX.md')
        generate_index(tmpdir, index_path)
        assert os.path.exists(index_path), "索引文件应存在"
        print("✓ 索引生成成功")
        
        print("\n✓ 集成测试通过！完整工作流正常！")

if __name__ == '__main__':
    test_full_workflow()
```

- [ ] **Step 2: 运行集成测试**

Run: `python tests/test_integration.py`
Expected:
```
✓ 列出笔记成功
✓ 搜索功能成功
✓ 关联推荐成功
✓ 索引生成成功

✓ 集成测试通过！完整工作流正常！
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests"
```

---

## Task 6: 创建示例笔记并验证

- [ ] **Step 1: 创建一条真实笔记**

在 `notes/` 目录创建：`2026-06-12-第一篇测试笔记.md`

```markdown
---
title: 第一篇测试笔记
url: https://example.com/test
tags: [测试, AI, 知识库]
date: 2026-06-12
---

## 摘要
这是一篇测试笔记，用于验证知识库功能。

## 要点
- 验证搜索功能
- 验证关联推荐
- 验证索引生成
```

- [ ] **Step 2: 运行搜索**

Run: `python scripts/search.py AI`
Expected: 找到测试笔记

- [ ] **Step 3: 运行索引生成**

Run: `python scripts/generate_index.py`
Expected: 生成 INDEX.md

- [ ] **Step 4: Commit**

```bash
git add notes/ INDEX.md
git commit -m "docs: add first test note and generate index"
```

---

## 完成检查清单

- [ ] 所有测试通过
- [ ] 搜索功能正常
- [ ] 关联推荐正常
- [ ] 索引生成正常
- [ ] CLAUDE.md 规则完整
- [ ] 目录结构正确

---

## 下一步（V2）

- [ ] 实现 Ingest 自动化（接收链接自动生成笔记）
- [ ] 添加周报生成功能
- [ ] 优化关联算法（加入标题关键词权重）
- [ ] 添加选题推荐功能
