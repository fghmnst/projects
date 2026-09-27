---
date: 2026-09-26
course: C语言
---

# 目录遍历与递归：note-stats 步骤 2 详解（新手版）

> [!note] 一句话先行
> 递归遍历目录只有一句话：**遇到子目录，就把"遍历一个目录"这件事原样外包给同一个函数自己**。落地靠三件套 `opendir` / `readdir` / `closedir`，加上两个必须练成肌肉记忆的写法——`while ((entry = readdir(dir)) != NULL)`（每轮重新抽牌）和 `snprintf(child, sizeof child, "%s/%s", ...)`（自己拼路径，**斜杠要自己写**）。
> 相关：[[课程笔记/C语言/C语言|C语言]] · [[课程笔记/C语言/文件操作背后的系统概念-五个直觉|文件操作背后的系统概念：五个直觉]] · [[课程笔记/C语言/P1-note-stats-实现大纲|P1 note-stats 实现大纲]] · [[课程笔记/C语言/命令行参数-argc与argv入门|命令行参数]] · [[课程笔记/C语言/标准错误流-fprintf与stderr详解|标准错误流]]

> [!warning] 本篇的靶心
> 初稿 `note-stats.c`（commit `73d84c6`）里有两处自标「没看懂」——循环的 while 和 snprintf 那两行，而且它们各藏一个 bug（第三节与第四节各拆一个）。看完这两节，再读标准答案（第八节）就顺了。

## 〇、先建画面：一叠牌 + 无数次"外包"

**递归的直觉**：目录树像一串俄罗斯套娃——拆开一层，里面可能又是一个套娃。你不需要为"第二层、第三层"写新代码：碰到子目录时，把 `scan_dir` **再喊一遍**，只把参数换成正面对的路径。

两个关键点：

- **每层调用各有家当**：`dir` 把手、`entry`、拼好的 `child` 缓冲区，都住在各自调用栈的"栈帧"里，互不干扰（机制见[[课程笔记/C语言/文件操作背后的系统概念-五个直觉|五个直觉]]第三节）。递归返回后，外层循环从"下一张牌"继续，不需要任何手动记账。
- **停止条件天然存在**：`readdir` 把牌抽完会返回 `NULL`，循环自然结束、函数返回。所以 P1 不用写"没有子目录就停"，也完全不用 `malloc`。

## 一、三件套：opendir / readdir / closedir

| 函数 / 字段 | 原型速记 | 干什么 | 坑 |
| --- | --- | --- | --- |
| `opendir` | `DIR *opendir(const char *name)` | 打开目录流，拿到"一叠牌的把手" | 失败返回 `NULL`；返回类型是 **`DIR *`**，不是 `int *`；头文件 `<dirent.h>` |
| `readdir` | `struct dirent *readdir(DIR *d)` | 抽下一张牌 | 参数是**把手**不是路径；抽完返回 `NULL`；返回的指针指向 libc 内部缓冲，**下次调用会覆盖**，要留名字立刻拷走 |
| `closedir` | `int closedir(DIR *d)` | 收牌 | 每个成功的 `opendir` 必须配一次；忘了 = 句柄泄漏 |
| `entry->d_name` | `char[256]` 字段 | 牌上的名字 | **只有文件名，没有路径** |

## 二、`struct dirent *entry;` 是什么：准备一把镊子

拆成两半读：**牌的类型 + 夹牌的镊子**。

- `struct dirent` 是 `<dirent.h>` 里定义好的结构体类型（目录条目，directory entry）。结构体 = 把几个数据打包成一张"有栏目的档案卡"；这张卡的栏目有 `d_name`（名字，你唯一要用的）、`d_type`、`d_ino` 等。
- `entry` 是变量名。
- `*` 表示它是**指针**——格子里装的是"一张牌的地址"，不是牌本身。

所以整行的意思是：**准备一把镊子 `entry`，用来夹住 `readdir` 递过来的每一张牌（的地址）**。声明时只留了一个放地址的格子（8 字节），并没有造牌。

