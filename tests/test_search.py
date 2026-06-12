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
        print("[PASS] test_list_all_notes 通过")

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
        print("[PASS] test_search_by_keyword 通过")

if __name__ == '__main__':
    test_list_all_notes()
    test_search_by_keyword()
    print("\n[PASS] 所有测试通过！")
