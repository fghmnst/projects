# Lesson 0002 · CubeMX 工程结构解剖：DianDengMaster 逐文件精读

> 本课里程碑：**面对 DianDengMaster 能说出每个文件是干什么的、哪些能改哪些不能改，main.c 每一行都看得懂**
> 前置：[[教学-STM32/lessons/0001-工具链闭环与LED闪烁|0001 工具链闭环与 LED 闪烁]]（已能编译+烧录）

## 本课你会得到什么

上一课你烧录了第一段程序，灯闪了。但那个工程对你还是「黑盒」——你知道怎么用，不知道里面是什么。本课把它拆开：

1. **明白工程是谁造出来的**：CubeMX 生成器和你之间有一条清晰的「代码边界」——越界手改，代码会被冲掉
2. **每个文件的作用**：从 `.ioc` 到 `main.c` 到链接脚本，逐个讲清楚
3. **代码的类别**：每个文件里的代码属于哪一类（初始化配置 / 业务逻辑 / 中断处理 / 库 / 胶水层），类别的边界就是「能不能改」的边界
4. **术语彻底过关**：本课出现的每个专业术语都有详细解释，学完再看任何 STM32 教程都不会被术语卡住

---

## 一、全景图：这个工程是谁造出来的

先回答一个关键问题：**DianDengMaster 文件夹里 90% 的内容不是你写的，也不是编译器写的，是 CubeMX 生成的。**

生成器的逻辑是这样的：

```
你在 CubeMX 里勾选配置（芯片型号、引脚、时钟…）
              │  存成
              ▼
        DDM_test.ioc（配置档案，纯文本）
              │  点 "Generate Code"
              ▼
    CubeMX 按配置批量生成代码文件：
    ├── Core/       ← 应用骨架（main.c、中断文件…）
    ├── Drivers/    ← HAL + CMSIS 库（拷贝进工程）
    ├── startup.s   ← 启动文件
    ├── .ld         ← 链接脚本
    └── cmake/      ← 构建系统
```

所以这套工程里有两种来源的文件：

| 来源 | 目录 | 能手动改吗 |
|---|---|---|
| CubeMX 生成的骨架 | `Core/`、`startup.s`、`.ld`、`cmake/` | **能，但只能在 USER CODE 保护区里改** |
| CubeMX 拷进来的库 | `Drivers/` | 不要改（改了也会被重新生成覆盖） |
| 你新建的文件 | 任意位置（建议 `Core/Inc`、`Core/Src`） | 完全自由 |

> [!warning] 最重要的一个概念：USER CODE 保护区
> CubeMX 每次点「Generate Code」都会**重写**它生成的文件。为了防止你的手写代码被冲掉，它在每个文件里预留了保护区：
>
> ```c
> /* USER CODE BEGIN 2 */
> 你的代码放这里        ← 安全区，重新生成时保留
> /* USER CODE END 2 */
>
> 保护区之外的代码      ← 危险区，重新生成时被删除
> ```
>
> 规则只有一条：**手写代码一律放进 `USER CODE BEGIN/END` 之间**。CubeMX 生成器会完整保留这两个标记之间的内容。这也解释了为什么 main.c 长得很啰嗦——大量空区块都是为你的代码预留的「车位」。

---

## 二、目录树总览

```
DianDengMaster/                          ← 工程根（既是源码根，也是 CMake 根）
│
├── DDM_test.ioc                         ← 【配置档案】CubeMX 的记忆
├── .mxproject                           ← 【缓存】CubeMX 的草稿纸（隐藏文件）
├── CMakeLists.txt                       ← 【构建入口】告诉 CMake 工程长什么样
├── CMakePresets.json                    ← 【构建预设】Debug/Release 配置
├── startup_stm32f103xb.s                ← 【启动文件】上电后第一条指令（汇编）
├── STM32F103xx_FLASH.ld                 ← 【链接脚本】内存布局说明书
│
├── cmake/                               ← 【构建辅助】
│   ├── gcc-arm-none-eabi.cmake          ←   交叉编译工具链定义（正式）
│   ├── starm-clang.cmake                ←   clang 工具链（备用，不用管）
│   └── stm32cubemx/CMakeLists.txt       ←   真正的编译清单（CubeMX 每次写！）
│
├── Core/                                ← 【你的代码】应用层
│   ├── Inc/                             ←   头文件
│   │   ├── main.h                       ←    引脚宏定义、函数声明
│   │   ├── stm32f1xx_it.h               ←    中断函数的声明
│   │   └── stm32f1xx_hal_conf.h         ←    HAL 库模块开关（总闸）
│   └── Src/                             ←   源文件
│       ├── main.c                       ←   主程序（你最重要的文件）
│       ├── stm32f1xx_it.c               ←   中断服务程序 ISR
│       ├── stm32f1xx_hal_msp.c          ←   外设底层支持 MSP 初始化
│       ├── syscalls.c                   ←   C 库系统调用桩
│       ├── sysmem.c                     ←   C 库内存管理（malloc 的来源）
│       └── system_stm32f1xx.c           ←   系统时钟初始化 SystemInit
│
└── Drivers/                             ← 【ST 官方库】只读，别碰
    ├── CMSIS/                           ←   ARM 内核标准（core_cm3.h 等）
    └── STM32F1xx_HAL_Driver/            ←   HAL 外设驱动（GPIO/RCC/UART…）
```

按「代码类别」重新分组就是：

| 类别 | 包含 | 负责什么 | 谁维护 |
|---|---|---|---|
| 应用代码 | `Core/Src/*.c`、`Core/Inc/*.h` | 你的业务逻辑（点灯、以后的控制） | **你** |
| 外设驱动库 | `Drivers/STM32F1xx_HAL_Driver/` | 操作 GPIO/时钟/串口的现成函数 | ST 官方 |
| 内核标准库 | `Drivers/CMSIS/` | CPU 内核与芯片寄存器的定义 | ARM/ST 官方 |
| 启动与链接 | `startup.s`、`.ld` | 上电准备、内存布局 | ST 官方（CubeMX 生成） |
| 构建系统 | `CMakeLists.txt`、`CMakePresets.json`、`cmake/` | 组织编译 | CubeMX 生成 + 你可扩充 |

> [!note] 术语
> **代码类别**：本文说的「类别」指代码在工程中的**职责分层**——初始化配置类、业务逻辑类、中断处理类、库类、胶水层类。类别决定了「这份代码能不能改、改了会不会被覆盖」。记住一句话：**层次越低（越接近硬件），越不该自己改**。

---

## 三、根目录 7 件逐文件讲解

### 3.1 `DDM_test.ioc` —— 配置档案（工程的「大脑」）

