# NOTES.md（教学偏好与工作笔记）

## 用户偏好（继承自贪吃蛇课程 2026-08-08 确立）

- **课程用 markdown 编写**，不用 teach skill 默认的 HTML lessons。交互练习用「obsidian callout + 终端/硬件改代码看效果」实现。
- 教学工作区位于 obsidian vault 内（`obsidian/教学-STM32/`），随仓库 git 备份。
- 用户是「看懂 ≠ 记住」的典型学习者：每课末尾必须有动手任务（retrieval practice），不能只看不练。
- 课程产出（lessons/）应通过 wikilinks 与每日日志、术语表、Index 关联。
- 术语：对话与课程尽量用中文讲解，专业术语首次出现附英文原名。
- 课程内建术语表（`reference/术语表.md`）；vault 顶层 `术语表/` 目录已建，主线推进中可逐步填充。

## 主线特有

- 参考仓库源码已通读（main.c / ball_track.py / pid.py），但未动手实践——先验知识只按"读过"记，不按"掌握"记。
- 里程碑节奏：W1 串口转舵机 → W2 云台追球（P 控制）→ W3 PID 稳定跟随 → W4 组装调优 demo。
- 硬件操作（接线、供电、烧录）涉及实体设备，动手课时用户需要在场操作硬件，agent 负责讲解与指导。

## 工作笔记

- 2026-08-08：确认用户有 ST-Link V2（SWD 烧录）。工具链未装：Windows 缺 CubeMX/CubeProgrammer，WSL 缺 arm-none-eabi-gcc/cmake。
- 2026-08-08：WSL2 访问 USB 的限制待验证（usbipd-win 或 Windows 侧烧录二选一）。
