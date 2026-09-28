---
date: 2026-09-19
course: C语言
---

# 命令行参数：argc 与 argv（新手版）

> [!note] 一句话先行
> 你在终端敲的每个"词"，都会被 shell 打包成一列字符串，经内核放到新程序的栈顶；C 运行时再把它作为参数调用 `main`。`argc` 是"几个词"，`argv` 是"哪些词"——`argv[0]` 是程序名，真正给用户的参数从 `argv[1]` 起。
> 相关：[[课程笔记/C语言/C语言|C语言]] · [[somezhishi/编程基础/Linux重定向-文件描述符与2&1详解|Linux 重定向：文件描述符与 2>&1]] · 延伸：[[somezhishi/项目笔记/计算机系统基础-学习路线与资源对比|内核/ELF/栈补课路线]]

## 一、先建画面：命令行是一张"点菜单"

从前的 main 大概是 `int main(void)`——空手起跑，程序里要什么自己造。但 P1 `note-stats` 要你告诉它"统计哪个目录"，P2 `prob-cli` 要你告诉它"读哪个 CSV、算什么"——这些**启动时临时给的信息**，入口就是 main 的这两个参数。

在终端敲：

```
./note-stats notes/ --tag C
```

回车瞬间，**shell（你敲命令的那个终端程序，bash）先把这一行按空格切成一个个"词"**，捧成一列交给 note-stats：

```
[ "./note-stats" | "notes/" | "--tag" | "C" ]
```

程序里的 main 就是接单的店员，收到两样东西：

| 名字 | 大白话 | 这次的值 |
| --- | --- | --- |
| **argv** | 那一列词本身（argument **vector**，参数"向量"——这里"向量"就是一排） | `["./note-stats", "notes/", "--tag", "C"]` |
| **argc** | 一列里共有几个词（argument **count**，参数个数） | `4` |

所以它俩不神秘：**命令行上敲的每个词，都会"漏"进 main 的参数里。**

## 二、写法与"不用背"的读法

```c
int main(int argc, char *argv[])
{
    ...
}
```

读法：**"main 收两样东西：一个整数 argc（几个词），一排字符串 argv（哪些词）。"**

拆开看 `char *argv[]`：

- `char *` —— 现在理解成"一个字符串"（C 里用指向字符的指针表示一串以 `\0` 结尾的字符）；
- `[]` —— "一排"；
- 合起来：**一排字符串**。`argv[1]` 是第 1 号词，`argv[2]` 第 2 号词……
- 在函数参数里 `char *argv[]` 和 `char **argv` 完全等价，以后见到别慌，是同一件事。

## 三、三条必须知道的规矩

1. **`argv[0]` 是程序自己，不是用户参数。** 它是你敲的程序名（这里 `"./note-stats"`），真正的用户参数从 **`argv[1]`** 开始。所以"用户给没给参数"要判 `argc < 2`，不是 `< 1`。
2. **个数和内容分开**：`argc` 给数量，`argv[1] … argv[argc-1]` 给内容；遍历真实参数用 `for (int i = 1; i < argc; i++)`。
3. **每个词都是字符串**，哪怕长得像数字："42" 是 `'4' '2'`，要算数得用 `atoi(argv[1])` / `strtol` 转换（P2 会用到）。

## 四、参数是怎么到 main 的：shell → 内核 → C 运行时

先纠正一个小直觉：**shell 并没有"直接喊话"给 main**。真正完成传递的是三层接力。以 `./note-stats notes/ --tag C` 为例：

