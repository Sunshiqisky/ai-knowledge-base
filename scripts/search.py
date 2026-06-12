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
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='gbk') as file:
                    content = file.read()
            except UnicodeDecodeError:
                with open(filepath, 'r', encoding='latin-1') as file:
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
