# projects
该仓库现如今作为我日常学习工作的AI工作流的重要一环，负担起文件备份，多设备同步的责任，同时也是部署在云端服务器的hermes的每日推送的重要依据。


**除了这篇readme是我自己手敲的以外，其他全部内容均由AI或其他工具生成**。

# 工作流介绍
用到的硬件：

1. 电脑
2. 服务器（我自己在雨云租了一个）
3. 移动端设备

用到的软件：

1. vscode
2. wsl（我用的是Ubuntu24.04）
3. opencode
4. obsidian（win端，wsl端，移动端）
5. Hermes（云服务器端）
6. git

主角是obsidian，obsidian如果玩明白了本身就能作为强大的知识库和任务管理器，同时配置一波坚果云和remotely save可以实现多端同步。

工作流的智能核心是opencode，理由是在wsl环境下可以非常快速准确地执行任务，最重要的是我用得顺手。

obsidian的主战场是wsl，理由是这样opencode可以非常方便地读取和操作知识库。

vscode的作用是提供一个现代且直观的编辑环境，还能够将许多操作都集成在一块。

git的作用是版本追踪，同时还能够上传至github远程仓库来进行文件备份。我们的笔记都是用md格式存放在obsidian中的，非常适合使用git进行版本追踪，且其他文件也是有版本追踪和备份的需求的。

Hermes为我在云服务器端部署的另一个AI助手，可通过我的飞书来与其进行对话，每天早上七点git pull此仓库，并告诉我昨天做了什么，今天应该做什么。

具体运转流程：

先在wsl环境中的vscode中与opencode对话，确认要求后opencode落实操作，接着推送至github，与此同时使用remotely save插件同步obsidian笔记。第二天云端的hermes会先git pull该仓库并在移动端飞书给我推送当日任务与昨日总结。移动端的obsidian可通过remotely save同步笔记。

# 项目介绍

## 火控云台（DDM_test）

目标：复刻网上见过的一个中的视觉追踪火控云台。

板子使用的是stm32f103c8t6，代码编辑环境为wsl端的vscode，系统是Ubuntu24.04，使用stlink进行调试和烧录，并通过开源项目WSL Dashboard 将USB设备共享至wsl端。

首先使用wsl端的cubemx生成源代码，然后再在vscode中利用opencode按需求生成代码，最后在stm32的官方插件进行调试、编译和烧录。

目前已经能够做到使用wasd来控制云台的移动。

## C-tools

尝试在AI的辅导下编写一个类似git的小工具。





