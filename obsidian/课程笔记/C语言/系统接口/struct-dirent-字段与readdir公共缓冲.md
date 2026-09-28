---
date: 2026-09-28
course: C语言
---

# struct dirent：字段与 readdir 的公共缓冲（新手版）

> [!note] 一句话先行
> `struct dirent` 是"目录条目卡片"的类型，声明链是 `dirent.h → bits/dirent.h`。真正该依赖的只有 `d_name`（**只有名字、没有路径**）；`readdir` 每次返回指向**同一张公共卡片**的指针，下次调用会覆盖——要留下内容就当场复制。
> 相关：[[课程笔记/C语言/C语言|C语言]] · [[课程笔记/C语言/系统接口/opendir与DIR句柄-从POSIX讲起|opendir 与 DIR 句柄]] · [[课程笔记/C语言/系统接口/struct-stat-文件体检报告与stat错误检查|struct stat]] · [[课程笔记/C语言/项目实战/目录遍历与递归-note-stats步骤2|目录遍历与递归]]

## 一、声明在哪：一条"头文件套娃"链

你写的是 `#include <dirent.h>`，但 glibc 的 `dirent.h` 自己并不写结构体，它转手引了平台相关的一份。本机真实源码：

```c
/* /usr/include/dirent.h:61 */
#include <bits/dirent.h>

/* /usr/include/x86_64-linux-gnu/bits/dirent.h:22-34 */
struct dirent
{
    __ino_t d_ino;
    __off_t d_off;
    unsigned short int d_reclen;
    unsigned char d_type;
    char d_name[256];
};
```

`bits/dirent.h` 开头还有警告（:18-20）："Never include `<bits/dirent.h>` directly"——`bits/` 属于实现细节，换平台（如 ARM）路径和内容都可能不同；入口永远走 `dirent.h`。

## 二、字段表与重要性分层

把"每张卡片 = 目录里一个条目"记住后，逐栏看：

| 成员 | 装的信息 | 要不要关心 |
| --- | --- | --- |
| `d_name` | **文件名**（不含路径），NUL 结尾 | ✅ 唯一必用 |
| `d_ino` | inode 号（文件"身份证号"） | 需要识别"同一个文件"时才用 |
| `d_type` | 条目类型：`DT_DIR` / `DT_REG` / `DT_LNK`… | ⚠️ 可用但**不可靠**，见第五节 |
| `d_off` / `d_reclen` | 库 / 内核内部记账与记录长度 | ❌ 不用 |

**可移植性分层**：POSIX 保证到处都能依赖的是 `d_name`（`d_ino` 也算）；`d_type`、`d_reclen`、`d_off` 是 Linux / BSD 系扩展。写跨平台代码时，就当只有 `d_name` 可用。

## 三、`d_name` 只是"名字"，不是路径

目录 `obsidian/` 里读到的 `d_name` 是 `"每日日志"` 这种光杆名字。这就是 note-stats.c:37 必须 `snprintf` 拼 `dirpath + entry->d_name` 的原因——**目录流不会帮你记路径，路径是你自己一层层攒出来的**（拼法与斜杠契约见 [[课程笔记/C语言/项目实战/目录遍历与递归-note-stats步骤2|步骤 2 笔记]]第四节）。

## 四、readdir 的"公共卡片"：下次调用会覆盖

`readdir(dir)` 每次从进度档案里抽一张卡片给你，返回 `struct dirent *`。但要记住：**这张卡片是档案里固定的那一张**，下次 `readdir` 会把它的内容擦掉重写。所以：

- 卡片指针不能存起来"以后再读"；
- 要留内容（比如文件名），当场复制走——note-stats 是立刻用它拼进 `child` 缓冲，正好符合这条纪律。

## 五、为什么不直接用 `d_type` 图快

直觉上，note-stats.c:51 的目录判断可以写成 `entry->d_type == DT_DIR`，不必 `stat`。但 `d_type` 有个坑：不少文件系统（某些 XFS、老 NFS 等）填不出来，统一报 `DT_UNKNOWN`——**"不知道"和"不是目录"就分不清了**。稳健做法就是像 note-stats 那样老实用 `stat(child, &st)` + `S_ISDIR`（:44-51），拿系统权威答案（详见 [[课程笔记/C语言/系统接口/struct-stat-文件体检报告与stat错误检查|struct stat 笔记]]）。

顺带认一眼 `DT_*` 枚举的真身（`dirent.h:97-117`）：`DT_UNKNOWN=0`、`DT_DIR=4`、`DT_REG=8`、`DT_LNK=10`……注意它是**另一套编码**，和 `st_mode` 里的 `S_IF*` 不是一回事（`IFTODT` 宏负责换算）。

## 术语小词典

| 词 | 大白话 |
| --- | --- |
| 目录条目（directory entry） | 目录里一条记录 = 文件名 + 它的 inode 号 |
| `bits/` 目录 | glibc 放平台相关内部头文件的目录，仅供间接引用 |
| inode | 文件系统里文件的编号与元数据结点，"身份证" |
| 不透明 / 内部缓冲 | 数据结构归库所有，你只拿指针、不拥有内容 |
| `DT_UNKNOWN` | "类型未知"，部分文件系统不填 `d_type` 时的值 |

## 自测

> [!question]- 想好再点开
> 1. `entry->d_name` 里拿到的是 `"/home/fgh/projects"` 还是 `"projects"`？和 note-stats.c:37 的拼接有何因果？
>    答：只有 `"projects"` 这种光杆名字；所以必须自己拼 `dirpath + "/" + d_name` 得到完整路径。
> 2. 为什么 `readdir` 返回的指针不能存起来、下次循环再读它的 `d_name`？
>    答：它指向库内部同一张公共卡片，下一次 `readdir` 会覆盖内容；要留就当场复制。
> 3. `DT_UNKNOWN` 为什么让"用 `d_type` 判目录"不可靠？
>    答：部分文件系统不提供类型，只能填"未知"；此时既不能确定是目录也不能确定不是，只有 `stat` 能给出权威答案。

## 关联

[[课程笔记/C语言/C语言|C语言]] · [[课程笔记/C语言/系统接口/opendir与DIR句柄-从POSIX讲起|opendir 与 DIR 句柄]] · [[课程笔记/C语言/系统接口/struct-stat-文件体检报告与stat错误检查|struct stat：文件体检报告]] · [[课程笔记/C语言/项目实战/目录遍历与递归-note-stats步骤2|目录遍历与递归]]
