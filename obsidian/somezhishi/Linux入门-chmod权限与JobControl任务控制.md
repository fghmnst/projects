---
title: Linux 入门：chmod 权限与 Job Control 任务控制
date: 2026-09-10
tags:
  - linux
  - 学习笔记
---

# Linux 入门：chmod 权限与 Job Control 任务控制

> [!note] 缘起
> 本文整理自一次真实排障经历：给 STM32CubeMX 修复 JRE 执行权限（chmod）、以及处理 Obsidian 日志刷屏终端（Job Control）。示例都来自实际操作场景。

---

## 一、Linux 文件权限基础

### 1.1 三种角色 × 三种权限

| 角色 | 字母 | 含义 |
| --- | --- | --- |
| 属主 | `u` (user) | 文件的所有者 |
| 属组 | `g` (group) | 所属用户组 |
| 其他人 | `o` (others) | 以上两者之外 |

| 权限 | 字母 | 数值 | 含义 |
| --- | --- | --- | --- |
| 读 | `r` | 4 | 查看内容 |
| 写 | `w` | 2 | 修改内容 |
| 执行 | `x` | 1 | 运行/进入目录 |

### 1.2 看懂 `ls -l` 的第一列

```
-rw-r--r-- 1 fgh fgh 12308 ...
```

共 10 个字符，每 3 个一组：

- 第 1 位：类型。`-`=普通文件，`d`=目录，`l`=符号链接
- 第 2~4 位：属主权限（rwx）
- 第 5~7 位：属组权限
- 第 8~10 位：其他人权限

例：`-rw-r--r--` = 属主可读写，组和他人只读 → **不可执行**。

> [!bug] 真实案例
> 用 Windows 解压工具解压 Linux 安装包，会丢失全部可执行权限（`jre/bin/java` 变成 `-rw-r--r--`），导致安装器报错 "Please install Java JRE 17.0.6..."。在 WSL **内部**用 `tar -xzf` 解压则不会丢权限。

### 1.3 chmod 符号模式

```bash
chmod a+x 文件      # 所有人(all)加执行权限
chmod u+x 文件      # 只给属主加执行
chmod -x 文件       # 去掉执行权限
chmod g+w,o-r 文件  # 组加写、他人去读（逗号组合）
```

| 写法 | 谁 | 含义 |
| --- | --- | --- |
| `a` | all | 所有人（默认即 a） |
| `u` / `g` / `o` | 属主/组/其他 | 可组合如 `u+x,g+x` |
| `+` / `-` / `=` | — | 加 / 减 / **直接设定** |

`-R` = 递归，作用到目录内所有层级：

```bash
chmod -R 755 ~/Downloads/xxx/jre
```

### 1.4 chmod 数字模式（推荐掌握）

数值 = 权限相加：`r`=4，`w`=2，`x`=1。

| 数字 | 含义 |
| --- | --- |
| 7 | rwx = 4+2+1 |
| 6 | rw- = 4+2 |
| 5 | r-x = 4+1 |
| 4 | r-- = 4 |
| 0 | --- |

三位数字从左到右 = 属主 / 属组 / 其他人：

```bash
chmod 755 文件   # 属主rwx，组和他人 r-x（程序/脚本惯例）
chmod 644 文件   # 属主rw-，组和他人 r--（普通文件惯例）
chmod 777 文件   # 所有人全权（仅临时/自己机器用）
```

> [!tip] 优化建议
> `chmod -R a+x` 是"追加式"，结果不可预期；`chmod -R 755` 是"整体设定"，对文件和目录都安全，是更严谨的写法。

### 1.5 相关命令速查

```bash
chown 用户名:组名 文件   # 改属主
stat 文件              # 查看权限等元信息详情
umask                  # 查看/设置新建文件的默认权限
ls -l                  # 查看权限
file 文件              # 识别文件真实类型（二进制/脚本…）
```

---

## 二、Job Control（任务控制）

### 2.1 问题根源：前台进程占住终端

前台进程的标准输出/错误（stdout/stderr）连着终端 → 日志刷屏，且**不退出就输不了新命令**。Obsidian 每次启动就打印 Electron 日志，正是如此。

### 2.2 三个按键操作

