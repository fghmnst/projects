powershell中 wsl --shut down 即可
# 坑：Obsidian GUI 启动失败（obsidian-gui 不出窗口）

**日期**：2026-08-11
**场景**：WSL2 Ubuntu-24.04 + WSLg，Obsidian Linux AppImage（`~/bin/Obsidian.AppImage`，Obsidian 1.13.6）。

## 现象

- 终端输入 `obsidian-gui`，只见 `[WARN:COPY MODE]`，GUI 不弹出
- 反复尝试：任务栏出现 Obsidian 图标，但点击窗口不可见（或完全无窗口）
- `/tmp/obsidian.log` 里有 `App is up to date.` 字样

## 根因（两层叠加，与 Obsidian 自身无关）

### 层 1：后台作业被终端作业控制挂起（进程 T 态）
旧 alias `APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage &` 用 `&` 后台运行，但 **stdout/stderr 仍挂在终端上**。AppImage 是后台作业却尝试与终端交互 → 被作业控制信号挂起，进程停在 **T 态**（`wchan=do_signal_stop`），GUI 初始化前就被冻结。
- 诊断：`ps -o pid,stat,cmd -p <pid>` 看 STAT 是不是 `T`；`cat /proc/<pid>/wchan` 见 `do_signal_stop`
- 伴随症状：`~/.config/obsidian/` 残留 `SingletonLock/SingletonCookie/SingletonSocket`（指向已无进程的 socket），不清掉则新实例启动报"已在运行"

### 层 2：WSLg 会话的 RDP 渲染通道损坏（任务栏有图标但窗口不可见）
WSL 本次启动时（09:10）WSLg 打开 RDP 共享内存失败：
```
/mnt/wslg/weston.log: rdp_allocate_shared_memory: Failed to open "/mnt/shared_memory/{...}" with error: Input/output error
```
后果：窗口在 X 服务器侧**完全正常**（`xwininfo` 可见 1046x804 已映射），weston 也把窗口注册进 RDP rail（任务栏出现图标），但**帧缓冲传不到 Windows 桌面**，窗口永远不可见。
- 诊断顺序：① `xwininfo -root -tree` 确认 X 侧窗口存在 → ② `grep -E "shared_memory|ClientGetAppidReq" /mnt/wslg/weston.log` 看渲染通道是否建好

### 两个"疑似元凶"实为良性（不是故障原因）
- **`[WARN:COPY MODE]`**：AppImage runtime 提示，表示"解压到 /tmp 再运行"而非 FUSE 挂载（alias 强制 `APPIMAGE_EXTRACT_AND_RUN=1`），正常现象
- **`App is up to date.`**：AppImage 启动器每次启动的更新检查输出（加载 asar → 查 GitHub → 报已最新），正常现象

## 解决

### 1. 清理被挂起的实例与残留锁
```bash
kill <T态PID>            # ps aux | grep -i obsidian 找 PID；杀不掉再 kill -9
rm -f ~/.config/obsidian/SingletonLock ~/.config/obsidian/SingletonCookie ~/.config/obsidian/SingletonSocket
rm -rf /tmp/scoped_dir*   # SingletonSocket 指向的临时目录（若存在）
```

### 2. alias 加固（根治层 1）
`~/.bashrc` 第 125 行改为：
```bash
alias obsidian-gui='nohup env APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage >/tmp/obsidian.log 2>&1 &'
```
要点：`nohup` 脱离终端（不再受作业控制信号影响）+ 输出重定向（日志落 `/tmp/obsidian.log`，不占终端）。改完 `source ~/.bashrc`。

### 3. WSLg 渲染通道损坏 → 重启 WSL（根治层 2）
**Windows 侧**（PowerShell/CMD）执行：
```
wsl --shutdown
```
等 5 秒重新打开 WSL 终端（自动重启 WSLg，重建共享内存），再跑 `obsidian-gui`。
⚠️ 会杀掉所有 WSL 进程（opencode 会话、VS Code Remote-WSL 断开，重开即可），无数据风险。

### 4. 启动后自检
```bash
sleep 8 && ps -o pid,stat,cmd -p $(pgrep -f "AppImage" | head -1)   # 期望 S/Sl 态（不是 T）
xwininfo -root -tree | grep -i obsidian                             # 期望见映射窗口
tail -3 /tmp/obsidian.log                                           # 期望无异常
```

## obsidian-gui 具体实现方法（输入即可打开 GUI）

1. 确认 AppImage 存在：`ls -la ~/bin/Obsidian.AppImage`
2. 把加固 alias 写入 `~/.bashrc` 末尾：
   ```bash
   echo 'alias obsidian-gui='"'"'nohup env APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage >/tmp/obsidian.log 2>&1 &'"'"'' >> ~/.bashrc
   ```
