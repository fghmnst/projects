---
date: 2026-09-19
course: C语言
---

# 标准错误流：fprintf 与 stderr（新手版）

> [!note] 一句话先行
> 每个程序都有"两张嘴"：`stdout` 说结果（给机器、管道、重定向用），`stderr` 说人话（错误、警告、用法提示）。`printf` 只会走 stdout；`fprintf` 能指定走哪张嘴——`fprintf(stderr, ...)` 就是"这条信息说给人听"的标准写法。
> 相关：[[课程笔记/C语言/C语言|C语言]] · [[课程笔记/C语言/命令行参数-argc与argv入门|命令行参数：argc 与 argv]] · [[somezhishi/编程基础/Linux重定向-文件描述符与2&1详解|Linux 重定向：文件描述符与 2>&1]]

## 一、当前 note-stats 干了什么

```c
int main(int argc, char *argv[])
{
    if (argc < 2) {                                  /* 用户没给目录 */
        fprintf(stderr, "用法：note-stats <目录>\n");
        return 1;                                     /* 退出码 1 = 失败 */
    }
    printf("目录: %s\n", argv[1]);                    /* 正常结果走 stdout */
    return 0;                                         /* 退出码 0 = 成功 */
}
```

一句话：**检查有没有给目录参数——没给就报用法并以失败退出，给了就打印目录名。**

实测行为（本机运行）：

| 命令 | 屏幕 | 退出码 |
| --- | --- | --- |
| `./note-stats` | `用法：note-stats <目录>` | 1 |
| `./note-stats 2>/dev/null` | （什么都不显示） | 1 |
| `./note-stats /tmp` | `目录: /tmp` | 0 |

第二行是关键实验：**把 stderr 丢掉，用法信息就没了，但退出码还是 1**——证明这行信息走的不是 stdout 那条路。

## 二、fprintf 是 printf 的亲兄弟

`printf` 是"特化版"：只会往标准输出写。`fprintf` 是一般形态，多给一个参数指定通道：

```c
printf("目录: %s\n", argv[1]);              /* 等价于 ↓ */
fprintf(stdout, "目录: %s\n", argv[1]);     /* 指定写 stdout */
fprintf(stderr, "用法：...\n");              /* 指定写 stderr */
```

- 名字里 `f` = file/formatted；第一个参数类型是 `FILE *`——一个"输出通道"的句柄；
- `stdout`、`stderr`、`stdin` 都是 `<stdio.h>` 里**预定义好的全局通道**，程序一启动就有，不用自己创建；
- 大学教材常跳过这组函数，但它不是超纲怪招：K&R 第 7 章讲 fprintf 家族，书里错误处理示例也一直用 `fprintf(stderr, ...)`。

## 三、stderr 是什么：程序的"第二张嘴"

每个程序启动时都有三条默认通道（编号来自 [[somezhishi/编程基础/Linux重定向-文件描述符与2&1详解|文件描述符]]）：

| 通道 | 文件描述符 | 默认去向 | 放什么 |
| --- | --- | --- | --- |
| `stdin` | 0 | 键盘 | 输入 |
| `stdout` | 1 | 屏幕 | **程序的正常产物** |
| `stderr` | 2 | 屏幕 | **诊断信息**（错误 / 警告 / 用法提示） |

它们默认都连屏幕，所以看起来一样；**一重定向就分道扬镳**。

## 四、为什么用法信息要用 fprintf + stderr

1. **分工原则**：目录列表（结果）以后要能管道给别的程序；用法提示是"给人看的诊断"，不该混进结果流。`./note-stats /tmp | wc -l` 时数据流必须干净。
2. **重定向后仍然可见**：`./note-stats > out.txt` 时 stdout 进了文件、stderr 还在屏幕——用户能立刻看到"为什么失败"；若用 printf，提示会静默进 `out.txt`，屏幕一片空白。
3. **不被缓冲拖住**：stdout 重定向到文件后是**全缓冲**（攒够一块才写），stderr 默认**不带缓冲**——程序提前退出时错误信息不会卡在缓冲区里丢件。
4. **和退出码配对**：机器看 `$?`（1 = 失败），人看 stderr 里的原因；`&&` 判断成败的那套就靠这个组合。

自己动手对比（会生成文件）：

```bash
./note-stats > /tmp/out.txt        # 屏幕仍显示用法；out.txt 是空的
./note-stats /tmp > /tmp/out.txt 2> /tmp/err.txt   # 两条通道分流到两个文件
```

> [!note] 小提示
> 这里把程序名写死成 `note-stats`。更通用的写法是用 `argv[0]`：`fprintf(stderr, "用法：%s <目录>\n", argv[0]);`——程序被改名或按全路径调用时，提示会自动跟着变。

## 五、以后什么时候该想到它（触发清单）

| 场景 | 用什么 |
| --- | --- |
| 正常结果（要被后续处理的数据） | `printf` / stdout |
| 用法提示、参数错误、失败原因 | `fprintf(stderr, ...)` + 非 0 退出码 |
| 写具体文件（P2 输出报告） | `fopen` 拿到 `FILE *fp` → `fprintf(fp, ...)` |
| 系统调用失败的报错 | `perror("opendir")`——自动附上系统错误原因；P1 读目录马上会用到 |
| 调试打印 | 也走 stderr，不污染 stdout 管道 |

一句话记忆：**"程序产物走 stdout，人的话走 stderr。"**

## 术语小词典

| 词 | 大白话 |
| --- | --- |
| `fprintf` | printf 的一般版：多给一个"通道"参数，指定往哪写 |
| `FILE *` | 一个输入/输出通道的句柄；stdout/stderr 就是预定义好的两个 |
| stdin / stdout / stderr | 每个程序自带的三条标准通道（0/1/2） |
| 诊断信息 | 错误、警告、用法提示——给人看，不是程序的结果 |
| 缓冲 | 数据先攒着、够量或退出前才真正写出；stderr 默认不攒、立即写 |
| `perror` | 打印"你给的说明 + 系统错误原因"到 stderr 的小工具 |
| `errno` | 最近一次系统调用失败原因的数字代号，`perror` 会替你翻译 |

## 自测

> [!question]- 想好再展开
> 1. 把 `fprintf(stderr, "用法：...\n")` 改成 `printf("用法：...\n")`，运行 `./note-stats > out.txt` 会看到什么？
>    答：屏幕上什么都看不到；用法信息被写进 out.txt（用户不知道为什么失败）。
> 2. `printf("hi\n")` 和 `fprintf` 是什么关系？
>    答：`printf(...)` 是完全等价的简写。
> 3. 以后要输出一份统计报告存到文件，用哪条通道/函数？
>    答：`fopen` 得到 `FILE *fp`，用 `fprintf(fp, ...)` 写文件；屏幕上的错误提示仍走 stderr。
