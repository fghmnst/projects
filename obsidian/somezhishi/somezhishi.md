---
date: 2026-09-11
---

# somezhishi

> 个人知识沉淀库：环境运维 / 工具坑 / 通用知识卡。创建或修改笔记前先读 [[somezhishi/AGENTS|AGENTS.md]]。
> 原 vault 顶层 `TIL/` 已于 2026-09-11 并入本库；四个子文件夹由本页统一索引。

## 工具速查

| 笔记 | 一句话 |
|---|---|
| [[somezhishi/工具速查/opencode-TUI-速查表\|opencode TUI 速查表]] | 斜杠指令、输入语法、本机自定义键位 |
| [[somezhishi/工具速查/tmux-共享终端操作手册\|tmux 共享终端操作手册]] | 进入方式、日常操作全表、故障排查 |
| [[somezhishi/工具速查/Translate-Pro-快捷键速查表\|Translate Pro 快捷键速查表]] | 划词翻译快捷键与使用提示 |
| [[somezhishi/工具速查/GitHub贡献计算-规则与排查\|GitHub 贡献计算]] | 计入规则、push 与邮箱分工、隐私配置与排查 |

## 环境排障

| 笔记 | 一句话 |
|---|---|
| [[somezhishi/环境排障/Obsidian-启动排障\|Obsidian 启动排障]] | 依赖缺失、T 态挂起、WSLg 窗口不可见 |
| [[somezhishi/环境排障/WSL-串口权限-dialout组与chmod临时方案\|WSL 串口权限]] | dialout 组与 chmod 临时方案 |
| [[somezhishi/环境排障/Hermes-云部署指南-飞书每日推送\|Hermes 云部署指南]] | 飞书每日推送：部署、踩坑、日常运维 |
| [[somezhishi/环境排障/VSCode-C++插件-IntelliSense配置与gcc-g++区别\|VS Code C/C++ 插件]] | IntelliSense 告警根因、远程设置修复、gcc/g++ 区别 |

## 编程基础

| 笔记 | 一句话 |
|---|---|
| [[somezhishi/编程基础/Linux权限-chmod详解\|Linux 权限：chmod]] | 权限基础、符号/数字模式、WSL 解压丢权限 |
| [[somezhishi/编程基础/Linux任务控制-JobControl与kill\|Linux 任务控制：Job Control 与 kill]] | 前后台切换、nohup/setsid、信号与 pkill |
| [[somezhishi/编程基础/Linux重定向-文件描述符与2&1详解\|Linux 重定向]] | 文件描述符、2>&1、书写顺序坑 |
| [[somezhishi/编程基础/Git多远程-切换与双仓库同步\|Git 多远程]] | 切换远程、双仓库同步、排查速查 |
| [[somezhishi/编程基础/SSH密钥-修改口令与ssh-keygen参数详解\|SSH 密钥]] | 修改/移除口令、ssh-keygen 参数 |
| [[somezhishi/编程基础/构建工具链-CMake与make与Ninja详解\|构建工具链：CMake/make/Ninja]] | 三者关系、apt 前置与包名坑、交叉编译器 arm-none-eabi-gcc |
| [[somezhishi/编程基础/RAG与MCP-概念与本仓库适用性判断\|RAG 与 MCP]] | 概念、关系、本仓库为何暂不需要、触发条件 |

## 项目笔记

| 笔记 | 一句话 |
|---|---|
| [[somezhishi/项目笔记/视觉目标追踪方案对比\|视觉目标追踪方案对比]] | HSV vs 更普适方案、本项目决策与实测 |
| [[somezhishi/项目笔记/STM32工具链-CubeMX与CubeCLT详解\|STM32 工具链：CubeMX 与 CubeCLT]] | 二者分工、arm-none-eabi-gcc 下载方式、本机工具盘点 |
| [[somezhishi/项目笔记/一生一芯-项目简介与观望记录\|一生一芯]] | 项目简介、契合度结论、寒假试探清单与决策记录 |

## 标签

- **类型**：`速查` · `排障` · `入门` · `指南` · `决策`
- **领域**：`工具` · `obsidian` · `wsl` · `hermes` · `linux` · `git` · `ssh` · `opencode` · `tmux` · `项目`
- 用法：用标签面板按类型/领域筛选；新笔记从词表选标签，不新造同义词

## 约定

- 一主题一篇；文件名 `主题-子主题.md`（空格用连字符）
- 每篇必须有 `date:` frontmatter（+ 词表内的 `tags:`）
- 内容面向初学者：概念讲清「是什么、为什么、怎么用」，命令配解释
