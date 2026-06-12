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
            with open(os.path.join(tmpdir, name), 'w', encoding='utf-8') as f:
                f.write(content)

        # 2. 测试列出
        all_notes = list_notes(tmpdir)
        assert len(all_notes) == 3, f"应有 3 条笔记，实际 {len(all_notes)}"
        print("[PASS] 列出笔记成功")

        # 3. 测试搜索
        ai_notes = search_notes(tmpdir, 'AI')
        assert len(ai_notes) == 2, f"应有 2 条 AI 相关笔记，实际 {len(ai_notes)}"
        print("[PASS] 搜索功能成功")

        # 4. 测试关联
        related = find_related(tmpdir, '2026-06-12-AI-Agent.md')
        assert len(related) > 0, "应找到关联笔记"
        print("[PASS] 关联推荐成功")

        # 5. 测试索引
        index_path = os.path.join(tmpdir, 'INDEX.md')
        generate_index(tmpdir, index_path)
        assert os.path.exists(index_path), "索引文件应存在"
        print("[PASS] 索引生成成功")

        print("\n[PASS] 集成测试通过！完整工作流正常！")

if __name__ == '__main__':
    test_full_workflow()