`.ioc`（I/O Configuration）是 CubeMX 的工程配置档案，**纯文本**，记录了你在图形界面里做的每一个选择。它既是「记忆」也是「源头」：改配置的正确路径是「改 .ioc → 重新生成代码」，而不是手改生成的 `.c` 文件。

打开看关键行：

| 行内容 | 含义 |
|---|---|
| `Mcu.Name=STM32F103C(8-B)Tx` | 芯片型号（8 = 64KB Flash 档） |
| `Mcu.Pin0=PA6` + `PA6.Signal=GPIO_Output` | 引脚 PA6 配成普通输出 |
| `PA6.GPIO_Label=LED` | 给 PA6 起名字叫 LED → 生成 `LED_Pin`/`LED_GPIO_Port` 宏 |
| `PA13.Mode=Serial_Wire` / `PA14.Mode=Serial_Wire` | 保留 SWD 调试口（0001 警告过的关键配置） |
| `RCC.APB1Freq_Value=8000000` | 时钟树当前值（8MHz，用的是内部时钟） |
| `ProjectManager.StackSize=0x400` | 栈大小 1KB → 写进链接脚本 |
| `ProjectManager.HeapSize=0x200` | 堆大小 512B → 写进链接脚本 |
| `ProjectManager.TargetToolchain=CMake` | 生成 CMake 工程 |
| `MxCube.Version=6.18.1` | 生成用的 CubeMX 版本 |

> [!note] 术语
> **.ioc 文件**：CubeMX 的工程档案（纯文本配置）。改配置 = 改 .ioc（在 GUI 里改）→ 重新生成代码。**不要手改 .ioc**，格式是工具专用格式，手改容易坏。
> **代码生成（code generation）**：CubeMX 按 .ioc 配置自动产出 `main.c` 等初始化代码的过程（0001 已收录）。

> [!warning] 坑提醒（本机实测）
> AGENTS.md 里记录的旧结构「CMake 根在嵌套 `DianDengMaster_1/`」已过时——2026-08-11 重新生成后，CMake 文件都在工程根目录（单层结构），`.ioc` 名字也成了 `DDM_test.ioc`。**以实际目录为准**。

### 3.2 `.mxproject` —— CubeMX 的缓存（草稿纸）

记录「上次生成了哪些文件、哪些库」，CubeMX 靠它做增量更新（只重写变动的文件）。纯元数据，**永远不要手动改**。

### 3.3 `CMakeLists.txt` —— 构建入口（工程的门面）

> [!note] 术语
> **CMake**：构建系统（0001 已收录）。它本身不编译，而是**读取规则、生成 Ninja/Makefile 构建文件**，真正的编译由 Ninja 执行。
> **CMakeLists.txt**：CMake 的规则声明文件，用 CMake 语法写「工程叫啥、有哪些源码、怎么编译」。

本工程根 `CMakeLists.txt` 只有 68 行，干 4 件事：

```cmake
set(CMAKE_C_STANDARD 11)          # 1. 用 C11 标准（HAL 库要求 C11 以上）
set(CMAKE_PROJECT_NAME DDM_test)  # 2. 工程名 = DDM_test（产物就叫 DDM_test.elf）
add_executable(DDM_test)          # 3. 声明可执行目标（先空壳，源码后面补）
add_subdirectory(cmake/stm32cubemx)  # 4. 引入子目录：真正的编译清单在那
target_link_libraries(DDM_test stm32cubemx)  #    链接上库目标
```

这个文件**只生成一次，CubeMX 不再重写**（文件头注释写明）——所以它是你将来扩展工程的入口：加第三方库、加你自己写的 `.c` 文件，都从这加。

> [!note] 术语
> **target（目标）**：CMake 里的构建单元，可以是可执行文件（`add_executable`）、库（`add_library`）等。目标是「打包」概念：把一堆源码、头文件路径、宏、链接选项捆在一起。
> **add_subdirectory**：把另一个含 CMakeLists.txt 的目录纳入当前工程（子工程/子目录）。

### 3.4 `CMakePresets.json` —— 构建预设（方案表）

```
CMakePresets.json
├── configurePresets  （配置方案）
│   ├── default  ← 隐藏基础方案：Ninja 生成器 + gcc-arm-none-eabi 工具链 + 产物进 build/Debug
│   ├── Debug    ← 继承 default，开调试优化（-O0 -g3）
│   └── Release  ← 继承 default，开体积优化（-Os）
└── buildPresets  （编译方案，对应上面的配置）
```

VS Code 的 CMake Tools 插件打开工程时，让你选的 preset 就是这里面的。**Debug** = 方便调试（不优化、带调试信息），**Release** = 体积小跑得快。学习阶段一直用 Debug。

> [!note] 术语
> **preset（预设）**：CMake 预定义好的「配置+编译方案」，把一长串参数（生成器、工具链、构建类型）打包成一个名字，选中即用。
> **Ninja**：一个比 make 更快的构建工具（编译执行器）。CMake 负责「算」，Ninja 负责「干」。

### 3.5 `startup_stm32f103xb.s` —— 启动文件（上电后的第一段代码）

这是整个工程**唯一的汇编文件**，也是芯片复位后执行的第一段代码。`.s` 后缀 = 汇编语言（Assembly）。

它做 4 件事，按顺序：

```
① 定义中断向量表（g_pfnVectors）
② Reset_Handler 启动流程：
   SystemInit()（配时钟）→ 拷贝 .data 段到 RAM → 清零 .bss 段 → main()
③ 为所有中断提供「弱符号」默认实现（死循环）
④ 定义 BootRAM 等引导信息
```

**① 中断向量表（vector table）** —— 文件里的一段表格：

```asm
g_pfnVectors:
  .word _estack          ; 第 0 项：栈顶地址（RAM 的最高处）
  .word Reset_Handler    ; 第 1 项：复位后执行的第一条指令
  .word NMI_Handler      ; 第 2 项：不可屏蔽中断
  .word HardFault_Handler; 第 3 项：硬件错误
  .word SysTick_Handler  ; ... 每个中断一项，共 60+ 项
```

> [!note] 术语
> **中断向量表（vector table）**：一张「中断编号 → 处理函数地址」的对照表，固定在 Flash 起始位置（0x08000000）。芯片发生中断时，硬件查这张表找到对应的处理函数跳过去。**它必须放在地址 0**（0x08000000），所以链接脚本把 `.isr_vector` 段排在最前面。

**② Reset_Handler 逐段解读**：