```
struct dirent *entry;                  ← 只有镊子

readdir(dir) 递牌 ──► [ d_name:"每日日志" | d_type:… ]   ← 牌躺在 libc 的桌上
                            ▲
entry ──────────────────────┘           ← 镊子指向当前这张

entry->d_name  ≡  (*entry).d_name       ← "走到牌前，看名字栏"
```

两个顺带：`->` 是语法糖（等价于 `(*entry).d_name`）；桌上只有**一张**公共牌，下一张会盖掉旧的，所以名字要留就当场 `snprintf` 拷进 `child`。

## 三、`while ((entry = readdir(dir)) != NULL)`：每轮都要重新抽牌

这行有三个知识点叠在一起，逐个拆：

1. **赋值表达式本身有值**：`entry = readdir(dir)` 这个表达式的值就是"刚抽到的指针"（抽完是 `NULL`），所以能直接当条件用。
2. **每轮条件求值都会执行一次 `readdir`**，保证每轮拿到的都是新牌。
3. **外层多的一对括号**是为了消掉 `=` 和 `==` 混淆的编译警告（`-Wall` 会提示）。

等价展开：

```
抽牌 → entry 非空？ → 是：进入循环体 → … → 回到"抽牌"
                    → 否：循环结束，去 closedir
```

### 反例：初稿的死循环（重点）

初稿写成了"只抽一张 + while 判断指针"：

```c
struct dirent *entry = readdir(dir);   // 只抽了一张牌
while (entry != NULL)                  // 判断的还是这张旧牌
{
    if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
    {
        continue;                      // 跳回条件 → entry 没变 → 原地空转
    }
    ...
}
```

- **现象**：程序卡住不返回。如果第一张恰好是 `.` 或 `..`，连一行输出都没有（实测 `timeout 3 ./note-stats ...` 直接超时，`rc=124`）。
- **为什么 `continue` 不救命**：`continue` 只跳本轮余下代码，回到条件重新判断；而 `entry` 还是那张旧牌，`readdir` 压根没被再调用。**抽牌动作不在循环里，永远抽不到下一张。**
- **修法**：把抽牌写回条件里（标准写法）；或在循环体最后补一句 `entry = readdir(dir);`（不推荐——多一条"每轮都要记得执行"的心账，容易漏）。

一句话记牢：**抽牌必须发生在"每轮都会执行到"的位置。**

## 四、`snprintf` 拼路径：斜杠是拼的人的责任

`readdir` 只给名字（`d_name`），而 `stat`、递归、打印全都要**完整路径**。C 里没有 `dir + "/" + name` 这种写法，用 `snprintf` 拼：

```c
char child[1024];
int n = snprintf(child, sizeof child, "%s/%s", dirpath, entry->d_name);
if (n < 0 || (size_t)n >= sizeof child)
{
    fprintf(stderr, "路径过长，跳过：%s/%s\n", dirpath, entry->d_name);
    continue;
}
```

三个要点：

1. **格式串 `"%s/%s"` 里的 `/` 要自己写**。初稿写的是 `"%s%s"`，拼出来是 `../../obsidian课程表.md`——目录和文件名粘在一起，`stat` 全部找不到、逐个报错。函数不会好心替你补分隔符：**拼接者对格式负责**。
2. **返回值是"本来想写多长"**（不含结尾 `\0`），不是"实际写了多少"。`n >= sizeof child` 说明被截断、这半截路径不能用，宁可跳过。
3. **`sizeof child` 比手写 1024 稳**：缓冲区大小改了，这里不用跟着改。

## 五、循环里的五个小决策

```
while ((entry = readdir(dir)) != NULL)
{
    ① 是 "." 或 ".."？ → continue（防无限套娃）
    ② snprintf 拼出完整路径 child（第四节；截断就跳过）
    ③ stat(child, &st) 失败？ → perror(child) + continue（坏条目不能毁全盘）
    ④ 是目录 → scan_dir(child) 递归；是普通文件且以 .md 结尾 → printf
    ⑤ 后缀判断 has_md_suffix(name)：只比末尾 3 个字符
}
```

