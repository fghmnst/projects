# AGENTS.md

本工作区是 30 天学习计划。核心产出是复刻「视觉追踪火控云台」（STM32 + OpenCV + PID），副线是 C++ 贪吃蛇。代码工作围绕主线展开；知识沉淀放 obsidian，不在本仓库。

## Agent 职责边界（opencode vs Hermes）

- 本文件是**本机 opencode 专属指令**（WSL 内 `/home/fgh/projects`），仅供 opencode 读取执行。
- **Hermes 不读本文件**：服务器 `/home/fghmnst/projects/.hermes.md` 优先级更高（Hermes 上下文文件发现顺序 `.hermes.md` → `AGENTS.md` → `CLAUDE.md`，先匹配先生效），Hermes 启动时只加载 `.hermes.md`，本文件内容不会污染云端。
- opencode 职责：本机工程（编译/烧录/串口）、知识库管理、每日日志撰写、服务器直连运维。
- Hermes 职责：云端学习助理（飞书对话、daily-digest 推送、学习建议），行为由服务器 `.hermes.md` 约束。
- 下文「云端服务器工作流」各条均为 **opencode 的执行规范**，与 Hermes 自身行为无关。

## 知识库与 Obsidian

- 知识库（obsidian vault）位于 **`/home/fgh/projects/obsidian`**（WSL 内，随 projects 仓库 git 管理）。结构：`30天学习 Index.md`（入口）、`每日日志/`、`教学-STM32/`（主线教学 workspace）、`教学-贪吃蛇/`（副线教学 workspace）、`模块笔记/`、`TIL/`、`术语表/`。**目录约定**：每个目录有同名索引笔记（如 `术语表/术语表.md`）；Wikilink 一律写**显式路径**（如 `[[术语表/术语表|术语表]]`），不要用短名——vault 存在多个同名笔记（两个教学 workspace 各有 MISSION/NOTES/术语表），短名会歧义。
- Obsidian 用 **Linux AppImage**（`~/bin/Obsidian.AppImage`）跑在 WSLg。命令行启动：`APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage &`。官方 CLI 在 `~/.local/bin/obsidian`，**要求 Obsidian App 正在运行**才能用。
- 教学场景用 `teach` 技能（教学工作区生成 MISSION.md/lessons/ 等，默认放 vault 内）；查/建笔记用 `obsidian-vault` 技能。
- **Obsidian 操作约定（必须遵守）**：涉及 vault 的读/写操作（查笔记、建/改/删笔记、搜内容、属性/标签/反向链接等）**优先使用 obsidian CLI**（`~/.local/bin/obsidian`，需 App 运行中）和相关 skills（`obsidian-cli` / `obsidian-markdown` / `obsidian-bases` / `obsidian-vault`）；但**编辑纯 markdown 文本时可直接修改 markdown 源文件**，仅当涉及双向链接（wikilinks）等 Obsidian 特色功能时必须使用 obsidian CLI。CLI 不可用（App 未启动）时，先启动 App 或报告用户。
- git 跟踪 vault 内的 **markdown 笔记 + `.obsidian/` 配置**（核心插件开关/主题/快捷键/插件数据随仓库跨设备同步，双链等特色功能换机即还原；仅 `workspace.json`/`cache/` 等设备相关文件被 `.gitignore` 排除）；图片等二进制仍排除（当前 0 附件，若未来启用需评估体积）。

## 主项目：视觉追踪火控云台

- 参考开源仓库（复刻对象）：`github.com/edythieajahgsgshwtvwywvwfd-sketch/S90_aim_ball`，本地 git clone 位于 **`~/S90_aim_ball`**（工作区外——2026-08-10 移出 `projects/`：其含独立 CMake 工程，留在工作区会触发 VS Code STM32 扩展「多个 CMake 项目」误报；代码不随本仓库 git 管理）
  - 文件布局：`Core/`(STM32 HAL 主程序)、`Drivers/`(HAL 驱动)、`ball_track.py`(视觉追踪)、`pid.py`(PID)、`color_picker.py`(HSV 阈值调色工具)、`S90_aim_ball.ioc`(CubeMX 配置)、CMake 工程
- 系统架构：PC(Python/OpenCV 识别橙色球 + PID) → 串口发送 `X增量,Y增量\n` → STM32F103C8T6 `sscanf` 解析 → PWM 驱动 2×SG90 舵机云台 → 激光头
- 视觉全部跑在 PC 端（OpenCV + pyserial），STM32 端只做串口解析和 PWM 输出

## 云端服务器（server2）工作流

### 连接
- 别名 `ssh server2`（`~/.ssh/config`：`[IP_REDACTED]` / `fghmnst` / 22，已配 ControlMaster 连接复用）；WSL 与 Windows 共用同一把 ed25519 密钥，免密登录。
- **非交互 ssh 的 PATH 坑**：`hermes` 不在 PATH，`sudo` 也不含 `~/.local/bin`——一律写全路径 `~/.local/bin/hermes`。
- 服务器 **sudo 需要密码**（无免密），涉及 sudo 的操作交用户手动执行。

