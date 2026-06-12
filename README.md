# AI 知识库

一个 AI 原生的个人知识管理系统，支持链接抓取、自动整理、智能搜索、关联推荐。

## 🚀 快速开始

### 方法一：双击启动（推荐）

双击 `启动知识库.bat` 文件即可打开程序。

### 方法二：命令行启动

```bash
python main.py
```

## 📖 功能说明

### 1. 查看所有笔记
列出知识库中的所有笔记文件。

### 2. 搜索笔记
按关键词搜索笔记内容（搜索标题、标签、摘要）。

### 3. 查看笔记关联
找到与某篇笔记相关的其他笔记（基于标签重叠）。

### 4. 生成索引
自动生成按时间排序、按标签分类的笔记目录。

### 5. 添加新笔记
创建新的笔记文件，自动填写 frontmatter。

## 📝 笔记格式

在 `notes/` 目录创建 `.md` 文件，格式如下：

```markdown
---
title: 笔记标题
url: https://... (可选)
tags: [标签1, 标签2, 标签3]
date: 2026-06-12
---

## 摘要
2-3 句话概括这篇文章

## 要点
- 要点一
- 要点二
- 要点三
```

## 📁 目录结构

```
├── main.py                  # 主程序（交互式界面）
├── 启动知识库.bat            # Windows 启动脚本
├── notes/                   # 笔记存储目录
├── scripts/                 # 功能脚本
│   ├── search.py           # 搜索
│   ├── find_related.py     # 关联推荐
│   └── generate_index.py   # 索引生成
├── tests/                   # 测试文件
├── CLAUDE.md               # AI 工作流规则
├── STATUS.md               # 项目状态跟踪
└── AI知识库-产品设计文档.md  # 产品设计文档
```

## 🛠️ 命令行工具

除了交互式界面，也可以直接使用命令行：

```bash
# 列出所有笔记
python scripts/search.py

# 搜索笔记
python scripts/search.py 关键词

# 查找关联
python scripts/find_related.py 笔记文件名.md

# 生成索引
python scripts/generate_index.py
```

## 📚 相关文档

- `AI知识库-产品设计文档.md` - 完整产品设计
- `STATUS.md` - 项目状态和进度
- `CLAUDE.md` - AI 工作流规则

## 🎯 下一步

1. 往 `notes/` 添加你的真实笔记
2. 尝试搜索和关联功能
3. 定期生成索引，整理知识库

---

**项目地址**：https://github.com/Sunshiqisky/ai-knowledge-base