- **① 为什么必须跳过 `.` 和 `..`**：每本"通讯录"都有这两行固定条目（`.` 是自己、`..` 是上级），不跳的话 `..` 会把遍历带回上一级 → 无限套娃（详见 [[课程笔记/C语言/文件操作背后的系统概念-五个直觉|五个直觉]]）。
- **③ stat 查档案**：`struct stat st; if (stat(child, &st) != 0) { perror(child); continue; }`。用 `stat` 而不是 `entry->d_type`：`d_type` 在部分文件系统会返回"不知道"，`stat` 永远可靠。
- **④ 分岔**：`S_ISDIR(st.st_mode)` → `scan_dir(child)`（注意传完整路径 `child`，不是 `d_name`！）；`S_ISREG(st.st_mode) && has_md_suffix(entry->d_name)` → 打印。
- **⑤ 后缀判断**：

```c
static int has_md_suffix(const char *name)
{
    size_t len = strlen(name);
    return len >= 3 && strcmp(name + len - 3, ".md") == 0;
}
```

`name + len - 3` 是指针算术：从首地址往后跳 `len-3` 格，正好落在最后 3 个字符上；`len < 3` 时 `&&` 短路，避免越界读。**不要用 `strstr`**——`a.md.txt` 会被误判成 md 文件。

## 六、perror 小抄

`perror(msg)` = 把内核留下的错误编号（`errno`）翻译成人话，拼上你的标签打到 **stderr**：

| 写法 | 实际输出 | 读者能知道什么 |
| --- | --- | --- |
| `fprintf(stderr, "dir = NULL\n")` | `dir = NULL` | 只知道"失败了" |
| `perror("opendir")` | `opendir: No such file or directory` | 谁失败 + 为什么 |
| `perror(argv[1])` / `perror(dirpath)` | `/no/such/dir: No such file or directory` | **哪个对象**失败 + 为什么 |

- **位置敏感**：`errno` 记的是"最近一次失败"，必须在失败现场**紧接着**调用，中间别夹别的可能失败的操作；
- 它会自动补 `: ` 和换行，标签里不用自己写冒号；
- 「结果走 stdout、诊断走 stderr」的分工见 [[课程笔记/C语言/标准错误流-fprintf与stderr详解|标准错误流笔记]]。

## 七、调用栈走一遍

拿真实结构举例：

```
scan_dir("../../obsidian")
 ├─ 抽出 "课程笔记"（目录）→ scan_dir("../../obsidian/课程笔记")
 │    ├─ 抽出 "C语言" → scan_dir(".../课程笔记/C语言")
 │    │    └─ 抽出 "make入门....md" → printf 路径；抽完 → 返回
 │    └─ 抽完 → 返回
 ├─ 抽出 "每日日志" → scan_dir(...)
 └─ 抽完 → 返回 main
```

外层 `scan_dir("../../obsidian")` 等"课程笔记"这一支整个走完才继续抽下一张牌——深度优先，像剥洋葱一圈圈往里。

## 八、标准答案（带注释）

