#!/usr/bin/env python3
"""AI 知识库 - 主程序入口"""
import os
import sys
import subprocess

# 添加 scripts 目录到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from search import list_notes, search_notes
from find_related import find_related
from generate_index import generate_index
from ingest import ingest_url
from suggest_topics import suggest_topics
from weekly_report import generate_weekly_report

NOTES_DIR = 'notes'

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """打印欢迎横幅"""
    print("=" * 50)
    print("       AI 知识库 - 个人知识管理系统")
    print("=" * 50)
    print()

def print_menu():
    """打印主菜单"""
    print("请选择操作：")
    print()
    print("  1. 查看所有笔记")
    print("  2. 搜索笔记")
    print("  3. 查看笔记关联")
    print("  4. 生成索引")
    print("  5. 添加新笔记")
    print("  6. 从链接导入（Ingest）")
    print("  7. 选题推荐")
    print("  8. 生成周报")
    print("  9. 查看使用帮助")
    print("  0. 退出")
    print()

def list_all_notes():
    """查看所有笔记"""
    print("\n【所有笔记】\n")
    notes = list_notes(NOTES_DIR)

    if not notes:
        print("还没有任何笔记。")
        print("请选择菜单 5 添加新笔记。")
        input("\n按回车键返回主菜单...")
        return

    print(f"共有 {len(notes)} 条笔记：\n")
    for i, note in enumerate(notes, 1):
        # 去掉 .md 后缀，显示更友好
        name = note.replace('.md', '')
        print(f"  {i}. {name}")

    print(f"\n笔记目录：{os.path.abspath(NOTES_DIR)}")
    input("\n按回车键返回主菜单...")

def search_notes_interactive():
    """搜索笔记"""
    print("\n【搜索笔记】\n")
    keyword = input("请输入搜索关键词：").strip()

    if not keyword:
        print("关键词不能为空。")
        input("\n按回车键返回主菜单...")
        return

    results = search_notes(NOTES_DIR, keyword)

    if not results:
        print(f"\n没有找到包含 '{keyword}' 的笔记。")
    else:
        print(f"\n找到 {len(results)} 条相关笔记：\n")
        for i, note in enumerate(results, 1):
            name = note.replace('.md', '')
            print(f"  {i}. {name}")

    input("\n按回车键返回主菜单...")

def find_related_interactive():
    """查看笔记关联"""
    print("\n【查看笔记关联】\n")
    notes = list_notes(NOTES_DIR)

    if not notes:
        print("还没有任何笔记。")
        input("\n按回车键返回主菜单...")
        return

    print("当前笔记列表：\n")
    for i, note in enumerate(notes, 1):
        name = note.replace('.md', '')
        print(f"  {i}. {name}")

    print()
    choice = input("请输入笔记编号（或文件名）：").strip()

    # 处理用户输入
    target_note = None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(notes):
            target_note = notes[idx]
        else:
            print("编号无效。")
            input("\n按回车键返回主菜单...")
            return
    elif choice in notes:
        target_note = choice
    elif choice + '.md' in notes:
        target_note = choice + '.md'
    else:
        print("未找到该笔记。")
        input("\n按回车键返回主菜单...")
        return

    print(f"\n正在查找与 {target_note} 相关的笔记...\n")
    related = find_related(NOTES_DIR, target_note)

    if not related:
        print("没有找到相关笔记。")
    else:
        print(f"找到 {len(related)} 条相关笔记：\n")
        for i, note in enumerate(related, 1):
            name = note.replace('.md', '')
            print(f"  {i}. {name}")

    input("\n按回车键返回主菜单...")

def generate_index_interactive():
    """生成索引"""
    print("\n【生成索引】\n")
    print("正在生成索引...")

    output_path = os.path.join(os.path.dirname(__file__), 'INDEX.md')
    generate_index(NOTES_DIR, output_path)

    print(f"\n索引已生成：{os.path.abspath(output_path)}")
    print("请用文本编辑器打开查看。")
    input("\n按回车键返回主菜单...")

def add_note_interactive():
    """添加新笔记"""
    print("\n【添加新笔记】\n")
    print("请填写笔记信息：\n")

    title = input("标题：").strip()
    if not title:
        print("标题不能为空。")
        input("\n按回车键返回主菜单...")
        return

    url = input("原文链接（可选，直接回车跳过）：").strip()
    tags_input = input("标签（用逗号分隔，如：AI,Agent,入门）：").strip()
    date = input("日期（YYYY-MM-DD，直接回车使用今天）：").strip()

    # 处理标签
    tags = [t.strip() for t in tags_input.split(',') if t.strip()] if tags_input else []

    # 处理日期
    if not date:
        from datetime import datetime
        date = datetime.now().strftime('%Y-%m-%d')

    # 生成文件名
    safe_title = title.replace(' ', '-').replace('/', '-').replace('\\', '-')
    filename = f"{date}-{safe_title}.md"
    filepath = os.path.join(NOTES_DIR, filename)

    # 生成笔记内容
    content = f"""---
title: {title}
"""
    if url:
        content += f"url: {url}\n"
    if tags:
        content += f"tags: [{', '.join(tags)}]\n"
    content += f"""date: {date}
---

## 摘要
（请在这里填写摘要）

## 要点
- （请在这里填写要点）
"""

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n笔记已创建：{os.path.abspath(filepath)}")
    print("\n请用文本编辑器打开，补充摘要和要点。")
    input("\n按回车键返回主菜单...")