```asm
Reset_Handler:
    bl  SystemInit          ; 调用 system_stm32f1xx.c 里的 SystemInit() 配时钟
    ; ── 把 .data 段从 Flash 拷到 RAM（C 语言里"有初值的全局变量"住这）──
    ldr r0, =_sdata         ; RAM 里 .data 起始地址
    ldr r1, =_edata         ; RAM 里 .data 结束地址
    ldr r2, =_sidata        ; Flash 里 .data 的存放位置（见链接脚本 3.6）
    ; …循环拷贝…
    ; ── 把 .bss 段清零（C 语言里"没初值的全局变量"默认该是 0）──
    ldr r2, =_sbss
    ldr r4, =_ebss
    ; …循环清零…
    bl __libc_init_array    ; C++ 静态对象构造（C 工程为空）
    bl main                 ; ★ 终于进入你的 main()！
```

为什么要有这一步？因为 Flash 掉电不丢、RAM 掉电清空——**变量初值只能存 Flash，上电后必须人工搬运到 RAM**。这就是嵌入式里经典的「C 运行环境准备」。

**③ 弱符号机制**：

```asm
.weak HardFault_Handler
.thumb_set HardFault_Handler,Default_Handler   ; 默认指向死循环
```

> [!note] 术语
> **弱符号（weak symbol）**：一个「可以被覆盖」的函数定义。链接时，如果别处定义了同名强符号，就替换掉弱符号。所以 CubeMX 生成的 `stm32f1xx_it.c` 里写了 `HardFault_Handler` 函数，启动文件里的弱版本就自动被顶替。**这套机制让「默认死循环兜底 + 用户按需覆盖」成为可能**——你没写的中断处理都指向死循环，芯片出错时停在原地等调试器，而不是乱跑。

### 3.6 `STM32F103xx_FLASH.ld` —— 链接脚本（内存布局说明书）

`.ld`（linker script）不是 C 也不是汇编，是**链接器读的专用语言**。它回答三个问题：内存有多大、程序各段放哪、栈和堆留多少。

**① 内存地图**：

```
MEMORY
{
  RAM (xrw)   : ORIGIN = 0x20000000, LENGTH = 20K   ← 运行时变量区
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 64K   ← 程序代码区
}
```

> [!note] 术语
> **内存映射（memory map）**：芯片把所有寄存器和内存统一编址到一张地址表上。Flash 从 0x08000000 开始，RAM 从 0x20000000 开始，外设寄存器从 0x40000000 开始。**0x08000000 就是烧录地址**——上一课 `st-flash write xxx.bin 0x8000000` 烧的就是这个位置。

**② 段（section）的放置规则**：

| 段名 | 内容 | 放哪 |
|---|---|---|
| `.isr_vector` | 中断向量表 | Flash 最开头（地址 0） |
| `.text` | 你的代码（编译出的指令） | Flash |
| `.rodata` | 常量（字符串、const 变量） | Flash |
| `.data` | 有初值的全局变量 | **运行时在 RAM，初值备份在 Flash**（`AT> FLASH`） |
| `.bss` | 无初值的全局变量 | RAM（上电清零） |
| `._user_heap_stack` | 堆 + 栈的预留空间 | RAM 末尾 |

**③ 栈与堆的大小**：

```
_estack = ORIGIN(RAM) + LENGTH(RAM);  /* 栈顶 = RAM 最高地址，向下生长 */
_Min_Heap_Size  = 0x200;              /* 堆 512B（malloc 的地盘） */
_Min_Stack_Size = 0x400;              /* 栈 1KB（函数调用的地盘） */
```

> [!note] 术语（重点）
> **栈（stack）**：函数调用时存放局部变量、返回地址的内存区，先进后出，编译器自动管理。**栈溢出**（比如递归太深）是嵌入式最常见的死机原因之一。
> **堆（heap）**：`malloc` 动态分配的内存区，程序员手动管理。裸机上堆通常只留几百字节（`sysmem.c` 管它）。
> **LMA / VMA（装载地址 / 运行地址）**：`.data` 段「初值存 Flash（LMA）、运行时在 RAM（VMA）」的机制，由 `AT> FLASH` 语法实现。启动文件的拷贝循环就是把 LMA 的数据搬到 VMA。
> **段（section）**：编译器/链接器把相同性质的内容打包的「集装箱」：代码进 .text、常量进 .rodata、变量进 .data/.bss。

链接脚本和启动文件通过**符号**配合：脚本定义 `_sidata/_sdata/_edata/_sbss/_ebss/_estack` 等地址符号，汇编代码引用它们。**它们是同一个团队的暗号**——这就是为什么改内存大小（比如栈太小）要改 `.ld`，而不是改 `.c`。

---

## 四、`Core/` —— 你的代码（重点中的重点）

### 4.1 `Src/main.c` —— 主程序（你唯一天天要看的文件）

打开 main.c，从整体看它的结构是「模板骨架 + 保护区」：

```c
/* ① 头文件区 */        #include "main.h"
/* ② 保护区区块群 */    USER CODE BEGIN/END（Includes/PTD/PD/PV/PFP…）
/* ③ 函数声明区 */      SystemClock_Config / MX_GPIO_Init 的声明
/* ④ main() */          程序入口
/* ⑤ 初始化函数 */      SystemClock_Config()、MX_GPIO_Init() 的实现
/* ⑥ 错误处理 */        Error_Handler()
```

按**代码类别**看，main.c 里只有 3 类代码：

| 类别 | 代表 | 特点 |
|---|---|---|
| **初始化配置类** | `SystemClock_Config()`、`MX_GPIO_Init()` | CubeMX 生成，别手改（要改配置去 .ioc） |
| **业务逻辑类** | while(1) 里的点灯代码 | **你的主场**，写在 USER CODE 区 |
| **兜底处理类** | `Error_Handler()` | 任何初始化失败都跳进来死循环 |

**④ main() 执行流逐行精读**（这是整节课最重要的一张图）：

```c
int main(void)
{
  HAL_Init();             // ① HAL 库总初始化
                          //    - 配置 SysTick 为 1ms 节拍（HAL_Delay 的计时基准）
                          //    - 配置 Flash 预取
                          //    - 设置 NVIC 中断优先级分组

  SystemClock_Config();   // ② 配置时钟树
                          //    本工程：HSI 内部 8MHz 直接当系统时钟，没用 PLL
                          //    （0001 里讲的 8MHz 晶振×PLL=72MHz 是外部晶振方案，
                          //     本板没接外部晶振，所以 CubeMX 自动选了 HSI 方案）

  MX_GPIO_Init();         // ③ 配置 GPIO：把 PA6 设为推挽输出，初始低电平

  while (1)               // ④ 主循环（嵌入式程序永不返回）
  {
    HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);  // PA6 电平翻转
    HAL_Delay(500);                              // 等 500ms
  }
}
```

