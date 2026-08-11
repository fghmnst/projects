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

## 关联

- [[TIL/Obsidian AppImage 依赖缺失|Obsidian AppImage 依赖缺失]]（同主题另一坑：缺系统库）
- [[30天学习 Index]] · [[术语表/术语表|术语表]]
