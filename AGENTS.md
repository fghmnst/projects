# AGENTS.md

本工作区是 30 天学习计划。核心产出是复刻「视觉追踪火控云台」（STM32 + OpenCV + PID），副线是 C++ 贪吃蛇。代码工作围绕主线展开；知识沉淀放 obsidian，不在本仓库。

## 知识库与 Obsidian

- 知识库（obsidian vault）位于 **`/home/fgh/projects/obsidian`**（WSL 内，随 projects 仓库 git 管理）。结构：`30天学习 Index.md`（入口）、`每日日志/`、`模块笔记/`、`TIL/`、`术语表/`。
- Obsidian 用 **Linux AppImage**（`~/bin/Obsidian.AppImage`）跑在 WSLg。命令行启动：`APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage &`。官方 CLI 在 `~/.local/bin/obsidian`，**要求 Obsidian App 正在运行**才能用。
- 教学场景用 `teach` 技能（教学工作区生成 MISSION.md/lessons/ 等，默认放 vault 内）；查/建笔记用 `obsidian-vault` 技能。
- **Obsidian 操作约定（必须遵守）**：涉及 vault 的读/写操作（查笔记、建/改/删笔记、搜内容、属性/标签/反向链接等）**优先使用 obsidian CLI**（`~/.local/bin/obsidian`，需 App 运行中）和相关 skills（`obsidian-cli` / `obsidian-markdown` / `obsidian-bases` / `obsidian-vault`）；但**编辑纯 markdown 文本时可直接修改 markdown 源文件**，仅当涉及双向链接（wikilinks）等 Obsidian 特色功能时必须使用 obsidian CLI。CLI 不可用（App 未启动）时，先启动 App 或报告用户。
- git 只跟踪 vault 内的 **markdown 笔记**（`.obsidian/` 配置与图片等二进制被 `.gitignore` 排除），知识随代码仓库一起备份/回退。

## 主项目：视觉追踪火控云台

- 参考开源仓库：`github.com/edythieajahgsgshwtvwywvwfd-sketch/S90_aim_ball`（用户提供的复刻对象，源码已可获取）
  - 文件布局：`Core/`(STM32 HAL 主程序)、`Drivers/`(HAL 驱动)、`ball_track.py`(视觉追踪)、`pid.py`(PID)、`color_picker.py`(HSV 阈值调色工具)、`S90_aim_ball.ioc`(CubeMX 配置)、CMake 工程
- 系统架构：PC(Python/OpenCV 识别橙色球 + PID) → 串口发送 `X增量,Y增量\n` → STM32F103C8T6 `sscanf` 解析 → PWM 驱动 2×SG90 舵机云台 → 激光头
- 视觉全部跑在 PC 端（OpenCV + pyserial），STM32 端只做串口解析和 PWM 输出

## 云端服务器（server2）工作流

### 连接
- 别名 `ssh server2`（`~/.ssh/config`：`[IP_REDACTED]` / `fghmnst` / 22，已配 ControlMaster 连接复用）；WSL 与 Windows 共用同一把 ed25519 密钥，免密登录。
- **非交互 ssh 的 PATH 坑**：`hermes` 不在 PATH，`sudo` 也不含 `~/.local/bin`——一律写全路径 `~/.local/bin/hermes`（tmux 在 `/usr/bin` 无碍）。
- 服务器 **sudo 需要密码**（无免密），涉及 sudo 的操作交用户手动执行。

### 服务器现役设施（2026-08-07 部署）
- **Hermes Agent**：provider `minimax-cn`（密钥在 `~/.hermes/.env`，非密钥配置在 `~/.hermes/config.yaml`）。
- **Hermes Gateway**：systemd 系统服务 `hermes-gateway`（开机自启）。**免 sudo 重启技巧**：`pkill -f "hermes_cli.main gateway"` → systemd 自动拉起（~30s），新进程读新配置。
- **QQ 机器人 Kricyan_Hermes**（AppID `1905371061`）：私聊白名单仅用户 OpenID `[QQ_OPENID_REDACTED]`；cron 投递目标 = `QQBOT_HOME_CHANNEL`（同 OpenID）。
- **cron 任务 `daily-digest`**（`0 7 * * *`，`--deliver qqbot --workdir /home/fghmnst/projects`）：git pull → 读昨日日志 → 生成「昨日小结+今日待办」→ 推 QQ。
- **`~/projects`**：GitHub 私有仓库 `fghmnst/projects` 的 clone（服务器专用 GitHub 密钥，公钥已加账号）。
- **tmux 会话 `work`**：cwd `~/projects`，`history-limit 10000`，`remain-on-exit on`。

### 远程操作约定（必须遵守）
- **日常操作优先走 tmux**：注入 = `ssh server2 'tmux send-keys -t work "cmd; echo __DONE__" Enter'`；读输出 = `ssh server2 'tmux capture-pane -t work -p -S -50'`；轮询哨兵 `__DONE__` 确认完成。
- **并发锁**：操作前先 `ssh server2 'test -f ~/.tmux-hold && echo HELD || echo FREE'`，`HELD` 表示用户正在打字，**必须停手等待**；用户打字前会 touch 锁、打完 rm 锁。锁存在期间绝不 send-keys。
- 复杂命令（含 `"` `$` 反引号）先写脚本 scp 到服务器 `/tmp`，再在 tmux 里执行，避免转义问题。
- pane 显示 `Pane is dead`：`tmux respawn-pane -t work` 复活（用户 Ctrl+D 属正常操作，非故障）。
- 服务器重启后 tmux 会话丢失：重建 = `tmux new-session -d -s work -c /home/fghmnst/projects` + 两条 `set-option`（见 TIL 手册）。
- 改 `.env`/`config.yaml` 后必须重启 gateway 生效（pkill 技巧）；验证 `hermes doctor` + 日志。
- 日志：`~/.hermes/logs/gateway.log`（连接/消息）、`agent.log`（cron 执行/投递）；推送成功标志 = `grep "delivered to qqbot" ~/.hermes/logs/agent.log`。
- 详细部署与排障见 `TIL/Hermes 云部署指南（QQ 每日推送）.md`；用户操作见 `TIL/tmux 共享终端操作手册.md`。
- **指挥 Hermes 优先用 `hermes-ops` skill**（`~/.agents/skills/hermes-ops/SKILL.md`，覆盖常用指令与本机约定）；skill 未覆盖的查 Hermes 官方文档（CLI 参考：`hermes-agent.nousresearch.com/docs/zh-Hans/reference/cli-commands`）。

### 每日联动
- 用户每晚 commit 每日日志 → 次日 7:00 cron 推送依赖 `git pull` 拉到最新日志（不提交就读不到）。

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