**④ 的代码就是点灯的全部逻辑**：翻转 → 等 500ms → 翻转 → 等 500ms…… 每 1 秒完成一个亮灭周期。

**每一个 HAL 调用背后发生了什么**（下钻到寄存器层，理解「HAL 帮你干了什么」）：

| 你写的 | 它内部实际做的（寄存器级） |
|---|---|
| `HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_6)` | 读 `GPIOA->ODR` 寄存器的第 6 位 → 异或翻转 → 写回（LED 状态取反） |
| `HAL_Delay(500)` | 死循环查 `uwTick` 全局变量，直到它增长 500ms。`uwTick` 由 SysTick 中断每 1ms 加 1（`stm32f1xx_it.c` 的 `HAL_IncTick()`） |
| `HAL_GPIO_WritePin(...)` | 直接写 `GPIOA->BSRR` 寄存器（置位/复位引脚） |

> [!note] 术语
> **GPIO（General Purpose I/O，通用输入输出）**：芯片的「引脚控制员」。每个引脚可以配置成输入（读电平）或输出（写电平）。
> **推挽输出（push-pull output）**：引脚既能输出高电平也能输出低电平，且驱动能力强（用两个晶体管「推」和「挽」）。控制 LED 用这个模式。对应的还有开漏输出（open-drain），接 I2C 总线等特殊场合用。
> **上拉/下拉（pull-up/down）**：引脚悬空时电平不确定，用内部电阻把它「拉」到固定电平。本工程 LED 引脚用 `GPIO_NOPULL`（不需要）。
> **GPIO_InitTypeDef**：HAL 的「配置单」结构体——把 Pin/Mode/Pull/Speed 四个参数填好，传给 `HAL_GPIO_Init()` 一次性生效。HAL 的通用套路：**先填结构体，再调用 Init 函数**。
> **SysTick**：Cortex-M3 内核自带的 24 位倒计时定时器，HAL 用它产生 1ms 心跳。`HAL_Delay`、`HAL_GetTick` 都靠它。
> **HSI（High Speed Internal，内部高速时钟）**：芯片内置的 8MHz RC 振荡器，精度一般但免外部晶振。与之相对 **HSE** 是外部晶振。本工程用 HSI 直通（8MHz 主频），后续火控云台若要精确波特率（串口），建议改用外部晶振 + PLL 到 72MHz。
> **时钟树（clock tree）**：时钟信号从源头分给各外设的路径配置（0001 已收录）。

**⑤ 初始化函数**——`MX_GPIO_Init()` 的代码类别是「配置类」，里面做的事：

```c
__HAL_RCC_GPIOA_CLK_ENABLE();          // 打开 GPIOA 外设的时钟（先开电，才能用）
HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);  // 初始：输出低电平
GPIO_InitStruct.Pin  = LED_Pin;        // 哪根引脚
GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;   // 推挽输出
GPIO_InitStruct.Pull = GPIO_NOPULL;    // 不带上拉/下拉
GPIO_InitStruct.Speed= GPIO_SPEED_FREQ_LOW;   // 低速档（LED 够用，还省干扰）
HAL_GPIO_Init(LED_GPIO_Port, &GPIO_InitStruct);  // 配置生效
```

> [!note] 术语
> **外设时钟开关（clock enable）**：STM32 的所有外设默认**断电**，用之前必须「打开它的时钟」（`__HAL_RCC_XXX_CLK_ENABLE()`）。这是省电设计，也是新手最容易漏的一步（漏了则寄存器操作无效）。
> **配置单模式**：HAL 的 Init 函数普遍采用「填结构体 → 调用」模式。看到 `XXX_InitTypeDef` 就知道是配置单。

**⑥ `Error_Handler()`** —— 所有 HAL 初始化函数失败时跳进来：

```c
void Error_Handler(void)
{
  __disable_irq();    // 关闭所有中断
  while (1) {}        // 死循环停住（红灯思维：出错就停下，方便调试器定位）
}
```

这是嵌入式「fail-stop（出错即停）」哲学：裸机上出错没有异常恢复机制，停住比乱跑好——乱跑的程序（跑飞）是最难查的 bug。

### 4.2 `Inc/main.h` —— main.c 的头文件（引脚宏定义之家）

```c
#ifndef __MAIN_H     // ← include guard（防止头文件被重复包含）
#define __MAIN_H
#ifdef __cplusplus   // ← 兼容 C++ 调用 C 函数（本项目不用，惯例保留）
extern "C" {
#endif

#include "stm32f1xx_hal.h"     // 一次性引入全部 HAL 头文件

void Error_Handler(void);      // 函数声明

#define LED_Pin GPIO_PIN_6     // ★ 引脚宏：LED = PA6 的第 6 位
#define LED_GPIO_Port GPIOA    // ★ 端口宏：LED 在 GPIOA

#ifdef __cplusplus
}
#endif
#endif
```

**两个宏是 CubeMX 从 .ioc 的 `PA6.GPIO_Label=LED` 生成的**——你在 CubeMX 里给引脚起的名字，到这里变成代码里能用的常量。这就是为什么代码里写 `LED_Pin` 而不是裸写 `GPIO_PIN_6`：**改名只改 .ioc，代码不用动**。

> [!note] 术语
> **宏（macro）**：`#define` 定义的文本替换。编译前预处理器把所有 `LED_Pin` 替换成 `GPIO_PIN_6`。HAL 库大量用宏：`GPIO_PIN_6` 就是 `((uint16_t)0x0040)` 的宏（二进制第 6 位）。
> **include guard（包含守卫）**：`#ifndef/#define/#endif` 三件套，防止同一个头文件被多个 .c 包含时重复定义报错。所有头文件都该有。

### 4.3 `Src/stm32f1xx_it.c` —— 中断服务程序（ISR 之家）

> [!note] 术语
> **中断（interrupt）**：硬件突然通知 CPU「有事了」，CPU 暂停手头的活，跳去执行对应的处理函数（ISR），完事再回来继续。就像你写代码时电话响了：放下代码（保存现场）→ 接电话（执行 ISR）→ 挂电话（恢复现场）→ 继续写。
> **ISR（Interrupt Service Routine，中断服务程序）**：中断到来时执行的函数。**ISR 里不能干耗时的事**（比如 HAL_Delay），否则会阻塞主循环。
> **NVIC（Nested Vectored Interrupt Controller，嵌套向量中断控制器）**：Cortex-M3 的中断管理硬件，管「哪个中断优先、谁来打断谁」。

本文件目前有意义的只有两个：

