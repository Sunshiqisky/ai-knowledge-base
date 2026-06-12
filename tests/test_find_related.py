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
            with open(os.path.join(tmpdir, name), 'w', encoding='utf-8') as f:
                f.write(content)

        # 测试找关联
        result = find_related(tmpdir, '2026-06-12-AI-Agent.md')
        assert len(result) > 0, "应该找到关联笔记"
        assert '2026-06-10-Agent框架.md' in result, "应该找到 Agent框架"
        print("[PASS] test_find_related_by_tags 通过")

if __name__ == '__main__':
    test_find_related_by_tags()
    print("\n所有测试通过！")