| 操作 | 信号 | 效果 |
| --- | --- | --- |
| `Ctrl+C` | SIGINT | **杀死**前台进程 |
| `Ctrl+Z` | SIGTSTP | **挂起**（Stopped，暂停但进程活着） |
| 关终端 | SIGHUP | 向子进程发挂断信号，多数进程随之退出 |

> [!warning] Ctrl+Z 之后
> 看到 `[1]+ Stopped` 表示进程只是暂停。继续方式三选一：
> ```bash
> fg        # 回前台跑（又会占终端）
> bg        # 转后台跑（日志仍刷屏）
> kill %1   # 彻底结束
> ```

### 2.3 后台运行 `&`

```bash
obsidian-gui &    # 命令尾部加 &，提示符立即返回
```
- 进程成为 shell 的一个**作业**（job），编号 `[1]`、`[2]`…
- `&` 只解放终端输入，**日志照常打印**

### 2.4 输出重定向：让日志不刷屏

```bash
obsidian-gui > /dev/null 2>&1 &
#        ↑ 标准输出写入…  ↑ 标准错误(2)也指向1号的目标
```

| 写法 | 含义 |
| --- | --- |
| `> 文件` | 标准输出写到文件（覆盖） |
| `>> 文件` | 追加到文件 |
| `/dev/null` | "黑洞"，内容直接丢弃 |
| `2>&1` | 标准错误合并到标准输出 |
| `&> 文件` | 上面两者的简写（bash） |

留日志方便排错：`> ~/obsidian.log 2>&1 &`，出问题 `tail ~/obsidian.log`。

### 2.5 `jobs`：查看作业

```bash
jobs        # [1]+ Running  obsidian-gui
jobs -l     # 附 PID
jobs -p     # 只列 PID
```

状态列：`Running` 运行中 / `Stopped` 被挂起 / `Done` 已结束。

### 2.6 `fg` / `bg` / `kill`：操控作业

```bash
fg          # 最近作业回前台（fg %2 = 指定 2 号作业）
bg          # 挂起的作业转后台继续（bg %1）
kill %1     # 按作业号结束
kill 5678   # 按 PID 结束
pkill -f obsidian   # 按名字模糊匹配结束
```

### 2.7 关终端也不死的三层加固

| 手段 | 作用 |
| --- | --- |
| `nohup cmd &` | 让进程忽略 SIGHUP（no hang up） |
| `cmd &` 后 `disown` | 把作业移出 shell 作业表，shell 退出不再管它 |
| `setsid cmd &` | 进程脱离会话、自成组长——**GUI 应用最彻底** |

最终形态（启动即后台、不刷屏、关终端不死、日志落盘）：

```bash
setsid obsidian-gui > ~/.config/obsidian/gui.log 2>&1 &
```

### 2.8 实操：把命令"自后台化"

与其每次手动加 `&`，不如让启动脚本自己后台化。以 `~/.local/bin/obsidian-gui` 为例：

```bash
#!/bin/bash
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
setsid "$HOME/Downloads/Obsidian-1.13.7.AppImage" --ozone-platform=wayland "$@" > ~/.config/obsidian/gui.log 2>&1 &
```

从此敲 `obsidian-gui` 立即返回提示符。要结束：`pkill -f Obsidian`。

> [!note] 为什么脚本能被终端直接调用？
> 1. 脚本本体在 `~/.local/bin/obsidian-gui`（含 `#!/bin/bash` + `exec`/`setsid` 启动真实程序）
> 2. `.bashrc` 里的 `export PATH="$HOME/.local/bin:$PATH"` 让 shell 找得到这个名字
> 两层缺一不可：PATH 管"能不能找到"，脚本管"找到后干什么"。

---

## 三、kill 与 pkill 详解：给进程发信号

### 3.1 kill 的本质：不是"杀"，而是"发信号"

`kill` 字面是"杀死"，实际功能是**向进程发送一个信号（signal）**。信号是一组预设的通知，进程收到后有三种可能：

1. 按**默认行为**处理——多数终止类信号的默认行为就是结束进程
2. **捕获**信号并自定义处理——例如先保存数据、关闭文件再退出
3. 对少数信号**无法捕获也无法忽略**——最典型的就是 SIGKILL(9) 和 SIGSTOP(19)