| 函数 | 作用 |
|---|---|
| `SysTick_Handler()` | 每 1ms 被 SysTick 中断调用，执行 `HAL_IncTick()` 把 `uwTick` 加 1 —— **`HAL_Delay(500)` 就是靠它计时的** |
| `HardFault_Handler()` 等一堆 | 死循环兜底（数组越界、野指针等致命错误都会进 HardFault） |

**以后学串口接收，中断处理函数就要加在这个文件里**——它的代码类别是「中断处理类」，CubeMX 会在你没勾选任何外设中断时，让这个文件保持最小化。

### 4.4 `Src/stm32f1xx_hal_msp.c` —— MSP：外设的「接线员」

> [!note] 术语
> **MSP（MCU Support Package，微控制器支持包）**：HAL 的「三段式」结构之一——外设初始化拆成两层：
> 1. **HAL_Periph_Init()**（在 HAL 库里）：配置外设本身（波特率、模式…）
> 2. **HAL_Periph_MspInit()**（在你工程里）：配置外设的「外部环境」——引脚复用、打开时钟
> 分层的意义：HAL 库想保持芯片无关，而「哪根引脚接哪个外设」因板而异，所以这层留给用户工程。

当前文件里只有一个 `HAL_MspInit()`，干两件事：

```c
__HAL_RCC_AFIO_CLK_ENABLE();      // 打开 AFIO（引脚复用功能）时钟
__HAL_RCC_PWR_CLK_ENABLE();       // 打开电源管理外设时钟
__HAL_AFIO_REMAP_SWJ_NOJTAG();    // ★ 关掉 JTAG 引脚，只留 SWD（PA13/PA14）
```

> [!note] 术语
> **AFIO（Alternate Function I/O，复用功能）**：F1 系列的外设引脚复用开关。引脚既可以当 GPIO，也可以当 USART/TIM 等外设的功能脚，AFIO 决定「当前是谁在用」。
> **SWJ_REMAP_NOJTAG**：调试口重映射——F103 上 JTAG 和 SWD 共用 5 根引脚，这条宏关掉占用 PA15/PB3/PB4 的 JTAG，只保留 SWD 的 PA13/PA14。**这样你就能拿 PA15/PB3/PB4 当普通 GPIO 用了**（火控云台要接舵机 PWM 时会用到）。

### 4.5 `Src/syscalls.c` + `Src/sysmem.c` —— C 库的「胶水层」（裸机 C 语言的地基）

在 Linux 上，`printf` 由操作系统帮忙输出到屏幕；`malloc` 由操作系统分配内存。**STM32 没有操作系统**（裸机），C 标准库不知道去哪输出、去哪分配——所以 CubeMX 生成这两个文件，把「后门」留给你：

**`sysmem.c` —— malloc 的内存来源**：

```c
void *_sbrk(ptrdiff_t incr)   // malloc 内部会调它："我要 incr 字节"
{
  // 从链接脚本的 _end 符号（.bss 之后）开始分配
  // 上限：RAM 顶减去栈保护区（_estack - _Min_Stack_Size）
  // 越界则返回 -1（内存不足）
}
```

> [!note] 术语
> **_sbrk**：C 库堆分配器（malloc 族）的底层钩子。裸机上必须自己实现它，否则 malloc 崩。它维护一个「水位指针」，从低地址往高地址一块块发内存。**堆用完的标志是 malloc 返回 NULL**——嵌入式里要检查。

**`syscalls.c` —— printf 的出口**：

```c
__attribute__((weak)) int _write(int file, char *ptr, int len)
{
  for (int i = 0; i < len; i++) __io_putchar(*ptr++);  // printf 每个字符都进这里
  return len;
}
```

**这就是以后「printf 重定向到串口」的钩子**：你只要在工程里实现 `__io_putchar`（把字符发到 USART），printf 就能通过串口在电脑上打印。这套机制在 0003 串口课会用到，现在知道「printf 从哪出来」就行。

> [!note] 术语
> **系统调用桩（syscall stub）**：C 库需要但裸机没有的系统功能（读、写、退出、杀进程…），提供最小实现占位。`_write/_read/_kill/_getpid` 都是桩。多数桩直接返回 -1（表示「不支持」），因为裸机不需要。
> **newlib / picolibc**：嵌入式常用的精简 C 标准库实现。`--specs=nano.specs`（见 4.7）就是让链接器用精简版 newlib。
> **weak 属性**：`__attribute__((weak))` 让 `_write` 成为弱符号——你以后实现自己的 `_write` 就能覆盖它。

### 4.6 `Src/system_stm32f1xx.c` + `Inc/stm32f1xx_hal_conf.h`

| 文件 | 角色 | 关键内容 |
|---|---|---|
| `system_stm32f1xx.c` | 系统初始化 | 实现 `SystemInit()`：设置 Flash 等待周期、复位时钟到默认状态。**被启动文件在 main 之前调用**（启动文件里的 `bl SystemInit`） |
| `stm32f1xx_hal_conf.h` | HAL 总闸 | `#define HAL_GPIO_MODULE_ENABLED` 这类宏决定编译哪些 HAL 模块。勾选的外设越多、代码越大，一般不用动 |

> [!note] 术语
> **Flash 等待周期（wait states）**：Flash 比 CPU 慢，CPU 主频高时必须插入等待周期才能稳定读 Flash。F103 在 8MHz 时 0 个等待周期，72MHz 时需要 2 个。`SystemInit` 里自动处理。
> **HAL_MODULE_ENABLED**：HAL 库的模块开关宏。`stm32f1xx_hal_conf.h` 里 `#define HAL_XXX_MODULE_ENABLED` 开着的模块才会被编译进去。

### 4.7 `Core/Inc/stm32f1xx_it.h` —— 中断文件的头文件

声明 `SysTick_Handler` 等中断函数。没有新概念，看一眼即可。

---

## 五、`Drivers/` —— ST 官方库（只读，永远不改）

### 5.1 `Drivers/CMSIS/` —— 内核标准库（最底层）

> [!note] 术语
> **CMSIS（Cortex Microcontroller Software Interface Standard，Cortex 微控制器软件接口标准）**：ARM 官方定的「内核统一标准」，让不同芯片厂商的代码风格一致。两层：
> - `core_cm3.h`：Cortex-M3 **内核**的寄存器定义（NVIC、SysTick、异常）——任何 M3 芯片都一样
> - `stm32f103xb.h`：STM32F103 这个**具体芯片**的寄存器定义（GPIOA、USART1、TIM2…的地址和位定义）——ST 生成
>
> **这两层加起来 = 「硬件地图」**。HAL 库和你的代码最终都编译成对这些地址的读写。`GPIOA->ODR` 里的 `GPIOA` 就是在 `stm32f103xb.h` 里定义成 `((GPIO_TypeDef *)0x40010800)` 的宏。