| 步 | 谁 | 干了什么 | 关键点 |
| --- | --- | --- | --- |
| 1 | **shell（bash）** | 处理这一行：变量/通配符先展开 → 按空格切词 → 按 PATH 找到程序 | 得到一列**词**；`argv[0]` 是"你敲的名字"（哪怕程序实际在 `/usr/bin/...`） |
| 2 | shell | `fork()`：克隆一个自己当"跑腿的"，本体留在原地等你结束 | 所以程序跑完还能回到提示符 |
| 3 | 跑腿子进程 | 调用 **`execve(程序路径, argv 数组, envp 数组)`** | **这才是"传递"发生的时刻**；系统调用 = 请求内核办事 |
| 4 | **内核** | "换脑"：把子进程的内存镜像几乎全换成新程序（进程号 PID 不变），并把 `argc`、`argv`、`envp` 摆在新程序**栈顶** | 换了一套大脑，但"订单"已放在桌上 |
| 5 | **C 运行时**（`_start` → `__libc_start_main`） | 从栈顶按约定取出 `argc/argv/envp`，然后调用**你的 `main`** | main 的形参就是在这里喂进来的 |
| 6 | 你的程序 | `return 0` → 运行时 `exit` → 内核记下退出码 → 等在原地的 shell 收进 `$?` | `gcc x.c -o x && ./x` 里的 `&&` 就靠它判断成败 |

一句话版：**shell 拼好一个字符串数组，通过 `execve` 交给内核；内核放在新进程栈顶；C 运行时再把它作为参数调用 main。** 用 Python 的 `subprocess` 或任何父进程直接 `execve` 也能传——shell 只是最常见的调用者，不是必需的。

### 都传了些什么

| 传的东西 | 内容 | 程序里怎么用 |
| --- | --- | --- |
| `argc` | 词的个数（含 argv[0]） | main 形参 |
| `argv` | 一排指针：`argv[0]`＝程序名（调用者放的，原则上可随便填）… `argv[argc]`＝`NULL` 哨兵 | main 形参 |
| `envp`（环境变量） | `PATH=…`、`HOME=…` 这些键值对 | 第三形参 `char *envp[]`（常见扩展）或 `getenv()` / `extern char **environ` |
| 文件描述符 0/1/2… | shell 在 `execve` **之前**摆好，然后继承给新程序 | `printf`/`read`；这就是 [[somezhishi/编程基础/Linux重定向-文件描述符与2&1详解|重定向]] 生效的机理——程序根本不知道被重定向了 |
| 当前工作目录 cwd | 继承 | 相对路径的基准（`./notes` 从哪算起） |
| （冷知识）auxv | 内核附赠的小便签（页大小、随机种子等），给动态链接器和安全设施用 | 一般碰不到 |

> [!note] 两件"没传"的事，反而常被误会
> - shell 变量若不 `export`，**不会**进 envp（`VAR=v ./prog` 可临时加一条）。
> - argv 是内核复制到新进程里的**副本**：在程序里改 `argv[1][0]`，父进程/shell 不受影响。

### 零安装，亲眼看"原始订单"

内核为每个进程维护一份"订单"，在 `/proc/self/cmdline` 里：

```bash
cat -v /proc/self/cmdline; echo
# 输出形如: cat^@-v^@/proc/self/cmdline^@
```

`^@` 是看不见的 `\0`（NUL）。也就是说：**订单就是一堆以 `\0` 分隔的词**——这正是 argv 的字符串排布（指针数组里每个指针指向一个词的开头，数组末尾再放个 `NULL`）。人类可读版：

```bash
strings /proc/self/cmdline      # 每个词一行
strings /proc/self/environ      # 环境变量（终端里通常几十条）
ls -l /proc/self/exe            # 程序"真身"位置，对照 argv[0] 的"名字"
```

### 想看 `execve` 调用本身（可选，需自行安装）

```bash
sudo apt install strace        # 验证: strace -V 能打印版本
strace -e trace=execve /bin/echo hello "two words"
```

预期输出**一行**（地址与 vars 数各机器不同，形状一致）：

```
execve("/bin/echo", ["/bin/echo", "hello", "two words"], 0x7ffd... /* 54 vars */) = 0
```

方括号里就是 argv，`/* 54 vars */` 是 envp 条数，`= 0` 表示成功换脑。**Plan B（不装也行）**：`/proc/self/cmdline` 已经能看到订单的最终形态。

## 五、亲手看一眼（5 行小实验）

```c
#include <stdio.h>

int main(int argc, char *argv[])
{
    for (int i = 0; i < argc; i++)
        printf("argv[%d] = %s\n", i, argv[i]);
    return 0;
}
```

```bash
gcc /tmp/args-demo.c -o /tmp/args-demo
/tmp/args-demo hello "two words"
```

