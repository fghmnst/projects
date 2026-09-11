# AGENTS.md

本仓库（WSL 内 `~/SomeThingFunny/projects`，GitHub 公开仓库 `fghmnst/projects`）的职责：**辅助规划大二学习路径，并记录相关项目进度**。规划与笔记沉淀在 `obsidian/`，工程代码在仓库根目录各项目文件夹。本文件是**本机 opencode 专属指令**；子库 `obsidian/somezhishi/` 另有自己的 `AGENTS.md`，只管辖该子库。

## 一、当前阶段（2026 秋 · 大二上）

- **唯一事实源**：`obsidian/2026-2027 大二上学期学习计划.md`（目标 / 时间预算 / 双轨策略 / 阶段门 / 风险）。**计划变更必须写进周复盘并在计划文档中体现**，不口头漂移。
- **入口**：`obsidian/2026秋 Index.md`。
- **阶段门**：W4 轻门 → W9-10 期中门（四决策点）→ W16 云台 2.0 验收 → W18 期末复盘；到期必须核查并留记录。
- **本学期主线**：C 阶梯（P1→P3，代码 `C-tools/`）、云台 2.0（`gimbal2/`，W11 点火）、CET-6（12 月）、五门校内课双轨。C++ 寒假启动。
- **Agent 默认角色**：学习教练 + 进度管家。规划类讨论先读计划文档，一次一问、每问附推荐方案；进度写日志/复盘，不改计划本身（除非用户明确要求）。

## 二、公开仓库安全（强制）

- `projects` 与 `Novice-Village-Elite-Monsters` 均为 GitHub 公开仓库，任何 commit 立即对外可见。**严禁提交隐私信息**：
  - 凭据/密钥/Token（`.env` 内容、API key、SSH 私钥、机器人 App Secret 等）
  - 服务器 IP / SSH 端口 / 云账号信息（如 server2 的 HostName）
  - 个人标识：邮箱、OpenID、频道/群 ID、白名单值、Windows 用户名、手机号；成绩、排名、校名等个人信息
- **写文档一律「写位置不写值」**：服务器 IP 写「见 `~/.ssh/config`」、飞书凭据写「`~/.hermes/.env`」、白名单/群 ID 写「`~/.hermes/config.yaml` 的 `platforms.feishu`」。
- `git add` 前先 `git diff --cached` 自查；拿不准就写位置不写值。
- `.hermes.md` 已按安全规范清洗并重新纳入 git 跟踪（2026-09-10）；内容仍须「写位置不写值」。
- 历史文件（`obsidian/归档/30天学习/每日日志/` 8-04~8-18、`obsidian/somezhishi/环境排障/Hermes-云部署指南-飞书每日推送.md`）含已公开的 IP/OpenID/邮箱——不得复制其内容到新文件。

## 三、Agent 职责边界（opencode vs Hermes）

- 本文件是**本机 opencode 专属指令**，仅供 opencode 读取执行。
- **Hermes 不读本文件**：服务器 `/home/fghmnst/projects/.hermes.md` 优先级更高（发现顺序 `.hermes.md` → `AGENTS.md` → `CLAUDE.md`，先匹配先生效），本文件内容不会污染云端。
- opencode 职责：学习规划与进度记录、知识库管理、本机工程（编译/烧录/串口）、服务器只读运维。
- Hermes 职责：云端学习助理（飞书对话、daily-digest 晨报），行为由服务器 `.hermes.md` 约束。
- 下文「云端服务器工作流」各条均为 **opencode 的执行规范**，与 Hermes 自身行为无关。

## 四、规划与进度记录工作流

- **规划**：讨论前先读 `obsidian/2026-2027 大二上学期学习计划.md`；结论变更写入周复盘并在计划文档同步；阶段门到期必须核查。
- **每日**：日志写入 `obsidian/每日日志/YYYY-MM-DD.md`，当天结束更新，三栏（今日推进 / 卡点 / 明日一击），≤10min。
- **每周日 21:00**：周复盘 30min（产出 vs 时间账偏差 / 告警 / 下周微调），写入 `obsidian/周复盘/`，模板见 `obsidian/周复盘/周复盘.md`。
- **项目进度落点**：里程碑（P1/W4、P2/W7、P3/W10、云台验收/W16）在周复盘对照检查；卡点当日进日志，供后续 session 优先处理。
- 学习/规划对话默认中文；重要结论必须落文档，不留在对话里。

## 五、知识库与 Obsidian

