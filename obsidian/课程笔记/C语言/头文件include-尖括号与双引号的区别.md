---
date: 2026-09-22
course: C语言
---

# 头文件 include：尖括号与双引号的区别（新手版）

> [!note] 一句话先行
> `#include` 是预处理阶段的"复印机"：真正编译之前，把目标头文件的**内容整段抄**到你写这一行的位置。`"..."` 和 `<...>` 的唯一区别是**先去哪儿找**——双引号先看"引用它的那个文件旁边"，尖括号跳过身边、直接逛配置好的书店。
> 相关：[[课程笔记/C语言/C语言|C语言]] · [[课程笔记/C语言/命令行参数-argc与argv入门|命令行参数：argc 与 argv]] · 延伸：[[归档/30天学习/教学-STM32/reference/0002b-stm32f1xx_hal.h逐行精读与C语法复习|0002b HAL 头文件精读（含 `"x"` vs `<x>` 语法点）]]

## 一、先建画面：预处理是一台"复印机"

一个 `.c` 变成可执行文件，走三段路：

```
main.c  --预处理-->  展开后的 main.c（一个 # 开头的行都不剩）  --编译-->  main.o  --链接-->  可执行文件
          ↑
      #include 只活在这一步
```

预处理器不认识 C 语法，只会做"文字工作"：抄头文件（`#include`）、换文字（`#define`）、按条件裁剪（`#ifdef`）。抄完的"膨胀版"才交给编译器。想亲眼看它抄了什么，用 `-E`（只预处理）：

```bash
gcc -E main.c | less
```

本机（GCC 13.3）实测，一个只写了 `#include "inc/my.h"` 和 `#include <stdio.h>` 的 `main.c`，`gcc -E main.c | head -8` 的开头是：

```
# 0 "main.c"
# 0 "<built-in>"
# 0 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 0 "<command-line>" 2
# 1 "main.c"
# 1 "inc/my.h" 1
# 2 "main.c" 2
```

- `# 1 "inc/my.h"` 这种 **行标记（line marker）** 是预处理器留下的"抄写记录"：告诉编译器"接下来这段来自哪个文件第几行"，以便报错时能指回原位。
- 有个小彩蛋：你一行 include 还没写，GCC 自己先塞了个 `/usr/include/stdc-predef.h`——编译器默认自带的行为，知道有这回事就行。

再看一眼"一次 `<stdio.h>` 到底抄了多少文件"，用 `-H`（打印包含链，只看文件名）：

```bash
gcc -E -H main.c 2>&1 >/dev/null | head -8
```

```
. inc/my.h
. /usr/include/stdio.h
.. /usr/include/x86_64-linux-gnu/bits/libc-header-start.h
... /usr/include/features.h
.... /usr/include/features-time64.h
..... /usr/include/x86_64-linux-gnu/bits/wordsize.h
..... /usr/include/x86_64-linux-gnu/bits/timesize.h
...... /usr/include/x86_64-linux-gnu/bits/wordsize.h
```

前面的点号是"包含深度"：`stdio.h` 内部又 include 了 `features.h`，`features.h` 又 include 了更多……**一行 include 背后可能是几十个文件**。所以头文件必须防重复（见第五节）。

## 二、为什么非要 include：声明 vs 定义

新手常问："我直接在 `main.c` 里调 `printf` 不行吗？" 不行——编译器是**逐文件干活**的，它的工作方式像流水线：读一个文件、立刻翻译一个文件。读到 `printf("hi")` 时，它必须已经知道：这个函数收什么参数、返回什么类型。

| 概念 | 大白话 | 在哪 |
| --- | --- | --- |
| **声明（declaration）** | 菜单上的菜名和价格：有这个函数、长这样，结尾是 `;` | 头文件 `.h` |
| **定义（definition）** | 后厨真正的做法：有 `{ }` 函数体 | 源文件 `.c` 或预编译好的库 |

所以：

- **编译**时：`#include <stdio.h>` 把 `printf` 的声明抄进来，编译器据此检查你调用得对不对；
- **链接**时：链接器去 libc 库里找 `printf` 的**定义**，把两边接上。