```c
#include <stdio.h>       // printf / fprintf / perror / snprintf 的声明
#include <dirent.h>      // opendir / readdir / closedir / struct dirent
#include <string.h>      // strlen / strcmp
#include <sys/stat.h>    // stat / struct stat / S_ISDIR / S_ISREG

// 判断文件名是否以 ".md" 结尾。返回 1=是，0=否
// static：只在本文件内可见——单文件程序里的好习惯
static int has_md_suffix(const char *name)
{
    size_t len = strlen(name);
    return len >= 3 && strcmp(name + len - 3, ".md") == 0;
}

// 递归遍历 dirpath，把所有 .md 文件路径打印到 stdout
// 返回值：0 = 成功；1 = 本层目录打不开（顶层调用者拿它当退出码）
static int scan_dir(const char *dirpath)
{
    DIR *dir = opendir(dirpath);  // "开班"：借一张目录号牌
    if (dir == NULL)
    {
        perror(dirpath);          // "路径: 内核给的原因" → stderr
        return 1;
    }

    struct dirent *entry;  // "镊子"
    while ((entry = readdir(dir)) != NULL)  // 每轮重新抽牌，抽完为 NULL
    {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
        {
            continue;  // 跳过自己与上级，防无限套娃
        }

        char child[1024];  // 栈上缓冲；本仓库最长路径百字节量级
        int n = snprintf(child, sizeof child, "%s/%s", dirpath, entry->d_name);
        if (n < 0 || (size_t)n >= sizeof child)
        {
            fprintf(stderr, "路径过长，跳过：%s/%s\n", dirpath, entry->d_name);
            continue;  // 截断的半截路径不能用
        }

        struct stat st;
        if (stat(child, &st) != 0)  // 查档案：类型 / 大小 / 修改时间
        {
            perror(child);  // 一个坏条目不该毁掉整次遍历
            continue;
        }

        if (S_ISDIR(st.st_mode))
        {
            scan_dir(child);  // 递归：同一个我，换正面对的路径
                              // 返回值故意忽略：子目录失败内部已 perror
        }
        else if (S_ISREG(st.st_mode) && has_md_suffix(entry->d_name))
        {
            printf("%s\n", child);  // 一行一个路径，方便 | wc -l 对账
        }
    }

    closedir(dir);  // "收班"：还牌。只借不还 = 句柄泄漏
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        fprintf(stderr, "用法：note-stats <目录>\n");
        return 1;
    }

    return scan_dir(argv[1]);  // 顶层打不开 → 退出码 1
}
```

三处最值得记住：`while ((entry = readdir(dir)) != NULL)`（每轮重抽）；错误处理分两档（**目录**打不开 → `perror` + `return`；**条目/文件**出问题 → `perror` + `continue`）；`closedir` 放在函数末尾（唯一提前返回是 `opendir` 失败——那时还没开班、无需收）。

## 九、初稿对照修正表

对照 commit `73d84c6` 的初稿：

| 处 | 初稿写法 | 问题 | 改法 |
| --- | --- | --- | --- |
| 抽牌 | `entry = readdir(dir)` 放在循环外一次 | 每轮条件只判断旧指针 → `continue` 后空转死循环（第三节） | 写回条件：`while ((entry = readdir(dir)) != NULL)` |
| 拼路径 | `snprintf(..., "%s%s", dirpath, entry->d_name)` | 缺 `/`，拼出"目录名文件名"粘连路径（第四节） | 改成 `"%s/%s"` |
| 报错行 | 路径过长的 `fprintf` 少了结尾 `\n` | 下一条错误会接在同一行 | 补 `\n` |

初稿其余部分——`DIR *` 类型、`perror(dirpath)`、`closedir`、返回 `int` 的分档——都已经写对了。

## 十、调试顺序与验收

**调试顺序（省命）**：

1. 先临时打印**所有**条目（含目录，不过滤）：确认覆盖全树、没有死循环；
2. 换小目录试（如 `../../obsidian/周复盘`，3 个文件）；
3. 再套 `.md` 过滤，最后上全库。

**六步验收**（2026-09-26 实测基准；数字随日志增长，**同刻**对账）：

```bash
make clean && make                                  # 编译通过，零 warning
./note-stats; echo "exit=$?"                        # stderr 用法提示；exit=1
./note-stats /不存在的目录; echo "exit=$?"            # 该路径: No such file or directory；exit=1
./note-stats ../../obsidian/周复盘                    # 3 行
./note-stats ../../obsidian | wc -l                 # 122（对账：find ../../obsidian -name '*.md' | wc -l）
./note-stats ../../obsidian >/dev/null; echo "exit=$?"   # exit=0，无 stderr 输出
```