**你会在什么时候碰它**：查寄存器定义时（比如想知道某个外设寄存器在哪），打开这两个头文件搜。阅读它们 > 修改它们。

### 5.2 `Drivers/STM32F1xx_HAL_Driver/` —— HAL 外设驱动（现成函数库）

`Src/` 下每个 `.c` 管一类外设：

| 文件 | 管什么 | 你已经在用 |
|---|---|---|
| `stm32f1xx_hal_gpio.c` | GPIO：读写引脚 | `HAL_GPIO_TogglePin`、`HAL_GPIO_Init` |
| `stm32f1xx_hal_rcc.c` + `_ex.c` | 时钟树 | `HAL_RCC_OscConfig`、`__HAL_RCC_GPIOA_CLK_ENABLE` |
| `stm32f1xx_hal.c` | HAL 核心 | `HAL_Init`、`HAL_Delay`、`HAL_IncTick` |
| `stm32f1xx_hal_cortex.c` | 内核集成 | NVIC、SysTick 配置 |
| `stm32f1xx_hal_flash.c` | Flash 操作 | 等待周期设置 |
| `stm32f1xx_hal_pwr.c` | 电源管理 | PWR 时钟 |
| `stm32f1xx_hal_dma.c` | DMA | 目前未用（CubeMX 默认勾了） |
| `stm32f1xx_hal_exti.c` | 外部中断 | 目前未用 |
| `Inc/` 下对应 `.h` | 头文件 | 声明 + 宏 + 结构体定义 |

**注意：并不是所有 HAL 模块都被编译**——只编译你实际需要的（编译清单见 6.2）。想加 UART？CubeMX 勾上 USART → 重新生成 → `stm32f1xx_hal_uart.c` 自动进清单。

> [!note] 术语
> **HAL（Hardware Abstraction Layer，硬件抽象层）**：0001 已收录。ST 官方把寄存器操作封装成函数库，「调函数」代替「写寄存器」。**本课程主线全部用 HAL**。
> **DMA（Direct Memory Access，直接内存访问）**：外设和内存之间不经过 CPU 直接搬数据。进阶话题，本项目暂不用。

---

## 六、`cmake/` —— 构建系统（编译的「配方」）

### 6.1 `gcc-arm-none-eabi.cmake` —— 工具链文件（编译器说明书）

CMake 默认会用本机编译器（x86 的 gcc），但我们的目标芯片是 ARM——所以需要这个文件告诉 CMake：「用 arm-none-eabi-gcc 这套交叉编译工具，并且带上这些专用参数」：

| 关键行 | 含义 |
|---|---|
| `set(CMAKE_C_COMPILER arm-none-eabi-gcc)` | 指定交叉编译器 |
| `-mcpu=cortex-m3` | 按 Cortex-M3 架构生成指令 |
| `-ffunction-sections -fdata-sections` | 每个函数/变量独立成段（配合 `--gc-sections` 删没用代码，省 Flash） |
| `-T STM32F103xx_FLASH.ld` | 链接时使用本工程的链接脚本 |
| `--specs=nano.specs` | 用精简版 C 库（newlib-nano，省 Flash） |
| `-Wl,-Map=DDM_test.map` | 生成 map 文件（内存使用清单，链接完可看） |
| Debug: `-O0 -g3` / Release: `-Os` | 优化等级与调试信息 |

> [!note] 术语
> **交叉编译（cross-compile）**：0001 已收录——x86 电脑编译出 ARM 机器码。
> **map 文件**：链接器输出的「每个符号放在哪个地址」的清单。**程序诡异崩溃时，看 map 文件能查出变量/栈的排布**。它在 `build/Debug/DDM_test.map`。
> **gc-sections（垃圾回收段）**：链接时丢弃没有被引用的函数，避免 HAL 库全量塞进 Flash。配合 `-ffunction-sections` 使用。

### 6.2 `cmake/stm32cubemx/CMakeLists.txt` —— 编译清单（唯一被 CubeMX 每次重写的构建文件）

这个文件是**真正的「哪些文件参与编译」清单**，共 4 个部分：

**① 宏定义（3 个）**：
```cmake
USE_HAL_DRIVER      # 让 HAL 库启用（HAL 头文件里大量 #ifdef USE_HAL_DRIVER）
STM32F103xB         # 芯片型号（决定用 stm32f103xb.h 还是其他型号的头文件）
DEBUG               # 仅 Debug 配置才定义（$<$<CONFIG:Debug>:DEBUG>）
```

> [!note] 术语
> **编译宏（compile definition）**：编译时全局生效的 `#define`。**宏决定了「编译哪些代码分支」**——HAL 库靠 `USE_HAL_DRIVER` 和 `STM32F103xB` 知道自己该支持什么芯片。

**② 头文件搜索路径（5 个）**：
```cmake
Core/Inc                    # 你的头文件
Drivers/STM32F1xx_HAL_Driver/Inc（含 Legacy）
Drivers/CMSIS/Device/ST/STM32F1xx/Include   # stm32f103xb.h
Drivers/CMSIS/Include                        # core_cm3.h
```

> [!note] 术语
> **include 路径（include path）**：`#include "xxx.h"` 时的搜索目录列表。头文件分布在不同文件夹，编译器需要这个清单才能找到它们。

**③ 应用源码（6 个文件）**：`main.c`、`stm32f1xx_it.c`、`stm32f1xx_hal_msp.c`、`sysmem.c`、`syscalls.c`、`startup_stm32f103xb.s` —— 加上链接脚本，这就是「你的工程」的全部编译单元。

**④ HAL 驱动源码（12 个 .c）**：`system_stm32f1xx.c` + 11 个 HAL 模块（见 5.2 表）。打包成名为 `STM32_Drivers` 的 OBJECT 库，再通过 `stm32cubemx` 接口库把宏和路径传给主目标。

> [!note] 术语
> **OBJECT 库 / INTERFACE 库**：CMake 的两种库类型。OBJECT 库 = 「只编译不打包」的中间产物集合；INTERFACE 库 = 「只传配置不产文件」（宏、路径、选项顺着依赖链传给使用者）。本工程用这两者把 HAL 的编译细节封装起来。
> **add_library / add_executable**：声明库/可执行文件的 CMake 命令（见 3.3 术语 target）。

> [!warning] 重点坑：这个文件会被 CubeMX 重写
> `cmake/stm32cubemx/CMakeLists.txt` 是 **CubeMX 每次重新生成都会重写的文件**。**不要往这里加你自己的源码**——重新生成就没了。你自己新建的 `.c` 文件加在根 `CMakeLists.txt`（只生成一次），或者干脆把新代码写进 `Core/` 已有文件 + 手动加根 CMakeLists（更稳）。