所以 `kill` 能杀进程，只是因为默认发送的 SIGTERM 默认行为恰好是终止。

> [!note] 类比
> `kill` 像给进程打电话：`kill -15` 是"请收拾东西下班"（可以商量）；`kill -9` 是直接拉电闸（没有任何反应机会）。

### 3.2 kill 语法与信号的三种写法

```bash
kill PID              # 默认发 SIGTERM(15)：礼貌请求退出
kill -9 PID           # 数字编号：发 9 号信号 SIGKILL，强制杀死
kill -s HUP PID       # 用 -s 指定信号名（最规范）
kill -KILL PID        # 直接写信号名（-SIGKILL 也等价）
kill -l               # 列出全部信号
kill -l 9             # 查询 9 号信号叫什么 → KILL
```

| 写法 | 例子 | 说明 |
| --- | --- | --- |
| `kill PID` | `kill 1234` | 省略信号 = SIGTERM(15) |
| `kill -数字 PID` | `kill -9 1234` | 数字编号，日常最常用 |
| `kill -s 信号 PID` | `kill -s TERM 1234` | 写法最清晰，推荐脚本使用 |
| `kill -信号名 PID` | `kill -HUP 1234` | 简写，`-SIGTERM` 形式也接受 |
| `kill %作业号` | `kill %1` | Job Control 专属，见 2.6 节 |

- 一次可杀多个：`kill -9 1234 5678`
- 默认只能操作自己的进程，杀别人的要加 `sudo`
- `kill` 通常是 shell 内建命令（`type kill` 可验证），所以支持 `%1` 作业号；外部命令 `/bin/kill` 不支持

### 3.3 常用信号速查表

| 编号 | 名称 | 能否被捕获 | 默认行为 | 典型用途 |
| --- | --- | --- | --- | --- |
| 1 | SIGHUP | 能 | 终止 | 终端挂断；常被服务用来**重载配置** |
| 2 | SIGINT | 能 | 终止 | 等价于 `Ctrl+C` |
| 9 | SIGKILL | **不能** | 终止 | 强杀，最后手段 |
| 15 | SIGTERM | 能 | 终止 | **kill 默认**，优雅退出 |
| 18 | SIGCONT | 能 | 继续 | 恢复被暂停的进程 |
| 19 | SIGSTOP | **不能** | 暂停 | 强制暂停（`Ctrl+Z` 的不可拦截版） |
| 20 | SIGTSTP | 能 | 暂停 | 等价于 `Ctrl+Z` |

> [!warning] 编号因系统而异
> 不同 Unix 的信号编号可能不同（如 SIGSTOP 在 macOS 是 17）。脚本里尽量用**名字**（`kill -TERM`），不要写死数字；只有 9 和 15 最通用。

实战常用：

```bash
kill -15 1234   # 先礼：请求进程清理后退出（默认信号，-15 可省略）
kill -9 1234    # 后兵：上一步没反应再用
kill -HUP 1234  # 让服务重读配置（nginx -s reload 底层就是它）
kill -STOP 1234 # 暂停进程；对应 kill -CONT 1234 恢复
kill -0 1234    # 不发信号，只测试进程是否存在（脚本判断用）
```

### 3.4 pkill：按名字批量杀

`pkill` 相当于 **`pgrep` 查找 + `kill` 发送**一步完成：按条件找到一批进程，再统一发信号。

```bash
pkill 模式             # 杀死名字匹配"模式"的进程（默认 SIGTERM）
pkill -9 模式          # 强杀
pkill -f 模式          # 匹配整条命令行，而不只是进程名
```

**匹配规则**：默认只匹配**进程名**（`ps` 中 COMMAND 列的短名，最长 15 字符）；加 `-f` 则匹配**完整命令行**，适合带参数启动的脚本程序。

```bash
pkill obsidian              # 杀所有进程名含 obsidian 的进程
pkill -f "python train.py"  # 杀命令行含该字符串的进程
pkill -u fgh firefox        # 只杀用户 fgh 的 firefox
pkill -HUP nginx            # 给所有 nginx 进程发 HUP 重载配置
```

