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
            with open(os.path.join(tmpdir, name), 'w', encoding='utf-8') as f:
                f.write(content)

        # 生成索引
        index_path = os.path.join(tmpdir, 'INDEX.md')
        generate_index(tmpdir, index_path)

        # 验证索引文件存在
        assert os.path.exists(index_path), "索引文件应该存在"

        # 验证内容
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'AI Agent' in content, "索引应包含 AI Agent"
        assert 'Python' in content, "索引应包含 Python"
        print("[PASS] test_generate_index 通过")

if __name__ == '__main__':
    test_generate_index()
    print("\n所有测试通过！")