坑速查：行数 0 → 过滤写反 / `has_md_suffix` 恒假；飞快刷屏或卡死 → `.`/`..` 没跳、或抽牌没更新；行数偏少 → 少拼了 `dirpath` 前缀；`implicit declaration` → 缺 `<sys/stat.h>` / `<string.h>`；段错误 → `DIR *` 类型或 `readdir` 参数写错。

## 术语小词典

| 词 | 大白话 |
| --- | --- |
| 目录流（`DIR *`） | 一叠牌的把手；`opendir` 打开、`readdir` 抽牌、`closedir` 收牌 |
| `struct dirent` | "一张牌"的类型：名字 `d_name` + 类型等栏目 |
| `->` | 顺着指针走到结构体，取某个栏目：`entry->d_name` ≡ `(*entry).d_name` |
| 递归 | 函数自己叫自己；遇子目录就"同一个我再跑一遍" |
| 栈帧 | 每次函数调用叠出的一层格子，放局部变量；返回时整层撕掉 |
| `snprintf` | 安全拼接：最多写 n-1 字符 + `\0`；返回"本来想写多长" |
| 截断 | 拼接结果超过缓冲区，后半截被丢弃；返回值 `>= 缓冲区大小` 即在报信 |
| `stat` / 档案 | 查路径的元信息：是目录还是文件、多大、何时改 |
| `S_ISDIR` / `S_ISREG` | 读档案"类型栏"的宏：是目录吗 / 是普通文件吗 |
| `perror` / `errno` | 把内核的错误编号翻译成人话打印到 stderr |
| 指针算术 | 指针加减整数 = 在地址上前后跳格；`name + len - 3` 落在末尾 3 字符 |
| 句柄泄漏 | 借了牌不还；牌桌借光后 `opendir` 开始返回 NULL |

## 自测

> [!question]- 先自己答，再展开
> 1. `while ((entry = readdir(dir)) != NULL)` 里外层括号为什么不能省？
>    答：省了会被编译器警告 `=` 与 `==` 混淆（`-Wall` 提示）；括号明确"这是赋值表达式当条件"。
> 2. 如果把 `readdir` 放到循环外（像初稿那样），程序会怎样？
>    答：`entry` 永远是同一张旧牌。遇到 `.`/`..` 时 `continue` 回到条件，还是同一个非 NULL 指针 → 原地空转（死循环，表现为卡死不返回）。
> 3. `"%s%s"` 拼路径为什么全盘 `stat` 失败？
>    答：缺分隔符，拼出来是"目录名+文件名"粘连的路径，不存在；`snprintf` 不会替你加 `/`。
> 4. `snprintf` 的返回值为什么是"本来想写多长"而不是"实际写了多长"？
>    答：这样调用者能判断是否截断——返回值 ≥ 缓冲区大小就说明没写完，这种半截路径必须丢弃。
> 5. `readdir` 已经给了 `d_name`，为什么还要 `snprintf` 拼 `dirpath + "/" + d_name`？
>    答：`d_name` 只有文件名没有路径；`stat`、递归、打印都需要从入口开始的完整路径。
> 6. 为什么判断类型用 `stat` 而不是 `entry->d_type`？
>    答：`d_type` 在部分文件系统返回"不知道"；`stat` 永远可靠，且步骤 5 的 `st_mtime` 反正要用它。

## 关联

[[课程笔记/C语言/C语言|C语言]] · [[课程笔记/C语言/文件操作背后的系统概念-五个直觉|文件操作背后的系统概念：五个直觉]] · [[课程笔记/C语言/P1-note-stats-实现大纲|P1 note-stats 实现大纲]] · [[课程笔记/C语言/命令行参数-argc与argv入门|命令行参数：argc 与 argv 入门]] · [[课程笔记/C语言/标准错误流-fprintf与stderr详解|标准错误流：fprintf 与 stderr 详解]] · [[课程笔记/C语言/make入门-make_test逐行详解|make 入门]] · [[somezhishi/编程基础/Linux重定向-文件描述符与2&1详解|Linux 重定向]]