---

## 七、编译产物流：全链路数据流（把本课串起来）

```
                        ★ 你只在这里操作 ★
                              │
                     DDM_test.ioc（改配置）
                              │ CubeMX "Generate Code"
                              ▼
      ┌─────────────────────────────────────────────┐
      │ Core/   Drivers/   startup.s   .ld   cmake/ │   ← 本课拆解的全部文件
      └─────────────────────────────────────────────┘
                              │
              CMakePresets.json → CMake 读取 CMakeLists.txt（根）→ 引入 cmake/stm32cubemx
                              │ 生成 Ninja 构建文件
                              ▼
              arm-none-eabi-gcc 按 gcc-arm-none-eabi.cmake 编译全部源码
                              │ 链接（用 STM32F103xx_FLASH.ld 决定放哪）
                              ▼
                build/Debug/DDM_test.elf  ← 编译产物（含调试信息）
                              │ arm-none-eabi-objcopy 转 .bin
                              ▼
                st-flash write ... 0x08000000  ← 烧录（0001 已做过）
                              │
              芯片上电 → 启动文件 → 搬 .data/清 .bss → main()
                              ▼
                      LED 以 1Hz 闪烁 ★
```

每个环节的产物和负责工具：

| 环节 | 输入 → 输出 | 工具 |
|---|---|---|
| 配置 | `.ioc` → 全部源码文件 | CubeMX |
| 构建 | 源码 → 构建文件（ninja） | CMake |
| 编译 | 源码 → 目标文件 → .elf | arm-none-eabi-gcc |
| 烧录 | .elf/.bin → Flash | st-flash（ST-Link） |
| 运行 | Flash → 上电执行 | 启动文件 + main() |

---

## 八、术语详解：本课全量清单

> 收录标准：本课出现的每个专业术语，一条**详细解释**（定义 + 类比 + 本工程落点）。已入 [[教学-STM32/reference/术语表|课程术语表]] 的标 📖。

### A. 硬件与芯片

| 术语 | 详细解释 |
|---|---|
| **MCU** 📖 | 微控制器：一块芯片集成 CPU+存储+外设。本工程 STM32F103C8T6 = Cortex-M3 内核 + 64KB Flash + 20KB RAM + 一堆外设 |
| **Flash** 📖 | 非易失存储（掉电不丢），64KB，从地址 0x08000000 开始。程序代码和常量住这里。烧录就是把 .bin 写进这里 |
| **RAM** 📖 | 易失存储（掉电清空），20KB，从 0x20000000 开始。运行中的变量、栈、堆住这里。**容量只有 Flash 的 1/3**，全局变量别乱开大数组 |
| **寄存器** 📖 | 硬件的最小操作单位，通过内存地址读写。`GPIOA->ODR` 就是 GPIOA 的输出数据寄存器（地址 0x4001080C）。HAL 帮你把它藏起来了 |
| **内存映射** | 芯片把 Flash/RAM/外设寄存器统一编进一张地址表。写代码其实就是「对特定地址读写」 |
| **GPIO** 📖 | 通用输入输出：引脚控制员。F103 的 GPIOA~G 共 7 组 × 16 脚（PA0~PA15…） |
| **推挽输出** | 引脚能强驱动高/低两种电平。控制 LED、舵机信号线用它 |
| **上拉/下拉** | 引脚悬空时电平漂移，内部电阻强制拉高/拉低。按键输入常用上拉 |
| **SysTick** | 内核自带 24 位倒计时定时器，HAL 配成 1ms 心跳。`HAL_Delay`/`HAL_GetTick` 都靠它 |
| **时钟树** 📖 | 时钟分发图。本工程：HSI 8MHz → 直通 SYSCLK（无 PLL）。003 串口课要升级到 72MHz |
| **HSI / HSE** | 内部高速时钟（8MHz RC，免晶振，精度一般）vs 外部高速时钟（需要晶振，精度高）。F103 经典方案是 HSE×PLL=72MHz |
| **外设** 📖 | CPU 与存储之外的功能模块：GPIO=手，UART=嘴，TIM=节拍器 |
| **中断** | 硬件打断 CPU 的机制。SysTick 每 1ms 中断一次，CPU 去执行 `SysTick_Handler` 再回来 |
| **NVIC** | 中断控制器硬件：管优先级和嵌套。`HAL_Init` 时配优先级分组 |
| **Flash 等待周期** | Flash 慢于 CPU 时插入的等待。8MHz 无需等待，72MHz 需 2 周期 |

### B. 工程与生成器

| 术语 | 详细解释 |
|---|---|
| **CubeMX** 📖 | ST 官方图形化配置工具：勾选外设 → 生成初始化代码。教学主线固定用它 |
| **.ioc** 📖 | CubeMX 配置档案（纯文本），工程的「大脑」。改配置的正路是 GUI 改 .ioc 再重新生成 |
| **代码生成** 📖 | .ioc → 源码文件的自动化过程 |
| **USER CODE 区** 📖 | `USER CODE BEGIN/END` 之间的保护区。**手写代码必须放这里**，否则被重写覆盖 |
| **HAL** 📖 | ST 官方硬件抽象层函数库，教学主线使用层 |
| **CMSIS** | ARM 官方内核标准：`core_cm3.h`（内核寄存器）+ `stm32f103xb.h`（芯片寄存器） |
| **MSP** | HAL 的「三段式」之一：外设的引脚/时钟等板级配置（`stm32f1xx_hal_msp.c`） |
| **AFIO** | F1 的引脚复用开关，决定引脚当前属于哪个外设。`SWJ_NOJTAG` 用它释放 JTAG 引脚 |

### C. 编译与链接