def ingest_url_interactive():
    """从链接导入笔记"""
    print("\n【从链接导入笔记】\n")
    url = input("请输入链接：").strip()

    if not url:
        print("链接不能为空。")
        input("\n按回车键返回主菜单...")
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print()
    filepath = ingest_url(url, NOTES_DIR)

    if filepath:
        print(f"\n导入成功！")
        print(f"文件位置：{os.path.abspath(filepath)}")
        print("\n请用文本编辑器打开，补充或修改内容。")
    else:
        print("\n导入失败，请检查链接是否正确。")

    input("\n按回车键返回主菜单...")

def suggest_topics_interactive():
    """选题推荐"""
    print("\n【选题推荐】\n")
    print("正在分析笔记，生成选题建议...")

    briefs_dir = os.path.join(os.path.dirname(__file__), 'briefs')
    os.makedirs(briefs_dir, exist_ok=True)

    from datetime import datetime
    output_path = os.path.join(briefs_dir, f'{datetime.now().strftime("%Y-%m-%d")}-选题推荐.md')

    suggestions = suggest_topics(NOTES_DIR, output_path)

    if suggestions:
        print(f"\n共生成 {len(suggestions)} 个选题建议。")
        print(f"详细报告已保存到: {os.path.abspath(output_path)}")
        print("\n前 3 个选题：")
        for i, s in enumerate(suggestions[:3], 1):
            print(f"  {i}. {s['topic']}")
            print(f"     理由: {s['reason']}")
    else:
        print("\n暂无选题建议，请先添加更多笔记。")

    input("\n按回车键返回主菜单...")

def weekly_report_interactive():
    """生成周报"""
    print("\n【生成周报】\n")
    print("正在分析本周笔记...")

    briefs_dir = os.path.join(os.path.dirname(__file__), 'briefs')
    os.makedirs(briefs_dir, exist_ok=True)

    output_path = generate_weekly_report(NOTES_DIR, briefs_dir)

    print(f"\n周报已生成！")
    print(f"文件位置：{os.path.abspath(output_path)}")
    input("\n按回车键返回主菜单...")

def show_help():
    """显示帮助信息"""
    print("\n【使用帮助】\n")
    print("这是一个 AI 知识库系统，帮助你管理和检索笔记。")
    print()
    print("主要功能：")
    print("  1. 查看所有笔记 - 列出知识库中的所有笔记")
    print("  2. 搜索笔记 - 按关键词搜索笔记内容")
    print("  3. 查看笔记关联 - 找到与某篇笔记相关的其他笔记")
    print("  4. 生成索引 - 自动生成笔记目录")
    print("  5. 添加新笔记 - 手动创建新的笔记文件")
    print("  6. 从链接导入 - 输入链接，自动生成笔记（需要网络）")
    print("  7. 选题推荐 - 基于笔记主题推荐可写选题")
    print("  8. 生成周报 - 梳理本周入库内容")
    print()
    print("笔记格式：")
    print("  - 笔记存储在 notes/ 目录")
    print("  - 使用 Markdown 格式")
    print("  - 包含 frontmatter（标题、链接、标签、日期）")
    print()
    print("更多帮助：")
    print("  - 查看 README.md")
    print("  - 查看 AI知识库-产品设计文档.md")
    input("\n按回车键返回主菜单...")

def main():
    """主函数"""
    # 确保目录存在
    os.makedirs(NOTES_DIR, exist_ok=True)

    while True:
        clear_screen()
        print_banner()
        print_menu()

        choice = input("请输入选项编号：").strip()

        if choice == '1':
            list_all_notes()
        elif choice == '2':
            search_notes_interactive()
        elif choice == '3':
            find_related_interactive()
        elif choice == '4':
            generate_index_interactive()
        elif choice == '5':
            add_note_interactive()
        elif choice == '6':
            ingest_url_interactive()
        elif choice == '7':
            suggest_topics_interactive()
        elif choice == '8':
            weekly_report_interactive()
        elif choice == '9':
            show_help()
        elif choice == '0':
            print("\n感谢使用，再见！")
            break
        else:
            print("\n无效选项，请重新选择。")
            input("\n按回车键继续...")

if __name__ == '__main__':
    main()