读法：**头文件负责"告诉编译器有这个功能"，库负责"提供这个功能的代码"。**

## 三、两种写法的区别：先去哪儿找

画面：你说"给我找本书来"——

- `#include "my.h"` —— **双引号 = 先看我身边**。先搜**引用它的那个文件所在目录**（注意：不是你在终端敲命令的当前目录），找不到再按配置的路径清单找。
- `#include <stdio.h>` —— **尖括号 = 只逛书店**。跳过"身边"，直接去编译器配置好的**包含路径清单**里找。

GCC 上精确的搜索顺序：

| 写法 | ① 引用它的文件所在目录 | ② `-iquote` 目录 | ③ `-I` 目录 | ④ 系统目录 |
| --- | --- | --- | --- | --- |
| `#include "x.h"` | ✅ | ✅ | ✅ | ✅ |
| `#include <x.h>` | ❌ | ❌ | ✅ | ✅ |

口诀：**双引号比尖括号多搜一个"文件旁边"，就这一个区别。**

### 三个实测（本机 GCC 13.3，都在 `/tmp/opencode/include-demo` 里跑）

**实验 1：自己的头文件用了尖括号 → 直接找不到。**

`my.h` 在 `inc/` 里，`main.c` 却写 `#include <my.h>`：

```
angle_test.c:1:10: fatal error: my.h: No such file or directory
    1 | #include <my.h>
      |          ^~~~~~
compilation terminated.
```

**实验 2：给尖括号配好路径 → 能通。** 加上 `-Iinc`：

```bash
gcc -c -Iinc angle_test.c -o /dev/null   # 编过
```

**实验 3：双引号找的是"文件旁边"，不是终端当前目录。** `local.h` 和 `uses_local.c` 都在 `sub/` 里，我在 `demo/` 目录下执行：

```bash
gcc -c sub/uses_local.c -o /dev/null     # 编过；cwd 里根本没有 local.h
```

它照样找到了 `sub/local.h`——因为 `"local.h"` 是从 **`uses_local.c` 自己所在的文件夹**开始找的。

### 那该怎么选

| 场景 | 写法 | 例子 |
| --- | --- | --- |
| 标准库 | `<...>` | `<stdio.h>` `<stdlib.h>` `<string.h>` |
| 第三方 / 官方库（在系统包含路径里） | `<...>` | `<SDL2/SDL.h>` |
| **你自己项目的头文件** | `"..."` | `"note-stats.h"` `"main.h"` |

技术上并不严格：GCC 下 `#include "stdio.h"` 也能跑——双引号在"身边"找不到后会退回同一份路径清单。所以这不是"能力"区别，而是**搜索顺序 + 意图标记**的区别：引号 = 这个文件属于本项目，尖括号 = 这是外部依赖。将来换编译器、配 IDE、别人读代码都靠它判断。

## 四、两个新手最常踩的坑

1. **自己的头文件用尖括号** → 报 `fatal error: xxx.h: No such file or directory`（如实验 1）。解法二选一：
   - 改回 `"xxx.h"`；
   - 或在构建配置里加路径：Makefile 写 `CFLAGS += -Iinclude`；CMake 写 `target_include_directories(note-stats PRIVATE include)`。
2. **身边同名文件"劫持"系统头**：假如你在当前目录放了一个自己的 `string.h`，然后 `#include "string.h"`——引到的是**你的**文件，系统的那个被挤掉了，里面函数全部失踪。这就是标准库统一用 `<...>` 的又一个理由：**尖括号不搜身边，不会被本地的同名文件意外顶包。**

## 五、配套概念（知道名字和用途就够）