| 术语 | 详细解释 |
|---|---|
| **交叉编译** 📖 | x86 电脑产出 ARM 机器码。工具链文件 `gcc-arm-none-eabi.cmake` 就是干这个的 |
| **工具链** 📖 | 编译器+构建系统+烧录器的全家桶（0001 已收录） |
| **CMake** 📖 | 构建系统：读规则、生成构建文件，不直接编译 |
| **Ninja** | 构建执行器（编译的实际执行者），比 make 快 |
| **preset** 📖 | CMake 预定义方案（Debug/Release），VS Code 一键选用 |
| **target** | CMake 构建单元（可执行文件/库），把源码、路径、宏打包 |
| **宏（编译宏）** | 全局 `#define`，决定代码编译哪个分支：`USE_HAL_DRIVER`、`STM32F103xB` |
| **include 路径** | `#include` 的搜索目录清单，5 个路径见 6.2 |
| **启动文件** | 上电后第一段代码：配栈、向量表、搬 .data、清 .bss、跳 main。`startup_stm32f103xb.s` |
| **中断向量表** | 「中断号 → 处理函数」对照表，固定在 Flash 开头（地址 0） |
| **弱符号** | 可被覆盖的定义。启动文件给所有中断提供死循环默认值，用户定义同名函数即覆盖 |
| **链接脚本** | 内存布局说明书（`.ld`）：地址、段、栈堆大小 |
| **段（section）** | 内容的集装箱：.text（代码）/ .rodata（常量）/ .data（有初值变量）/ .bss（无初值变量） |
| **LMA / VMA** | 装载地址（初值存哪）/运行地址（运行时在哪）。`.data` 段 LMA 在 Flash、VMA 在 RAM，启动文件负责搬运 |
| **栈** | 函数调用内存区（局部变量、返回地址），先进后出，编译器管理。1KB，在 RAM 顶部向下生长 |
| **堆** | malloc 内存区，`sysmem.c` 的 `_sbrk` 管理。512B |
| **_sbrk** | malloc 的底层内存分配钩子，裸机必须实现 |
| **系统调用桩** | C 库系统功能的占位实现（_write/_read/_exit…），裸机场景多数直接失败返回 |
| **newlib(-nano)** | 嵌入式精简 C 库。`--specs=nano.specs` 启用 |
| **.elf / .bin / .map** | .elf = 带调试信息的完整程序；.bin = 纯二进制（烧录用）；.map = 符号地址清单（排障用） |
| **gc-sections** | 链接时删除没被引用的函数/数据，省 Flash。配合 -ffunction-sections 使用 |
| **OBJECT/INTERFACE 库** | CMake 两种库：OBJECT=只编译的中间集合；INTERFACE=只传配置不产文件 |

### D. 烧录与调试

| 术语 | 详细解释 |
|---|---|
| **烧录** 📖 | .bin/.elf 写入 Flash（0x08000000）。st-flash 完成 |
| **SWD** 📖 | 串行线调试协议，4 线（SWDIO/SWCLK/GND/3.3V）。PA13/PA14 |
| **ST-Link** 📖 | ST 官方烧录/调试器 |
| **JTAG** | 另一种调试协议（5 线）。F103 上 JTAG 与 SWD 引脚重叠，工程默认关 JTAG 保 SWD |

### E. main.c 里的代码级术语

| 术语 | 详细解释 |
|---|---|
| **GPIO_InitTypeDef** | HAL 的「配置单」结构体，填好 Pin/Mode/Pull/Speed 传给 `HAL_GPIO_Init` |
| **HAL_GPIO_TogglePin** | 翻转引脚：读 ODR → 异或 → 写回 |
| **HAL_Delay(ms)** | 忙等待毫秒数：死循环查 uwTick（SysTick 中断每 1ms +1） |
| **Error_Handler** | 初始化失败兜底：关中断 + 死循环（fail-stop 哲学） |
| **include guard** | `#ifndef/#define/#endif` 防重复包含 |
| **extern "C"** | C++ 兼容声明（C++ 名字修饰与 C 不同，这行防止链接失败） |

---

## 九、练习（动手才能记住）

> [!example] 练习 1（10 分钟）：文件「改动权」分类
> 不看笔记，把以下文件分到三类：**A 放心改 / B 只能改 USER CODE 区 / C 永远别改**
>
> `main.c` · `startup_stm32f103xb.s` · `stm32f1xx_hal_conf.h` · `STM32F103xx_FLASH.ld` · `stm32f1xx_hal_gpio.c` · `sysmem.c` · `stm32f1xx_hal_msp.c` · `cmake/stm32cubemx/CMakeLists.txt` · `DDM_test.ioc`
>
> 提示：想「B 和 C 的本质区别是什么」——一个是生成模板，一个是拷进来的库。

> [!example] 练习 2（15 分钟）：改代码看效果（需板子；无板子就只改不烧）
> 1. 打开 `Core/Src/main.c`，把 `HAL_Delay(500)` 改成 `HAL_Delay(100)`（在 USER CODE 区内！）
> 2. 编译 + 烧录，观察闪烁变快 5 倍
> 3. 改回来。再试：在 while 循环里加一句 `HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);`（这样每次循环翻两次）——**先写下你预测的现象再烧**，观察对不对

> [!example] 练习 3（10 分钟）：概念复述
> 不看笔记，用 3 句话解释：
> ① 为什么程序要「烧录」进 Flash 而不是 RAM？
> ② 上电后到 `main()` 之间，启动文件干了哪 4 件事？
> ③ 为什么 `cmake/stm32cubemx/CMakeLists.txt` 里不能加自己的源码文件？
> ④ `printf` 在裸机上为什么不能直接用？（提示：`_write` 桩）

> [!example] 练习 4（进阶挑战，20 分钟）：追一个宏的源头
> 1. 在 `main.c` 里 `HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin)` 上按 F12（VS Code）跳转，一路跟进 HAL 库源码
> 2. 找到它最终写寄存器的代码（应该看到 `GPIOx->BSRR` 或 `ODR` 操作）
> 3. 写一句话：从你写的代码到寄存器，中间隔了几层？

---

## 十、本课回顾（用回忆检验，别看上面）

- 这个工程里哪些文件会被 CubeMX 重新生成覆盖？覆盖时你的手写代码为什么没事？
- 中断向量表的第一项和第二项分别是什么？为什么它必须放在 Flash 开头？
- `.data` 和 `.bss` 段的区别？启动文件对它们分别做了什么？
- 栈和堆分别在哪块内存区？各归谁管理？本工程各多大？
- `HAL_Delay(500)` 的计时原理（哪两个文件配合）？
- 想改引脚（比如换到 PA5），正确流程是什么？哪些文件会被自动更新？

## 关联

- 上一课：[[教学-STM32/lessons/0001-工具链闭环与LED闪烁|0001 工具链闭环与 LED 闪烁]]
- 下一课：[[教学-STM32/lessons/0003-PWM控制舵机|0003 · PWM 控制舵机]]（SG90 转角 = 脉宽映射，里程碑：舵机转起来）
- 精读笔记：[[教学-STM32/reference/0002b-stm32f1xx_hal.h逐行精读与C语法复习|0002b · stm32f1xx_hal.h 逐行精读 + C 语法复习]]
- 术语表：[[教学-STM32/reference/术语表|STM32 课程术语表]]
- 任务书：[[教学-STM32/MISSION.md|Mission]]
- 速查表：[[教学-STM32/reference/0001-工具链速查|工具链速查表]]
- 今日进度：[[每日日志/2026-08-11|2026-08-11 每日日志]]