预期三行：

```
argv[0] = /tmp/args-demo
argv[1] = hello
argv[2] = two words
```

观察两点：

- `"two words"` 带引号只算 **1 个**参数（**引号把带空格的词打包**；不加引号会被拆成两个）。
- 单独跑 `/tmp/args-demo`（啥都不带）只会打印 `argv[0]` 一行，这就是 `argc = 1` 的"没带参数"。

## 六、项目里马上就这么用

P1 `note-stats` 的标准开头（"用法提示"套路）：

```c
int main(int argc, char *argv[])
{
    if (argc < 2) {                        /* 用户没给目录 */
        fprintf(stderr, "用法: %s <笔记库目录>\n", argv[0]);
        return 1;                          /* 非 0 = 告诉 shell "没干成" */
    }
    const char *dir = argv[1];             /* 真实参数在这里 */
    /* 接下来打开 dir、开始统计…… */
    return 0;
}
```

- P2 `prob-cli` 的"参数解析"就是它的放大版：`--mean`、`--var` 这类选项逐个 `strcmp` 比对。
- 先记住必踩的坑：**判断字符串相等不能写 `argv[i] == "--tag"`**（`==` 比的是地址，不是内容），要写 `strcmp(argv[i], "--tag") == 0`。

## 七、走查实例：`./note-stats 123 321` 从回车到输出

现在这版代码长这样（`C-tools/note-stats/note-stats.c`）：

```c
int main(int argc, char *argv[])
{
    printf("argc: %d\n", argc);            /* 第 5 行 */
    for (int i = 0; i < argc; i++) {       /* 第 7-9 行 */
        printf("argv[%d]: %s\n", i, argv[i]);
    }
    return 0;                              /* 第 10 行 */
}
```

实测输出：

```
argc: 3
argv[0]: ./note-stats
argv[1]: 123
argv[2]: 321
```

### 订单在内存里长什么样

```
argc = 3
argv ─┬─► [0] ──► "./note-stats\0"
      ├─► [1] ──► "123\0"
      ├─► [2] ──► "321\0"
      └─► [3] ──► NULL          ← 标准保证的"到此为止"标志
envp ──► [0] ──► "PATH=..."    …
```

`argv` 是一排指针（格子里放"字符串开头的地址"），字符串本体也在栈上；`argv[i]` 取第 i 个指针，`%s` 顺指针打印到 `\0`。第 0 格固定被"你敲的程序名"占了——这就是它出现在输出第一行的原因。把第四节的接力表代入本例：步骤 1 的词列表就是 `["./note-stats", "123", "321"]`，步骤 5 的 `call main` 里 `argc = 3`。

### main 里逐行发生了什么

| 执行到 | 代码 | 发生了什么 | 屏幕出现 |
| --- | --- | --- | --- |
| 第 5 行 | `printf("argc: %d\n", argc)` | `%d` 把 int `3` 转成字符 `'3'`，写到 stdout（终端是行缓冲，遇 `\n` 立即刷出） | `argc: 3` |
| i=0 | `printf("argv[%d]: %s\n", 0, argv[0])` | `argv[0]` 指向 `"./note-stats"`；`%s` 逐字符打印到 `\0` | `argv[0]: ./note-stats` |
| i=1 | argv[1] → `"123"` | `"123"` 是**字符串**不是数字，原样照打 | `argv[1]: 123` |
| i=2 | argv[2] → `"321"` | 同上 | `argv[2]: 321` |
| i=3 | `3 < 3` 为假 | 循环结束（`argv[3]` 其实是内核放的 `NULL` 哨兵，但循环没走到它） | — |
| 第 10 行 | `return 0` | 运行时 `exit(0)` → 内核记录退出码 → bash 收进 `$?` | — |

### 为什么输出"这样"：三个决定因素

1. **`argc = 3`**：切出了 3 个词（程序名也算）。规律：`argc = 1 + 用户参数个数`。
2. **顺序**：`argv` 顺序 = 命令行词序，循环 0→2 照序打印。
3. **原样**：程序只"念"不"算"，所以 `123` 怎么看都像数字也不会变。

