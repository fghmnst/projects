# AGENTS.md

本工作区是 30 天学习计划。核心产出是复刻「视觉追踪火控云台」（STM32 + OpenCV + PID），副线是 C++ 贪吃蛇。代码工作围绕主线展开；知识沉淀放 obsidian，不在本仓库。

## 知识库与 Obsidian

- 知识库（obsidian vault）位于 **`/home/fgh/projects/obsidian`**（WSL 内，随 projects 仓库 git 管理）。结构：`30天学习 Index.md`（入口）、`每日日志/`、`模块笔记/`、`TIL/`、`术语表/`。
- Obsidian 用 **Linux AppImage**（`~/bin/Obsidian.AppImage`）跑在 WSLg。命令行启动：`APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage &`。官方 CLI 在 `~/.local/bin/obsidian`，**要求 Obsidian App 正在运行**才能用。
- 教学场景用 `teach` 技能（教学工作区生成 MISSION.md/lessons/ 等，默认放 vault 内）；查/建笔记用 `obsidian-vault` 技能。
- **Obsidian 操作约定（必须遵守）**：所有涉及 vault 的读/写操作（查笔记、建/改/删笔记、搜内容、属性/标签/反向链接等）一律通过 **obsidian CLI**（`~/.local/bin/obsidian`，需 App 运行中）和相关 skills（`obsidian-cli` / `obsidian-markdown` / `obsidian-bases` / `obsidian-vault`）执行，**禁止直接编辑/创建 vault 内的 markdown 源文件**。CLI 不可用（App 未启动）时，先启动 App 或报告用户，而非绕过规则直接改文件。
- git 只跟踪 vault 内的 **markdown 笔记**（`.obsidian/` 配置与图片等二进制被 `.gitignore` 排除），知识随代码仓库一起备份/回退。

## 主项目：视觉追踪火控云台

- 参考开源仓库：`github.com/edythieajahgsgshwtvwywvwfd-sketch/S90_aim_ball`（用户提供的复刻对象，源码已可获取）
  - 文件布局：`Core/`(STM32 HAL 主程序)、`Drivers/`(HAL 驱动)、`ball_track.py`(视觉追踪)、`pid.py`(PID)、`color_picker.py`(HSV 阈值调色工具)、`S90_aim_ball.ioc`(CubeMX 配置)、CMake 工程
- 系统架构：PC(Python/OpenCV 识别橙色球 + PID) → 串口发送 `X增量,Y增量\n` → STM32F103C8T6 `sscanf` 解析 → PWM 驱动 2×SG90 舵机云台 → 激光头
- 视觉全部跑在 PC 端（OpenCV + pyserial），STM32 端只做串口解析和 PWM 输出

## 已定的技术决策（不要推翻）

- STM32 工具链：**vscode + STM32CubeMX(生成代码) + CMake**。参考仓库原用 CLion+CubeMX，用户已决定改用 vscode。
- 副线贪吃蛇：**C++**。主线 STM32 用 C(HAL)，Python 定位为工具语言（视觉/脚本），均不引入第三方学习路线。
- 烧录器：需确认用户是否有 ST-Link V2；尚未配置（可能需采购约 10 元的 ST-Link）。

## 已知坑（来自参考文章，直接相关）

- SG90 舵机虚位大、有死区：需 PD 控制 + 软件死区（误差 <40px 停止调整），见参考仓库 `pid.py`。
- 激光头与摄像头物理不重合导致打偏：需要 `OFFSET_X`/`OFFSET_Y` 视差补偿。
- 2×SG90 需 5V/2A 独立供电，不要全从板子 USB 口取电。

## 每日日志规范

- 每天一篇，写在 `obsidian/每日日志/YYYY-MM-DD.md`，当天结束时更新。
- 必须包含以下栏目：
  1. **今日完成事项**：做了什么（含关键 commit/命令）。
  2. **手动操作事项**：涉及 sudo/浏览器/GUI/采购等必须用户手动做的事，详录到命令级，供换电脑重搭环境时照做。
  3. **运行环境现状**：`✅ 已完成` / `❌ 缺少/待办` 两份清单。
  4. **计划/工作流待办**：未决事项、工具盘点报告中的待办、待确认决策。
  5. **疑惑点**：用户不理解的、卡住的、待解答的问题（重点记录，供后续 session 优先处理）。
- 底部加 `[[wikilinks]]` 关联（Index / TIL / 术语表）。
- 当天写完随代码一起 `git commit`。

## 工程惯例

- 无 CI/lint/测试配置，验证方式 = vscode 编译 + 烧录 + 串口观察。
- 每天 `git commit` 作为安全网（PID 调参改坏可回退）。
- 学习节奏：每周 5 深度日 + 2 浅度日，深度日 8h 里上午/下午给主线、晚上给贪吃蛇；浅度日只做维护性任务，不安排主线硬核内容。