- **include guard（包含守卫）**：头文件开头 `#ifndef XXX_H` / `#define XXX_H`，结尾 `#endif`，保证同一个头文件被间接包含多次时**只被完整读一遍**。新式写法是文件第一行 `#pragma once`，效果类似。为什么需要？看第一节的包含链——`stdio.h` 和你的 `my.h` 可能都包含同一个文件，没有守卫就会重复定义报错。
- **永远不要 `#include "xxx.c"`**：`.c` 是拿来单独编译的；把 `.c` 抄进别的 `.c`，链接时同一份定义出现两遍，直接报重复定义。
- **包含路径清单从哪来**（`-I` 那一栏）：
  - 命令行：`gcc -Iinc ...`
  - Makefile：`CFLAGS += -Iinclude`
  - CMake：`target_include_directories(myexe PRIVATE include)`（STM32 工程的 `Core/Inc` 就是这样进去的）
  - VS Code 的 C/C++ 插件另有一份 `includePath` 只给它自己的 IntelliSense 用，和编译无关——详见 [[somezhishi/环境排障/VSCode-C++插件-IntelliSense配置与gcc-g++区别|VSCode C++ 插件：IntelliSense 与 gcc 的区别]]
- **STM32 工程里的真实例子**：`main.c` 里写 `#include "main.h"`（同目录，双引号正合适）；HAL 库文件里写 `#include "stm32f1xx_hal.h"`（不同目录，靠 CMake 的包含路径清单找到）。后者再次说明：**双引号在"身边"找不到时会退回 `-I` 清单**，所以它才通。

## 六、自己验证（可复现，全程在 /tmp 里做，不动仓库）

```bash
mkdir -p /tmp/opencode/include-demo/inc && cd /tmp/opencode/include-demo
printf '#define GREETING "hello"\n' > inc/my.h
printf '#include "inc/my.h"\n#include <stdio.h>\nint main(void){ puts(GREETING); return 0; }\n' > main.c

gcc -E main.c | head -8          # 看行标记：行首 # 开头那几行
gcc -E -H main.c 2>&1 >/dev/null # 看包含链（点号表示深度）
gcc main.c -o main && ./main     # 实测输出: hello
```

## 术语小词典

| 词 | 大白话 |
| --- | --- |
| 预处理（preprocess） | 编译前的"文字处理"：抄头文件、换文字、按条件裁剪 |
| 预处理器（preprocessor） | 干上面这些活的程序，`#` 开头的行归它管 |
| 头文件（header，`.h`） | 放声明、宏、类型定义的文件，被 `#include` 抄进 `.c` |
| 声明 vs 定义 | 声明 = 菜单菜名（`;` 结尾）；定义 = 后厨做法（有 `{ }`） |
| 链接（link） | 把多个 `.o` 和库拼成可执行文件，接上函数定义的时刻 |
| 包含路径（include path） | 编译器找头文件的目录清单，`-I` / CMake / IDE 配置 |
| `-E` | gcc 选项：只做预处理就停，用来偷看"抄完长什么样" |
| 行标记（line marker） | `# 1 "inc/my.h"` 这类行，记录"这段抄自哪"，为报错定位 |
| include guard | 防止同一头文件被读两次的 `#ifndef/#define/#endif` 三行哨兵 |
| `#pragma once` | 更简短的新式防重复包含写法，作用类似 include guard |
| 劫持（shadow） | 本地同名文件抢在系统头前面被引到，导致函数"消失" |

## 自测

> [!question]- 想好再展开
> 1. `#include "inc/my.h"` 里那个 `inc/` 是相对谁算的？
>    答：相对**写这行 include 的文件所在目录**，不是终端当前目录（实验 3）。
> 2. 为什么标准库要用 `<...>` 而不是 `"..."`？
>    答：两层原因：① 尖括号不搜"身边"，不会被本地同名文件劫持；② 明确表达"这是外部依赖"的意图。
> 3. 自己的 `my.h` 写成 `<my.h>` 报 `No such file or directory`，两种修法？
>    答：改成 `"my.h"`；或在构建配置里加路径（`gcc -Iinc` / Makefile `CFLAGS += -I...` / CMake `target_include_directories`）。
> 4. `#include` 是"把库的代码接进来"吗？
>    答：不是。它只是在预处理时**抄头文件里的声明**；函数真正的定义在库里，由**链接器**接上。
> 5. 头文件里的 include guard 是防什么的？
>    答：防止同一个头文件（经多条路径）被重复完整包含，导致重复定义报错。