| 命令 | argc | argv[1] | 原因 |
| --- | --- | --- | --- |
| `./note-stats` | 1 | （没有） | 无用户参数 |
| `./note-stats 123 321` | 3 | `123` | 空格把两个词分家 |
| `./note-stats "123 321"` | 2 | `123 321` | **引号打包**，空格不再是分隔符 |
| `./note-stats 123 321 456` | 4 | `123` | 多给就多收，程序照单全收 |

### 自己验证（都只读）

```bash
./note-stats 123 321; echo "退出码: $?"   # 实测: 退出码 0
file note-stats                           # 实测: ELF 64-bit … dynamically linked
strings note-stats | grep argc            # 实测: 能看到 "argc: %d"、"argv[%d]: %s"
```

最后一条挺有意思：printf 的模板字符串在**编译时**就存进了可执行文件（`.rodata` 只读区），运行时直接取用——不运行程序也能从文件里"看到"它。

## 术语小词典

| 词 | 大白话 |
| --- | --- |
| argc | argument count，参数个数：命令行被切成几个词 |
| argv | argument vector，参数向量：装这些词的"一排字符串" |
| vector | 在这里就是"一排 / 一列"，不是数学向量 |
| 字符串（`char *`） | 一串以 `\0` 结尾的字符，`printf` 的 `%s` 认识它 |
| shell 切词 | bash 按空格把命令行拆成词再交给程序；引号能打包空格 |
| `strcmp` | 比较两个字符串**内容**的函数，相同返回 0 |
| 系统调用（syscall） | 程序请求内核办事的正式接口，如 `execve` |
| `fork` | 克隆当前进程；shell 用它保住自己再派跑腿的 |
| `execve` | "换脑"系统调用：装入新程序，顺便把 argv/envp 交过去 |
| 内核 | 操作系统核心；把参数摆到新进程栈上的正是它 |
| C 运行时 / `_start` | 程序入口处的启动代码，负责取出 argc/argv 再调用 main |
| `envp` / `environ` | 环境变量列表（继承来的键值对），`getenv` 可查 |
| cwd | 当前工作目录，相对路径的起算点 |
| `$?` | shell 收到的上一个程序退出码 |
| ELF | Linux 可执行文件的格式；内核靠它知道怎么装载程序 |
| 动态链接器 | 程序启动前先跑的一小段，负责把 printf 等库函数接进来 |
| 栈 | 进程内存里放临时数据的区域；启动参数就摆在这 |
| `.rodata` | 只读数据段，字符串常量（如格式串）住在这里 |
| 行缓冲 | 终端模式下 stdout 遇 `\n` 就立刻输出，所以顺序实时可见 |

## 自测

> [!question]- 想好再展开
> 1. 敲 `./note-stats notes --tag C` 后，`argc` 是几？`argv[2]` 是什么？
>    答：argc = 4（程序名 + 3 个词）；argv[2] = `"--tag"`。
> 2. 为什么"没给参数"判 `argc < 2`，不是 `argc < 1`？
>    答：argv[0] 被程序名占了，用户参数从 argv[1] 起；argc=1 就是零个用户参数。
> 3. `argv[1][0]`（设 argv[1] 为 `"--tag"`）取到什么？
>    答：`'-'`。第一层 `[1]` 取第 1 号词，第二层 `[0]` 取该词的第 0 个字符。
> 4. 是 shell 把 argv 直接"塞"给 main 的吗？
>    答：不是。shell 拼好数组交给 `execve`，内核放到新进程栈顶，C 运行时（`_start`）再取出来调用 main。
> 5. 为什么重定向对程序内部是"隐形"的？
>    答：shell 在 `execve` 之前就改了 fd 1/2 的指向，程序拿到的仍是 fd 1，只是它的去向变了。
> 6. 环境变量和命令行参数一句话区别？
>    答：argv 是"这一行命令里敲的词"；env 是从父进程继承的键值对，`VAR=v ./prog` 可临时加一条。
> 7. 同样程序，命令换成 `./note-stats "123 321"`，argc 和 argv 变成什么？
>    答：argc=2；argv[1]=`123 321`（引号打包成一个词）。