### 服务器现役设施（2026-08-10 现状，飞书时代）
- **Hermes Agent**：provider `deepseek`，模型 `deepseek-v4-flash`（密钥在 `~/.hermes/.env`，非密钥配置在 `~/.hermes/config.yaml`）。
- **Hermes Gateway**：systemd 系统服务 `hermes-gateway`（开机自启）。**免 sudo 重启技巧**：`pkill -f "hermes_cli.main gateway"` → systemd 自动拉起（~30s），新进程读新配置；网关状态 `systemctl status hermes-gateway`。
- **飞书机器人**（2026-08-10 起启用，当前唯一消息平台——QQ markdown 仅支持受限子集、微信有 24h 主动消息限制，见 TIL 指南「平台选型」）：平台 `feishu`，**WebSocket 长连接模式（无需公网入口）**；凭据 `FEISHU_APP_ID/SECRET`（`~/.hermes/.env`）；私聊白名单 `FEISHU_ALLOWED_USERS=[FEISHU_UID_REDACTED]`；home channel `[FEISHU_CHAT_REDACTED]`（`config.yaml` 的 `platforms.feishu`）；飞书消息按 post 富文本渲染，markdown 自动降级纯文本（渲染失败不会乱码）。
- **QQ / 微信：已停用**（2026-08-10 迁移至飞书）：config.yaml `enabled: false` + .env 凭据已注释，备份在 `~/.hermes/.env.bak-[DATE_REDACTED]`。**不要重新启用**，除非用户明确要求。
- **文件系统检查点**：已启用（`checkpoints.enabled: true`），Hermes 对话内 `/rollback` 可恢复被改坏的文件。
- **cron 任务 `daily-digest`**（`0 7 * * *`，`--deliver feishu --workdir /home/fghmnst/projects`）：git pull → 读昨日日志 → 生成「昨日小结+今日待办」→ 推飞书。
- **`~/projects`**：GitHub 私有仓库 `fghmnst/projects` 的 clone（服务器专用 GitHub 密钥，公钥已加账号）。

### 远程操作约定（必须遵守）
- **服务器操作一律只读**：agent 仅可 `ssh server2 'cmd'` 执行**只读命令**（ls/cat/grep/tail/git log/git status/git diff/ss/ps/日志查询等，不修改服务器任何状态），执行路径（直连）在回复中注明。
- **一切写操作命令化交付（用户执行）**：凡会修改服务器状态的操作——文件写/改配置、`git pull`/commit 等 git 写操作、重启 gateway、cron 增删改、hermes 命令（查询/对话/写操作）——一律由 agent 输出可复制的命令行 + 验证手段，**用户手动执行并反馈结果**，agent 不直接执行。复杂命令（含引号 `"` `$` 反引号）agent 先写脚本文件，用户仅执行脚本。
- 改 `.env`/`config.yaml` 后必须重启 gateway 生效（pkill 技巧，命令化交付）；验证 `hermes doctor` + 日志。
- 日志：`~/.hermes/logs/gateway.log`（连接/消息）、`agent.log`（cron 执行/投递）；推送成功标志 = `grep "delivered to feishu" ~/.hermes/logs/agent.log`。
- 详细部署与排障见 `TIL/Hermes 云部署指南（飞书每日推送）.md`。
- **指挥 Hermes 优先用 `hermes-ops` skill**（`~/.agents/skills/hermes-ops/SKILL.md`，覆盖常用指令与本机约定）；skill 未覆盖的查 Hermes 官方文档（CLI 参考：`hermes-agent.nousresearch.com/docs/zh-Hans/reference/cli-commands`）。

### 每日联动
- 用户每晚 commit 每日日志 → 次日 7:00 cron 推送依赖 `git pull` 拉到最新日志（不提交就读不到）。
- 修改 vault 内容后应顺手 `git commit` 作为安全网（与 Hermes 云端约定一致）。

## 已定的技术决策（不要推翻）

- STM32 工具链：**vscode + STM32CubeMX(生成代码) + CMake**。参考仓库原用 CLion+CubeMX，用户已决定改用 vscode。
- 副线贪吃蛇：**C++**。主线 STM32 用 C(HAL)，Python 定位为工具语言（视觉/脚本），均不引入第三方学习路线。
- 烧录器：用户已有 ST-Link V2（SWD 烧录，2026-08-08 确认）。烧录通路：usbipd-win 直通 WSL（Plan B：Windows 侧 CubeProgrammer CLI，永不阻塞）。

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
- **安装指令一律给命令行，让用户自行安装**（除非用户特殊说明，如明确要求 agent 代装）：涉及任何安装（WSL apt / Windows winget / 浏览器下载 / 插件等），只输出可复制的命令行给用户执行，不代为安装。每条安装指令必须附带：① **验证手段**（验证命令或检查清单）；② **可能遇到的问题**（坑与对应解法，含 Plan B 降级路径）。参考模板：`教学-STM32/lessons/0001` 第四节「动手 1：安装工具链」。
- 学习节奏：每周 5 深度日 + 2 浅度日，深度日 8h 里上午/下午给主线、晚上给贪吃蛇；浅度日只做维护性任务，不安排主线硬核内容。