3. 生效：`source ~/.bashrc`（新开终端自动生效）
4. 使用：任意终端输入 `obsidian-gui` 回车，GUI 数秒内弹出
5. 若 GUI 不出：按上文「解决」3 步排查（T 态 → 锁 → WSLg）

### 补充：每个命令行与涉及的文件详解

#### 涉及的文件（4 个）

| 文件 | 角色 |
|---|---|
| `~/bin/Obsidian.AppImage` | 启动的目标程序：官方 Obsidian Linux 版 AppImage（约 136MB 单文件 ELF，内含 Electron 运行时 + Obsidian 本体 + CLI）。`~` = `/home/fgh`。需有执行权限（`-rwxr-xr-x`，含 `x`） |
| `~/.bashrc` | bash 配置文件。**每个新终端启动时自动读取**，alias 写在这里才能"任何终端都有效"。仅交互式 shell 读取（脚本/非交互 shell 不读——这也是排查时自动化 shell 里报 command not found 的原因） |
| `/tmp/obsidian.log` | 启动日志：alias 把 stdout/stderr 都重定向到这里（`>` 覆盖写，每次启动重新生成）。`/tmp` 重启即清，排障时 `tail -3` 查异常；`App is up to date.` 就在这里 |
| `/tmp/appimage_extracted_*` | 运行时解压目录（AppImage 启动自动生成到 /tmp，重启 WSL 后清空），无需手动管理 |

#### 每个命令行

1. **`ls -la ~/bin/Obsidian.AppImage`** —— 验证文件存在 + 有执行权限，无副作用。
2. **`echo 'alias obsidian-gui='"'"'...'"'"'' >> ~/.bashrc`** —— 把 alias 追加进配置：
   - `echo '文本'`：打印文本；**引号拼接**：单引号内无法直接写 `'`，用 `'"'"'` 三段式（`'` 结束当前串 + `"'"` 双引号包单引号字符 + `'` 重新开串），把两段拼成完整一行 alias
   - `>>`：**追加**（两个 `>`，不覆盖已有内容；误用单个 `>` 会清空整个 .bashrc）
   - 等效做法：`nano ~/.bashrc` 手动加同一行
   - 最终写入的内容就是第 2 步加固 alias 那一行
3. **`source ~/.bashrc`** —— 当前终端立即重读配置，alias 马上生效，无需重开终端。
4. **`obsidian-gui`** —— 输入后 shell 把 alias 展开成完整命令，以 `&` 后台启动，立即返回提示符，GUI 数秒内弹出。

#### alias 命令本身每个部分的作用

```bash
nohup env APPIMAGE_EXTRACT_AND_RUN=1 ~/bin/Obsidian.AppImage >/tmp/obsidian.log 2>&1 &
```

| 部分 | 作用 | 缺了会怎样 |
|---|---|---|
| `nohup` | 忽略 SIGHUP（终端关闭不杀进程）+ 脱离终端作业控制 | 今天元凶：`&` 后台但不脱离终端 → 被作业控制挂起（T 态、GUI 冻结） |
| `env APPIMAGE_EXTRACT_AND_RUN=1` | 强制 AppImage 走解压模式（WSL 无 libfuse2，挂载模式跑不了） | 报 FUSE 错误起不来 |
| `~/bin/Obsidian.AppImage` | 程序本体 | — |
| `> /tmp/obsidian.log` | 标准输出重定向到日志 | 输出喷终端 + 后台作业写终端有被挂起风险 |
| `2>&1` | 标准错误并入同一日志 | 报错污染终端（同样有挂起风险） |
| `&` | 后台运行，立即还提示符 | 前台占终端 5-10 秒，关终端进程即死 |

**为什么这组合最稳**：`&`（后台）+ `nohup`（脱离作业控制）+ 重定向（不与终端交互）= 不占终端、不受终端关闭/作业控制信号影响、报错有日志可查——把本次故障的两个根因（T 态挂起、无法观察日志）全部堵死。

#### 为什么不直接做脚本/符号链接

alias 是 bash 特性，展开后等价于亲手输入该命令，环境变量继承最干净；脚本也可行但多一层封装。唯一限制：只在交互式终端可用（这正是预期场景——"输入命令即开 GUI"）。

## 关联

- [[TIL/Obsidian AppImage 依赖缺失|Obsidian AppImage 依赖缺失]]（同主题另一坑：缺系统库）
- [[30天学习 Index]] · [[术语表/术语表|术语表]]