- 知识库（vault）位于 **`~/SomeThingFunny/projects/obsidian`**（随本仓库 git 管理）。结构：`2026秋 Index.md`（学期入口）、`2026-2027 大二上学期学习计划.md`、`每日日志/`（含 Bases 自动索引）、`周复盘/`、`课程笔记/`（含 Bases 自动索引）、`somezhishi/`（沉淀子库，原 `TIL/` 已并入）、`归档/30天学习/`（30 天阶段历史）。
- **目录约定**：每个目录有同名索引笔记；Wikilink 一律写**显式路径**（如 `[[somezhishi/somezhishi|somezhishi]]`），不要用短名。
- **somezhishi 子库**（`obsidian/somezhishi/`，已纳入本仓库跟踪）遵循其自己的 `AGENTS.md`：日期 frontmatter、初学者向、一主题一篇、文件名用连字符；分 `工具速查/`、`环境排障/`、`编程基础/`、`项目笔记/` 四个子文件夹（不设同名索引），由顶层 `somezhishi/somezhishi.md` 统一导航。环境运维/工具坑（原 `TIL/`）与通用知识卡都进此库。
- **Obsidian 启动**：GUI 用 `~/.local/bin/obsidian-gui`（封装 `~/Downloads/Obsidian-1.13.7.AppImage`，WSLg/Wayland）；官方 CLI 在 `~/.local/bin/obsidian`，**要求 App 运行中**才能用。
- **操作约定**：涉及 vault 的读/写优先用 obsidian CLI 与技能（`obsidian-cli` / `obsidian-markdown` / `obsidian-bases` / `json-canvas` / `defuddle`）；纯 markdown 文本可直接编辑源文件；教学场景用 `teach` 技能。
- git 跟踪 vault 内 **markdown 笔记 + `.obsidian/` 配置**（设备相关文件与图片被 `.gitignore` 排除）。

## 六、项目与进度