### 3.5 pkill 常用后缀（选项）

| 选项 | 含义 | 例子 |
| --- | --- | --- |
| `-信号` / `-s 信号` | 指定发送的信号 | `pkill -9 node` |
| `-f` | 匹配完整命令行而非进程名 | `pkill -f "npm run dev"` |
| `-x` | 精确匹配**整个名字**，不模糊 | `pkill -x nginx`（不误伤 nginx-worker） |
| `-i` | 忽略大小写 | `pkill -i firefox` |
| `-u 用户名` | 只匹配该用户的进程 | `pkill -u fgh chrome` |
| `-n` / `-o` | 只选**最新** / **最旧**的那个进程 | `pkill -n node` |
| `-P 父PID` | 只匹配指定父进程的子进程 | `pkill -P 1234` |
| `-t 终端` | 只匹配某终端上的进程 | `pkill -t pts/2` |
| `-e` | 打印被杀的进程名和 PID | `pkill -e node` |
| `-v` | 反向匹配（杀**不**匹配的） | 危险，少用 |

> [!tip] 先预览，再下手
> pkill 是模糊匹配，杀错进程风险高。养成两步习惯：
> ```bash
> pgrep -a -f "模式"   # 先列出会命中的进程（-a 显示完整命令行）
> pkill -f "模式"      # 确认名单无误再杀
> ```
> `pgrep` 与 `pkill` 选项几乎一一对应，只是"只查不杀"；此外 pgrep 还支持 `-c`（只统计数量）、`-l`（列出名字）、`-a`（列出完整命令行）。

### 3.6 kill / pkill / killall 对比

| 命令 | 定位方式 | 适合场景 | 误杀风险 |
| --- | --- | --- | --- |
| `kill` | PID / 作业号 `%n` | 已知 PID，精确操作 | 低（最可控） |
| `pkill` | 名字/命令行**模糊**匹配 | 批量结束同类进程 | 中高 |
| `killall` | 名字**精确**匹配 | 同名进程一次清 | 中 |

### 3.7 为什么有时"杀不掉"？

| 现象 | 原因 | 对策 |
| --- | --- | --- |
| 普通 kill 无效 | 进程捕获了 SIGTERM，正在清理或卡住 | 换 `kill -9` |
| `kill -9` 也无效 | 进程处于 D 状态（不可中断睡眠，如在等磁盘 I/O） | 只能等 I/O 完成或重启 |
| 僵尸进程（Zombie）杀不掉 | 进程已死，只等父进程回收其状态 | 无需处理；结束/重启其父进程即可回收 |
| 提示 "Operation not permitted" | 目标不是自己的进程 | 加 `sudo` 或确认用户名 |

### 3.8 回到最初的问题：PID 是什么

- **PID（Process ID，进程 ID）**：Linux 给每个运行中的进程分配的唯一数字编号，相当于进程的身份证号。查看方式：`ps aux`、`pgrep -a 名字`、`pidof 名字`、`jobs -l`。
- **kill 走"号码"路线**：先查到 PID，再精确发信号 → `kill 1234`，一个号只对应一个进程。
- **pkill 走"名字"路线**：给一个名字/模式，它内部先查出一批 PID，再批量发信号 → `pkill nginx`。
- 特殊 PID：`1` 是 init/systemd，所有进程的祖先；PID 会被系统回收复用，所以操作前最好确认名字对得上。

---

## 四、一句话总结

- **权限**：`ls -l` 看，`chmod 数字|符号` 改，`-R` 递归，数字三位 = u/g/o
- **任务控制**：前台 `Ctrl+C` 杀 / `Ctrl+Z` 挂起，`jobs` 看、`fg`/`bg` 切、`kill %n` 杀
- **后台化**：`&` 起步 → 加 `> 文件 2>&1` 防刷屏 → `setsid` 彻底脱离
- **kill/pkill**：kill 按 PID 精确发信号（默认 15 优雅退出，`-9` 强杀）；pkill 按名字模糊匹配批量杀（`-f` 匹配命令行），杀前先用 `pgrep -a` 预览
- **WSL 解压**：在 WSL 内用 `tar -xzf`，别用 Windows 解压工具（会丢执行权限）
