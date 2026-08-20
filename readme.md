# projects
该仓库用于备份我在推进某些小项目时产生的文件，同时也展现了项目的几乎全部细节。**除了这篇readme是我自己手敲的以外，其他全部内容均由AI或其他工具生成**。

## 文件介绍
1. `DDM_test` cubemx生成，opencode修改的工程源文件

2. `fire_control` 键盘与云台进行wasd交互的python程序

3. `obsidian` 笔记仓库

4. `.hermes.md` 给云端hermes看的辅助进行工作区理解的文件

5. `readme.md` 给opencode看的辅助进行工作区理解的文件

6. `CppSnake` 暂时搁置的贪吃蛇项目

# 项目介绍

## 火控云台
目标：复刻https://zhuanlan.zhihu.com/p/1992580909858305860 中的视觉追踪火控云台。

目前已经能够做到使用wasd来控制云台的移动。
# 工作流介绍

板子使用的是stm32f103c8t6，代码编辑环境为wsl端的vscode，系统是Ubuntu24.04，使用stlink进行调试和烧录，并通过开源项目WSL Dashboard 将USB设备共享至wsl端。

首先使用linux端的cubemx生成源代码，然后再在vscode中利用opencode按需求生成代码，最后在stm32的官方插件进行调试、编译和烧录。

其中，opencode会在项目推进的过程中将某些知识点、术语、遇到的坑与每天的工作日志等整理为markdown笔记，并存放在obsidian文件夹中，可随时用wsl端的obsidian查看，后续也可通过插件来进行多设备的同步。

Hermes为我在云服务器端部署的另一个AI助手，可通过我的飞书来与其进行对话，每天早上七点git pull此仓库，并告诉我昨天做了什么，今天应该做什么。



