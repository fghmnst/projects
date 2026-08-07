# Hermes 云部署指南（QQ 每日推送）

**日期**：2026-08-06
**场景**：在云服务器上配置 Hermes Agent，让它每天 7:00 通过 QQ 机器人推送「昨日小结 + 今日待办」，内容来自 GitHub 私有仓库的每日日志。

## 最终效果

```
每天 07:00（Asia/Shanghai）→ 服务器 Hermes cron 触发
  → git pull 私有仓库 projects
  → 读取 obsidian/每日日志/ 昨天的日志
  → 生成【昨日小结】【今日待办】
  → 推送到你的 QQ（机器人 Kricyan_Hermes）
```

## 架构

```
本地 WSL ──ssh server2──> 云服务器（RainYun, Ubuntu）
                           ├─ Hermes Agent（~/.hermes，provider: minimax-cn）
                           ├─ Hermes Gateway（systemd 服务，24h 常驻）
                           │    ├─ QQ Bot 适配器（WebSocket ↔ QQ 官方 API）
                           │    └─ Cron 调度器（每 60s tick）
                           └─ ~/projects（GitHub 私有仓库 clone）
```

## 前置准备

| 项目 | 说明 |
|------|------|
| 云服务器 | Ubuntu（本例 RainYun 小 VPS，1.9G 内存够用），Hermes 已安装可对话 |
| QQ 官方机器人 | 在 [q.qq.com](https://q.qq.com) 创建应用，拿到 **App ID** 和 **App Secret** |
| GitHub 账号 | 用于授权服务器读取私有仓库 |
| 本地 ssh | WSL 与 Windows 共用同一对 ed25519 密钥（已在服务器 authorized_keys） |

> 注意：Hermes 的 QQ 适配器用的是**官方 QQ Bot API**（机器人形态），不是个人 QQ 号挂协议。机器人需支持 C2C 私聊；新机器人默认沙盒模式，只能和沙盒成员互动。

## 步骤

### 1. 本地 ssh 别名（WSL）

Windows 侧的 `C:\Users\<你>\.ssh\config` 可能已配好别名，但 WSL 不共享它，需在 `~/.ssh/config` 写一份：

```
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 10

Host server2
    HostName  [IP_REDACTED]
    User fghmnst
    Port 22
```

验证：`ssh server2` 能免密登录即 OK。

### 2. 服务器基础准备

```bash
ssh server2
sudo timedatectl set-timezone Asia/Shanghai   # 关键！cron 按服务器本地时区走
```

生成 GitHub 专用密钥（与登录用的密钥分开，最小授权）：

```bash
ssh-keygen -t ed25519 -N "" -C "server2-fghmnst" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub   # 复制公钥
```

去 GitHub → Settings → SSH and GPG keys → New SSH key 粘贴，然后：

```bash
ssh -T git@github.com   # 出现 "Hi <用户>! You've successfully authenticated" 即成功
git clone git@github.com:<用户>/projects.git ~/projects
```

### 3. Hermes QQ 配置

**凭据**：追加到 `~/.hermes/.env`（密钥类配置都放这里，非密钥的放 config.yaml）：

```
QQ_APP_ID=1905371061
QQ_CLIENT_SECRET=xxxxxxxx
```

**启用平台**：`~/.hermes/config.yaml` 追加：

```yaml
platforms:
  qqbot:
    enabled: true
    extra:
      dm_policy: allowlist   # 只允许白名单私聊；想临时放开所有人可改 open
```

> `dm_policy: open`（放开私聊）时必须同时设置 `QQ_ALLOW_ALL_USERS=true`（或 `GATEWAY_ALLOW_ALL_USERS=true`），否则 Hermes 会**拒绝启动**（安全设计，见踩坑 4）。

### 4. 启动 Gateway（必须用 systemd）

Gateway 是 Hermes 的常驻后台进程：负责 QQ 长连接 + cron 调度。**不要用 nohup 裸跑**（ssh 断开就死，见踩坑 3）。

```bash
sudo ~/.local/bin/hermes gateway install --system   # 注意：sudo 下必须写全路径
sudo ~/.local/bin/hermes gateway start --system
sudo ~/.local/bin/hermes gateway status --system
```

验证连接：`tail -f ~/.hermes/logs/gateway.log` 应出现 `✓ qqbot connected`。

### 5. 拿到你的 OpenID 并收紧白名单

**OpenID** 是 QQ 官方 API 的隐私匿名 ID：你的 QQ 号对机器人不可见，每条消息的发送者是一个随机串（同一用户对同一机器人永远不变），cron 推送就是靠它定向。

1. 沙盒模式下先到 q.qq.com → 开发设置 → 沙箱配置，把自己的 QQ 加为沙盒成员
2. 在 QQ 给机器人发一条任意消息（如"测试连接"）
3. 服务器日志里抓 OpenID：
   ```bash
   grep "inbound message" ~/.hermes/logs/gateway.log
   # inbound message: platform=qqbot user=08942AFB...612 chat=08942AFB...612
   ```
4. 写入 `.env`（cron 投递目标）+ 收紧白名单：
   ```
   QQBOT_HOME_CHANNEL=[QQ_OPENID_REDACTED]
   ```
   ```yaml
   # config.yaml
   platforms:
     qqbot:
       enabled: true
       extra:
         dm_policy: allowlist
         allow_from:
           - "[QQ_OPENID_REDACTED]"
   ```

### 6. 创建每日 7 点 cron 任务

```bash
hermes cron create "0 7 * * *" "$(cat /tmp/cron_prompt.txt)" \
  --deliver qqbot --workdir /home/fghmnst/projects --name daily-digest
```

- `--deliver qqbot`：agent 的最终回复自动推到 QQ（`QQBOT_HOME_CHANNEL` 指定的你）
- `--workdir`：任务在该目录运行，自动加载仓库的 AGENTS.md
- 完整 prompt 见文末附录，核心指令：`git pull` → 读昨天日志 → 输出小结与待办

验证：

```bash
hermes cron list          # 看 Next run 是否为 07:00 (+08:00)
hermes cron run daily-digest   # 手动触发一次端到端测试
grep "delivered to qqbot" ~/.hermes/logs/agent.log   # 确认投递成功
```

## 踩坑记录（新手必看）

1. **`sudo hermes` 找不到命令**：sudo 用系统 secure_path，不含 `~/.local/bin`。解法：`sudo ~/.local/bin/hermes ...` 写全路径。
2. **cron 时间不对**：服务器默认 UTC（+0），7 点变 15 点。先 `timedatectl set-timezone Asia/Shanghai`。
3. **nohup 起 gateway 一断 ssh 就死**：后台进程挂在 ssh 会话的 cgroup 里，会话关闭即被清理。长驻进程必须走 systemd。
4. **gateway 崩溃循环 `Refusing to start: qqbot has dm_policy set to 'open' but neither GATEWAY_ALLOW_ALL_USERS nor QQ_ALLOW_ALL_USERS is enabled`**：open 策略必须显式 opt-in，否则 Hermes 拒绝启动（安全设计）。要么设 `QQ_ALLOW_ALL_USERS=true`，要么用 allowlist。
5. **无 sudo 重启 systemd 服务**：服务是 `Restart=on-failure`，`pkill -f "hermes_cli.main gateway"` 杀掉进程后 systemd 会自动拉起（~30s），新进程会读到改过的配置。
6. **ssh 非交互 shell 没有 hermes**：PATH 里没有 `~/.local/bin`，脚本里用全路径 `~/.local/bin/hermes`。
7. **本地 `ssh server2` 解析失败**：WSL 与 Windows 的 ssh 配置不互通，WSL 侧要自己写 `~/.ssh/config`（密钥可共用）。
8. **QQ 显示"该机器人未连接服务"**：说明 gateway 没连上（崩了/没起），查 `~/.hermes/logs/gateway.log`，不是 QQ 端问题。

## 日常运维

| 事项 | 说明 |
|------|------|
| 每晚 `git commit` 每日日志 | cron 每次先 `git pull`，不提交就读不到最新日志 |
| 查推送是否成功 | `grep "delivered to qqbot" ~/.hermes/logs/agent.log` |
| 健康检查 | `hermes doctor`；`hermes gateway status --system` |
| QQ 主动消息配额 | 官方对机器人主动推送有限额，某天没收到先查日志 |
| 换 provider | `hermes model`，与部署无关，随时可改 |

## 附：tmux 共享终端（opencode ↔ 用户协作）

**用途**：opencode agent 与用户共用服务器上一个常驻终端——agent 注入命令（send-keys）、用户 attach 实时观看并可随时亲手操作。2026-08-07 部署验证通过。

**架构**：tmux 常驻服务器，会话名 `work`；agent 通过 `ssh server2 'tmux send-keys ...'` 操作，用户 `ssh -t server2 tmux attach -t work` 附着。

**初始化**（服务器重启后重跑）：

```bash
tmux new-session -d -s work -c /home/fghmnst/projects
tmux set-option -t work history-limit 10000
tmux set-option -t work remain-on-exit on
```

**agent 操作模板**：

```bash
ssh server2 'tmux send-keys -t work "git pull; echo __DONE__" Enter'   # 注入命令+哨兵
ssh server2 'tmux capture-pane -t work -p -S -50'                       # 读输出
ssh server2 'tmux respawn-pane -t work'                                 # pane shell 退出后复活
```

**用户操作**：

```bash
ssh -t server2 tmux attach -t work     # 附着观看/交互（-t 必须有）
# Ctrl-b d 脱离（会话不消失）；logout 会让 pane 的 shell 退出，用 respawn-pane 复活
```

**并发锁**（打字前占锁，agent 检测到即停手）：

```bash
ssh server2 'touch ~/.tmux-hold'       # 占锁（打字前）
ssh server2 'test -f ~/.tmux-hold && echo HELD || echo FREE'   # agent 检查
ssh server2 'rm ~/.tmux-hold'          # 释放（打完字）
```

**注意事项**：会话不随断连消失，仅服务器重启丢失（重建见初始化命令）；复杂命令先写脚本 scp 过去再在 tmux 里执行，避免转义问题。

## 附录：daily-digest 任务 prompt（可复现）

```
你是用户的学习助理。当前服务器时区为 Asia/Shanghai。请按以下步骤执行并输出：

1. 先运行 git -C /home/fghmnst/projects pull --quiet 拉取最新提交（若拉取失败直接继续）。
2. 在 /home/fghmnst/projects/obsidian/每日日志/ 目录中，找到「昨天」的日志文件
   （文件名格式 YYYY-MM-DD.md，昨天 = 今天减一天；若不存在则取最近一篇，并在开头注明）。
3. 【昨日小结】：阅读该日志的「今日完成事项」栏目，用 3-5 条要点总结昨天完成的工作
   （保留关键 commit/命令信息）。
4. 【今日待办】：从该日志的「计划/工作流待办」和「疑惑点」栏目提取今天应该做的事项；
   若内容不足，参考 30天学习 Index.md 的学习计划补充 1-2 条建议事项。
5. 最终回复必须使用以下格式：
📅 昨日小结（YYYY-MM-DD）
- ...
📋 今日待办
- ...
```

## 术语

| 术语 | 一句话解释 |
|------|-----------|
| Gateway | Hermes 的常驻后台进程：平台连接器（QQ 等）+ cron 调度器，必须 24h 运行 |
| OpenID | QQ 官方 API 给你的匿名 ID（机器人看不到 QQ 号），用于定向推送和授权 |
| Cron | 定时任务；Hermes 的 cron 由 gateway 每 60 秒 tick 检查触发 |
| systemd | Linux 的服务管理器，保证进程开机自启、崩溃自动拉起 |

相关：[[30天学习 Index]] · [[术语表]] · [[opencode TUI 速查表]]
