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