- **云台项目背景**：PC(Python/OpenCV + PID) → 串口协议 → STM32F103C8T6 PWM → 2×SG90 云台 → 激光头。暑假完成 WASD 手动控制（`fire_control/`）；视觉追踪方案曾冻结。
- **DDM_test/**：⚠️ 已冻结（2026-08-23），代码与 git 历史保留；若恢复从限位校准 + 像素-角度映射起步。**STM32 新项目一律新建同类平铺 CMake 文件夹**。
- **fire_control/**：PC 端脚本（`servo_test.py` 等），云台 2.0 阶段复用/重构。
- **C-tools/**：C 阶梯三产物（P1 `note-stats` / P2 `prob-cli` / P3 `mytool`），W2 起逐步建立，纯 C + Makefile + git。
- **gimbal2/**：云台 2.0（W11 点火），目标：UART 中断/DMA + 环形缓冲 + 帧协议 + 分层 + 斜坡限幅，W16 验收。
- **CppSnake/**：已移除；C++ 线按计划推迟到寒假（触发条件：C 阶梯达标）。
- 参考仓库 `~/S90_aim_ball` 已不在本机；相关历史见 `obsidian/somezhishi/` 与 `obsidian/归档/`。

## 七、云端服务器（server2）工作流

### 连接
- 别名 `ssh server2`（`~/.ssh/config` 已配 ControlMaster 连接复用，服务器信息见 config，不写本文件）；WSL 与 Windows 共用同一把 ed25519 密钥，免密登录。
- **非交互 ssh 的 PATH 坑**：`hermes` 不在 PATH，`sudo` 也不含 `~/.local/bin`——一律写全路径 `~/.local/bin/hermes`。
- 服务器 **sudo 需要密码**（无免密），涉及 sudo 的操作交用户手动执行。

### 服务器现役设施
- **Hermes Agent**：provider `deepseek`，模型 `deepseek-v4-flash`（密钥在 `~/.hermes/.env`，非密钥配置在 `~/.hermes/config.yaml`）。
- **Hermes Gateway**：systemd 系统服务 `hermes-gateway`（开机自启）。**免 sudo 重启技巧**：`pkill -f "hermes_cli.main gateway"` → systemd 自动拉起（~30s）。网关状态 `systemctl status hermes-gateway`。
- **飞书机器人**（当前唯一消息平台）：平台 `feishu`，WebSocket 长连接；凭据 `~/.hermes/.env`；白名单与 home channel 见 `~/.hermes/config.yaml` 的 `platforms.feishu`（值不写本文件）。
- **QQ / 微信：已停用**，不要重新启用，除非用户明确要求。
- **文件系统检查点**：已启用（`checkpoints.enabled: true`），`/rollback` 可恢复被改坏的文件。
- **cron 任务 `daily-digest`**（`0 7 * * *`，`--deliver feishu --workdir /home/fghmnst/projects`）：git pull → 读昨日日志 → 生成「昨日小结+今日待办」→ 推飞书。**日志不 commit 就读不到**。
- **`~/projects`**：GitHub `fghmnst/projects` 的服务器 clone。

### 远程操作约定（必须遵守）
- **服务器操作一律只读**：agent 仅可 `ssh server2 'cmd'` 执行只读命令（ls/cat/grep/tail/git log/git status/git diff/ss/ps/日志查询等），执行路径（直连）在回复中注明。
- **一切写操作命令化交付（用户执行）**：改文件/配置、git 写操作、重启 gateway、cron 增删改、hermes 命令——一律输出可复制命令行 + 验证手段，用户手动执行并反馈。复杂命令先写脚本文件，用户仅执行脚本。
- 改 `.env`/`config.yaml` 后必须重启 gateway 生效；验证 `hermes doctor` + 日志。
- 日志：`~/.hermes/logs/gateway.log`、`agent.log`；推送成功标志 = `grep "delivered to feishu" ~/.hermes/logs/agent.log`。
- 详细部署与排障见 `obsidian/somezhishi/环境排障/Hermes-云部署指南-飞书每日推送.md`；Hermes 官方文档 `hermes-agent.nousresearch.com/docs/zh-Hans/reference/cli-commands`（本机已无 `hermes-ops` 技能）。

### 每日联动
- 用户每晚 commit 每日日志 → 次日 7:00 cron 推送依赖 `git pull` 拉到最新日志。
- 修改 vault 内容后应顺手 `git commit` 作为安全网（与 Hermes 云端约定一致）。

## 八、已定的技术决策（不要推翻）

- STM32 工具链：**vscode + STM32CubeMX(生成代码) + CMake**。
- 烧录器：ST-Link V2（SWD）；烧录通路 usbipd-win 直通 WSL（Plan B：Windows 侧 CubeProgrammer CLI）。
- 语言线：**C 是主线语言**（STM32 HAL + C 阶梯）；**C++ 寒假启动**（触发：C 阶梯达标）；Python 定位工具语言（视觉/脚本），本学期随课。
- 视觉方案：不沿用被否定的 HSV 快照方案；W11 启动周做选型门（见 `obsidian/somezhishi/项目笔记/视觉目标追踪方案对比.md`）。

## 九、已知坑

- **VS Code STM32 扩展「多个 CMake 项目」误报**：嵌入式开发用 `code ~/SomeThingFunny/projects/DDM_test`（或同类项目文件夹）单独开窗，仓库根窗口只做文档。
- SG90 舵机虚位大、有死区：需 PD 控制 + 软件死区（误差 <40px 停止调整）。
- 激光头与摄像头不重合导致打偏：需 `OFFSET_X`/`OFFSET_Y` 视差补偿。
- 2×SG90 需 5V/2A 独立供电，不要全从板子 USB 口取电。
- WSL 串口权限：CH340 → `/dev/ttyUSB0`，需 `dialout` 组；临时绕过 `sudo chmod 666 /dev/ttyUSB0`（重新枚举后失效）。
- Obsidian 在 WSLg 下必须走 `obsidian-gui`（设 `XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` + Wayland），不要直接跑 AppImage。

## 十、每日日志规范

- 每天一篇，写在 `obsidian/每日日志/YYYY-MM-DD.md`，当天结束时更新（≤10min）；frontmatter 写 `date: YYYY-MM-DD`（Bases 索引依赖）。
- **三栏**：
  1. **今日推进**：做了什么（含关键 commit/命令）。
  2. **卡点**：卡住的问题；需要用户手动做的事（sudo/浏览器/GUI/采购等）详录到命令级。
  3. **明日一击**：明天最重要的一件事。
- 底部加 `[[wikilinks]]` 关联（Index / somezhishi / 归档术语表）。
- 当天写完随代码一起 `git commit`。

## 十一、工程惯例

- 无 CI/lint/测试配置，验证方式 = vscode 编译 + 烧录 + 串口观察（PC 端脚本 = 实际运行）。
- 每天 `git commit` 作为安全网。
- **安装指令一律给命令行，让用户自行安装**：每条附带 ①验证手段 ②可能的问题与解法（含 Plan B）。
- 学习节奏：**20h/周**，主战场周五+周末；志愿者周砍序见计划文档；健身 6h/周（听力叠加）。
- 报告语言：中文。
