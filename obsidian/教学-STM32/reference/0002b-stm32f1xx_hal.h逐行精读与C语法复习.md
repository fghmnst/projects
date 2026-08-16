# Lesson 0002b · stm32f1xx_hal.h 逐行精读 + C 语法复习

> 本笔记是 [[教学-STM32/lessons/0002-CubeMX工程结构解剖-DianDengMaster逐文件精读|0002 课]] 的附属阅读材料：把 HAL 库总入口头文件 **逐行拆开**，所有注释翻译成中文，所有 C 语法点批注在源码旁边。
> 前置：0002 课（了解工程结构）＋基础 C 语法（变量/函数/指针概念）。本笔记会**顺带把 C 语法复习一遍**。
> 配套文件：`DDM_test/Drivers/STM32F1xx_HAL_Driver/Inc/stm32f1xx_hal.h`（共 357 行）

## 本篇笔记怎么用

1. 先读「一、这是什么文件」—— 建立整体地图
2. 再读「二、阅读前：C 语法点清单」—— 把 10 个语法点变成自己的行囊
3. 然后逐节读「三、逐行精读」—— 同一语法点第二次出现只写「→ 见 §」，不用回头也能跟上
4. 读完做「六、练习」—— **看懂 ≠ 记住**，不动手等于白读

---

## 一、这是什么文件：HAL 图书馆的中央大厅

把整个 HAL 库想成一座图书馆，每个外设（GPIO、UART、TIM…）是一层楼，各有自己的头文件（`stm32f1xx_hal_gpio.h` 等）。而本文件是**中央大厅**：

- **想进任何楼层都要经过大厅**：每个外设头文件的第一行几乎都是 `#include "stm32f1xx_hal.h"`
- 大厅里摆着全馆共用的三样东西：**一个时钟**（`uwTick`）、**一扇启动门**（`HAL_Init`）、**一个查册窗口**（版本/芯片 ID 查询）
- 大厅本身**不干外设的活**——它只管"公共设施"，所以只有 357 行，是 HAL 里最短的头文件之一

全景地图（按文件顺序）：

```
L1-18   楼门口的石碑：文件介绍 + 版权声明
L20-29  安检门：防重复包含 + C++ 兼容 + 拿 conf 钥匙
L31-43  楼层指示牌（Doxygen 分组标签，纯文档用）
L45-61  大厅的时钟：uwTick 及其频率
L66-262 紧急开关柜：DBGMCU 调试冻结宏（一大排，看不懂先跳过）
L264-272 私人物品架：IS_TICKFREQ 校验宏
L274-325 服务窗口：全部函数声明（重点）
L326-355 空房间 + 收尾
```

---

## 二、阅读前：C 语法点清单（本文件会出现的一切）

| # | 语法点 | 一句话 | 出现位置 |
|---|---|---|---|
| 1 | **预处理指令** | 以 `#` 开头、编译前由预处理器执行的指令（`#include`/`#define`/`#ifdef`） | 全文开头 |
| 2 | **include guard** | `#ifndef/#define/#endif` 三件套，防止头文件被重复包含 | §3 |
| 3 | **extern "C"** | 告诉 C++ 编译器：这段声明按 C 的符号规则编译，防止 C++ 链接时找不到名字 | §3 |
| 4 | **Doxygen 注释** | `/** ... */` 里带 `@` 标签的注释，可被工具生成文档；不影响编译 | §4、§5… |
| 5 | **typedef enum** | 给一组命名整数常量起一个新类型名 | §5 |
| 6 | **字面量后缀 `U`** | `100U` 表示无符号整数，避免隐式转换警告 | §5 |
| 7 | **extern 变量声明** | `extern` 表示"这个变量定义在别的文件"，这里只做声明 | §5 |
| 8 | **volatile / `__IO`** | 告诉编译器"这个变量可能被硬件/中断悄悄改掉"，每次用都必须重新读取 | §5 |
| 9 | **宏函数** | `#define 名字(参数) 替换体`——预处理时纯文本替换，不是真函数 | §6 |
| 10 | **宏续行符 `\`** | 宏太长时用行尾反斜杠换行 | §7 |
| 11 | **条件编译 `#if defined`** | 满足条件才编译这一段，按芯片裁剪代码 | §6 |
| 12 | **结构体指针访问 `->`** | `DBGMCU->CR`：通过指针访问结构体成员（寄存器） | §6 |
| 13 | **位掩码** | 一个数里的某一位代表一个开关，用 `|`/`&` 操作 | §6 |
| 14 | **函数声明 vs 定义** | 声明只有签名以 `;` 结尾；定义有 `{}` 函数体。头文件放声明，源文件放定义 | §8 |
| 15 | **弱函数（weak）** | 有默认实现的函数，用户可写同名函数覆盖（0002 学过 weak symbol） | §8 |

每一行后面标注的「§」就是下面「三、逐行精读」的小节号，边读边对照。

---

## 三、逐行精读

### §1 楼门口的石碑：文件头注释（L1-18）

```c
/**
  * @file    stm32f1xx_hal.h              // 文件名
  * @author  MCD Application Team         // 作者：ST 官方的 MCU 应用团队
  * @brief   本文件包含 HAL 模块驱动器的全部函数声明（原型）
  * @attention                             // 注意：版权声明
  *
  * 版权归 STMicroelectronics 所有（2017），
  * 使用条款见本软件根目录的 LICENSE 文件
  */
```

> [!info] 语法点 4：Doxygen 注释
> `/** */` 是 Doxygen 文档注释（`*` 开头的行只是装饰）。`@file`/`@author`/`@brief`/`@attention` 是**标签**，Doxygen 工具会按标签生成文档。**不影响编译**。VS Code 里把鼠标悬停在函数名上弹出的说明框，就是这种注释。

### §2 安检门：include guard + extern "C" + conf 钥匙（L20-29）

```c
/* 防止重复包含 -------------------------------------*/
#ifndef __STM32F1xx_HAL_H   // 预处理：如果 __STM32F1xx_HAL_H 这个宏还没被定义…
#define __STM32F1xx_HAL_H   // …就定义它，然后继续读下面内容
                            // 第二次再被包含时：第一个判断为假，整个文件被直接跳过

#ifdef __cplusplus          // 预处理：如果现在是 C++ 编译器在编译
extern "C" {                // 把大括号里所有声明按 C 的规则处理
#endif

/* 包含 ------------------------------------------------------------------*/
#include "stm32f1xx_hal_conf.h"  // 引入"总开关清单"：外设模块开关、晶振频率等
```

> [!info] 语法点 2：include guard
> 一套 `#ifndef → #define → #endif` 的"哨兵"。为什么需要？头文件会被很多文件包含，而 main.c 里可能同时 `#include` 了两个头文件，它们又都包含 `stm32f1xx_hal.h` —— 没有哨兵就会重复定义报错。哨兵保证：**同一个头文件只被完整读一次**。这是所有 C 头文件的通用套路。

> [!info] 语法点 1：预处理指令
> 以 `#` 开头的行是**预处理指令**：C 代码在真正编译前，先由「预处理器」处理一遍——做文本替换（`#define`）、按条件裁剪（`#ifdef`）、把别的文件内容原样搬进来（`#include`）。所以你看到的 `.h` 并不是"最终代码"，而是"原材料"。

> [!info] 语法点 3：extern "C"
> C++ 编译函数时会把函数名"装饰"成带参数信息的长名字（名字修饰 name mangling）；C 不会。如果 C++ 程序调用一个 C 写的函数（HAL 就是 C），两边名字对不上，链接报 `undefined reference`。`extern "C"` 就是声明："这块内容是 C 写的，请按 C 的规则找名字"。**只有用 C++ 写 STM32 程序时才生效**（`#ifdef __cplusplus` 保证纯 C 编译时这行被跳过）。我们的工程用 C，这行对你暂时是透明的。

> [!info] 语法点：`#include "x"` vs `#include <x>`
> 双引号：**先找当前文件所在目录**，找不到再去系统路径——工程内部头文件都用它。
> 尖括号：只找编译器配置的包含路径——标准库/库头文件用。本文件的 `"stm32f1xx_hal_conf.h"` 和它同目录，所以用双引号。

### §3 楼层指示牌：Doxygen 分组标签（L31-43）

```c
/** @addtogroup STM32F1xx_HAL_Driver   // 把下面内容归入"STM32F1xx HAL 驱动"大组
  * @{
  */
/** @addtogroup HAL                    // 再归入"HAL"小组
  * @{
  */
```

> [!info] 纯文档
> `@addtogroup` + `@{` 开组、`}`（在文件末尾）关组，是 Doxygen 用来组织文档结构的标签，**编译时不存在**。Obsidian 里的 MOC/索引文件夹思维和它类似——文件夹是为了人找东西方便。

### §4 大厅的时钟：枚举 + 全局变量（L45-61）

```c
/* 导出的常量 ------------------------------------------------------------*/

/** @defgroup HAL_TICK_FREQ 时钟频率
  * @{
  */
typedef enum                          // 定义一个"枚举类型"
{
  HAL_TICK_FREQ_10HZ   = 100U,        // 10Hz：每 100ms 跳一次
  HAL_TICK_FREQ_100HZ  = 10U,         // 100Hz：每 10ms 跳一次
  HAL_TICK_FREQ_1KHZ   = 1U,          // 1kHz：每 1ms 跳一次（默认值）
  HAL_TICK_FREQ_DEFAULT = HAL_TICK_FREQ_1KHZ  // "默认"这个名字 = 1kHz
} HAL_TickFreqTypeDef;                // 新类型名，分号结尾（typedef 语句和函数一样要以 ; 结束）

/* 导出的类型 ------------------------------------------------------------*/
extern __IO uint32_t uwTick;          // 系统时基计数器：每 1ms 被中断加 1
extern uint32_t uwTickPrio;           // 时基中断的优先级
extern HAL_TickFreqTypeDef uwTickFreq; // 当前时基频率
```

> [!info] 语法点 5：typedef enum
> `enum { A=1, B=2 }` 是一组命名的整数常量。`typedef` 给它起个类型名 `HAL_TickFreqTypeDef`，以后就能写 `HAL_TickFreqTypeDef f = HAL_TICK_FREQ_1KHZ;`。
> 成员名字 = 数值：`HAL_TICK_FREQ_1KHZ` 就是数字 `1`。
> **约定**：ST 给类型名都带 `TypeDef` 后缀，成员都带 `HAL_TICK_FREQ_` 前缀——长，但一看就知道是什么、从哪来。C 工程里类型名 `大驼峰`，变量名 `小驼峰`（`uwTick` 是历史命名：`u`=unsigned 无符号，`w`=word 32 位宽）。

> [!info] 语法点 6：字面量后缀 `U`
> `100U` 的 `U` 表示这是个**无符号整数常量**。10Hz 的 tick 周期是 100ms，用无符号表示"不可能是负数"，也让比较运算的类型一致，少些警告。

> [!info] 语法点 7：extern 变量声明
> `extern` 的意思是"**声明**：这个变量确实存在，但它定义在别的 .c 文件里（这里是 `stm32f1xx_hal.c`）"。
> 头文件里写 `extern` 声明、源文件里写真正的定义（`__IO uint32_t uwTick = 0;`）——这是 C 工程的铁律：**定义只能有一份，声明可以有很多份**。如果头文件里直接写定义，每个包含它的 .c 都会带一份，链接直接报重复定义。

> [!info] 语法点 8：volatile 与 `__IO`
> `__IO` 是 CMSIS（ARM 官方内核库）定义的宏，展开就是 `volatile`。
> `volatile` 告诉编译器："**这个变量的值可能被编译器看不见的东西修改**"——对嵌入式来说，就是中断服务函数（`HAL_IncTick()` 在 SysTick 中断里改 `uwTick`）。没有 `volatile` 时，编译器可能觉得"没人改它"而把 `uwTick` 缓存到寄存器里，结果你的 `while(uwTick < 1000);` 永远死循环。
> `uint32_t` 是 `<stdint.h>` 提供的定宽整数类型：32 位无符号。写嵌入式优先用它而不是 `int`，因为位数明确、跨平台不猜。

### §5 紧急开关柜：DBGMCU 冻结/解冻宏（L66-262）

这一大段是**调试模式开关**，本质是同一套模式的重复（TIM2~TIM17、WWDG、IWDG、I2C、CAN）。精讲第一个，其余看表格。

```c
/* 导出的宏 --------------------------------------------------------------*/
/** @defgroup DBGMCU_Freeze_Unfreeze 调试模式下冻结/解冻外设
  * @brief   调试模式下冻结/解冻外设
  * 注意：在 STM32F10xx8/B、F101/103 的 C/D/E/F/G、F10xx4/6 等型号上，
  *       DBGMCU_IDCODE 和 DBGMCU_CR 寄存器只能在调试模式下访问
  *       （正常运行的用户程序访问不到），详见对应型号的 errata 勘误手册。
  * @{
  */

/* APB1 总线上的外设 */
/**
  * @brief  TIM2 外设调试模式
  */
#define __HAL_DBGMCU_FREEZE_TIM2()            SET_BIT(DBGMCU->CR, DBGMCU_CR_DBG_TIM2_STOP)
#define __HAL_DBGMCU_UNFREEZE_TIM2()          CLEAR_BIT(DBGMCU->CR, DBGMCU_CR_DBG_TIM2_STOP)
```

> [!info] 语法点 9：宏函数
> `#define 名字(参数) 替换体` —— 预处理器在编译前做**纯文本替换**：代码里出现 `__HAL_DBGMCU_FREEZE_TIM2()` 的地方，直接被替换成 `SET_BIT(DBGMCU->CR, DBGMCU_CR_DBG_TIM2_STOP)`。
> 它**不是函数**：没有类型检查、没有调用栈、没有任何开销（不压栈传参），所以 HAL 里大量用它做寄存器操作。
> 名字以 `__HAL_` 开头——双下划线是"内部/低级"的惯例，表示它不是给你在业务代码里用的 API。

> [!info] 语法点 12：结构体指针 `->` 与寄存器
> `DBGMCU` 是一个指向"调试模块寄存器结构体"的指针（定义在 `stm32f1xx.h`），`->` 访问它的成员 `CR`（Control Register 控制寄存器）。
> **整个 HAL 的本质就是：宏/函数 → 操作这些结构体成员（寄存器）→ 寄存器再控制硬件。**

> [!info] 语法点 13：位掩码 SET_BIT / CLEAR_BIT
> `SET_BIT(REG, BIT)` 展开为 `((REG) |= (BIT))`：把 `BIT` 指定的那一位**置 1**。
> `CLEAR_BIT(REG, BIT)` 展开为 `((REG) &= ~(BIT))`：把那一位**清 0**。
> `DBGMCU_CR_DBG_TIM2_STOP` 是预定义的**位掩码**（如 `0x00000004`，即二进制的第 2 位）。
> 用途：调试器暂停（halt）时，让 TIM2 也暂停（冻结），否则定时器在调试时偷偷走，时间对不上。

> [!info] 语法点 11：条件编译 `#if defined`
> 一堆宏外面裹着 `#if defined (DBGMCU_CR_DBG_TIM4_STOP)` —— 如果芯片的头文件里没定义这个位（芯片没有 TIM4 的这个功能），**这一段代码直接不存在**。
> 这就是 HAL 一个库能通吃 F103 全系列（C8/CB/RC/RD/RF/RG…）的秘密：按芯片裁剪。条件编译的代码在最终编译前就被预处理器删掉了。

**其余宏全是同一模式**（冻结=置位 `DBGMCU_CR_DBG_xxx_STOP`，解冻=清位）：

| 外设 | 总线 | 对应的控制位 |
|---|---|---|
| TIM2 / TIM3 | APB1 | `DBG_TIM2_STOP` / `DBG_TIM3_STOP` |
| TIM4 / TIM5 / TIM6 / TIM7 | APB1 | `DBG_TIM4_STOP` … `DBG_TIM7_STOP`（带 `#if defined` 裁剪） |
| TIM12~TIM14 | APB1 | `DBG_TIM12_STOP` … `DBG_TIM14_STOP` |
| WWDG / IWDG | APB1 | `DBG_WWDG_STOP` / `DBG_IWDG_STOP`（看门狗调试时停走，方便单步调试） |
| I2C1 / I2C2 | APB1 | `DBG_I2C1_SMBUS_TIMEOUT` / `DBG_I2C2_SMBUS_TIMEOUT` |
| CAN1 / CAN2 | APB1 | `DBG_CAN1_STOP` / `DBG_CAN2_STOP` |
| TIM1 / TIM8 | APB2 | `DBG_TIM1_STOP` / `DBG_TIM8_STOP` |
| TIM9~TIM11 | APB2 | `DBG_TIM9_STOP` … `DBG_TIM11_STOP` |
| TIM15~TIM17 | APB2 | `DBG_TIM15_STOP` … `DBG_TIM17_STOP` |

> [!warning] 初学者怎么处理这段
> **跳过**。这段 200 行对一个点灯项目毫无用处，你要做的是"知道它存在"：*调试时能冻结外设*。等以后单步调试 PWM 舵机遇到"调完代码定时器已经跑飞了"的问题，再回来看。

### §6 私人物品架：IS_TICKFREQ 校验宏（L264-272）

```c
/** @defgroup HAL_Private_Macros HAL 私有宏
  * @{
  */
#define IS_TICKFREQ(FREQ) (((FREQ) == HAL_TICK_FREQ_10HZ)  || \   // 参数必须是三种合法频率之一
                           ((FREQ) == HAL_TICK_FREQ_100HZ) || \
                           ((FREQ) == HAL_TICK_FREQ_1KHZ))
```

> [!info] 语法点 10：宏续行符 `\`
> 宏只能写在一行，但太长时可以在行尾加反斜杠 `\` 继续下一行——预处理器处理时把 `\换行` 拼成一行。注意 `\` 后面**不能有空格**，否则续行失效，这是常见低级错误。
> `IS_xxx(FREQ)` 是 ST 库的**参数校验宏**惯例：返回"参数是否合法"。库内部调 `HAL_SetTickFreq()` 前先 `assert_param(IS_TICKFREQ(Freq))` 检查，非法就在 `assert_failed` 处卡死——裸机上的"调试断言"。
> **宏参数为什么都加括号** `(FREQ)`？宏是文本替换：如果传 `1+2`，`FREQ == 1` 会变成 `1+2 == 1`（先算加法），括号保证语义正确。这是 C 面试题经典考点。

### §7 服务窗口：函数声明（L274-325）

```c
/* 导出的函数 ------------------------------------------------------------*/
/** @addtogroup HAL_Exported_Functions HAL 导出的函数
  * @{
  */

/** @addtogroup HAL_Exported_Functions_Group1 初始化与反初始化函数
  * @{
  */
HAL_StatusTypeDef HAL_Init(void);           // 初始化整个 HAL：配置 Flash 预取、时基等（main 第一句）
HAL_StatusTypeDef HAL_DeInit(void);         // 反初始化（复位 HAL 状态，正常业务几乎不用）
void HAL_MspInit(void);                     // 弱函数：由你在 stm32f1xx_hal_msp.c 里实现（配置时钟/引脚）
void HAL_MspDeInit(void);                   // 弱函数：配套反初始化
HAL_StatusTypeDef HAL_InitTick(uint32_t TickPriority); // 初始化时基（SysTick 定时器）
/** @}
  */

/** @addtogroup HAL_Exported_Functions_Group2 外设控制函数
  * @{
  */
void HAL_IncTick(void);                     // 时基中断里执行：uwTick++（你永远不直接调用）
void HAL_Delay(uint32_t Delay);             // 忙等 Delay 毫秒（点灯课的闪烁就靠它）
uint32_t HAL_GetTick(void);                 // 读当前 uwTick（"现在是第几毫秒"）
uint32_t HAL_GetTickPrio(void);             // 读时基中断优先级
HAL_StatusTypeDef HAL_SetTickFreq(HAL_TickFreqTypeDef Freq); // 改时基频率
HAL_TickFreqTypeDef HAL_GetTickFreq(void);  // 读当前时基频率
void HAL_SuspendTick(void);                 // 暂停时基（进低功耗前用）
void HAL_ResumeTick(void);                  // 恢复时基
uint32_t HAL_GetHalVersion(void);           // 查 HAL 库版本号
uint32_t HAL_GetREVID(void);                // 芯片修订版本号（revision）
uint32_t HAL_GetDEVID(void);                // 芯片型号 ID（device ID）
uint32_t HAL_GetUIDw0(void);                // 芯片唯一 ID 第 1 个字（96 位 UID 拆成 3 个字）
uint32_t HAL_GetUIDw1(void);                // 芯片唯一 ID 第 2 个字
uint32_t HAL_GetUIDw2(void);                // 芯片唯一 ID 第 3 个字
void HAL_DBGMCU_EnableDBGSleepMode(void);   // 调试：睡眠模式下保持调试连接
void HAL_DBGMCU_DisableDBGSleepMode(void);
void HAL_DBGMCU_EnableDBGStopMode(void);    // 调试：停止模式下保持调试连接
void HAL_DBGMCU_DisableDBGStopMode(void);
void HAL_DBGMCU_EnableDBGStandbyMode(void); // 调试：待机模式下保持调试连接
void HAL_DBGMCU_DisableDBGStandbyMode(void);
/** @}
  */
```

> [!info] 语法点 14：函数声明 vs 定义
> - **声明（原型）**：`HAL_StatusTypeDef HAL_Init(void);` —— 只有签名、以 `;` 结尾。告诉编译器"存在这么个函数，参数返回长这样"，**具体实现别处找**。
> - **定义**：`HAL_StatusTypeDef HAL_Init(void) { ... }` —— 有函数体 `{}`，在 `stm32f1xx_hal.c` 里。
> 头文件放声明、源文件放定义，是 C 工程的铁律：声明可以无数份（每个想用的人各拿一份），定义只能有一份。所以你在 main.c 里调用 `HAL_Delay(500)` 时，编译器靠这个声明知道"该传 int、返回 void"，链接器再去 `stm32f1xx_hal.c` 找真正的代码。
> `HAL_StatusTypeDef` 是 HAL 的**通用返回类型**：`HAL_OK`/`HAL_ERROR`/`HAL_BUSY`/`HAL_TIMEOUT`——就像函数的"三色指示灯"，用它判断调用是否成功。

> [!info] 语法点 15：弱函数 HAL_MspInit
> `HAL_MspInit` 声明在这里，但**定义是"弱"的**（0002 学过 weak symbol）：库里给了一个空默认实现，`stm32f1xx_hal_msp.c` 里写了一个同名强定义把它覆盖掉。Msp = MCU Support Package，负责"外设的底层配置"：时钟、引脚。
> 通俗理解：HAL 库负责"公共设施"，Msp 负责"你家装修"——所以 CubeMX 生成一个空模板让你填。

> [!info] HAL_GetUIDw0~2
> 每颗 ST 芯片出厂烧录 96 位唯一 ID（3 个 32 位字）。用途：软件授权（一机一码）、设备身份识别。我们的火控云台用不到，但值得知道它的存在——以后做"绑定设备"功能就用它。

### §8 空房间与收尾（L326-355）

```c
/* 私有类型 -------------------------------------------------------------*/
/* 私有变量 -------------------------------------------------------------*/
/** @defgroup HAL_Private_Variables HAL 私有变量
  * @{
  */
/** @}
  */
/* 私有常量 -------------------------------------------------------------*/
/** @defgroup HAL_Private_Constants HAL 私有常量
  * @{
  */
/** @}
  */
/* 私有宏 ----------------------------------------------------------------*/
/* 私有函数 -------------------------------------------------------------*/
/** @}
  */

#ifdef __cplusplus   // 收尾：如果上面开了 extern "C"，在这里关掉
}
#endif

#endif /* __STM32F1xx_HAL_H */  // 收尾：include guard 的最后一个 #endif（对应 L21）
```

> [!info] 为什么全是空组？
> 这是 ST 的**模板强迫症**：所有头文件都预留统一的段落结构（类型/变量/常量/宏/函数），本文件恰好全空——说明本文件的"私有内容"为零：它只是门面，真正的私有实现（`static` 变量、内部函数）都藏在 `stm32f1xx_hal.c` 里。C 的 `static` 是"文件内私有"的关键字。
> 收尾两行与开头一一对应：`extern "C"` 开关配对、include guard 配对。**头文件的结构就是括号配对**——看到 `#ifndef` 就一定在文件末尾有个配对的 `#endif`。

---

## 四、C 语法点汇总表（复习用）

| 语法点 | 一句话 | 关键特征 |
|---|---|---|
| include guard | 防止头文件被读两次 | `#ifndef` + `#define` + `#endif` 三件套 |
| 预处理指令 | 编译前执行的文本操作 | 以 `#` 开头，无分号 |
| extern "C" | C++ 调用 C 代码的接头暗号 | 只对 C++ 编译生效 |
| Doxygen 注释 | 带 `@` 标签的文档注释 | `/** */`，不参与编译 |
| typedef enum | 给一组命名整数定义类型 | 以 `;` 结尾 |
| `U` 后缀 | 无符号整数字面量 | `100U` |
| extern 变量 | "定义在别的 .c 里"的声明 | 头文件里只能声明不能定义 |
| volatile | "可能被硬件/中断改，别缓存" | 嵌入式必备 |
| 宏函数 | 预处理期纯文本替换 | 无类型检查、无开销 |
| 宏续行 `\` | 宏跨行 | `\` 后不能有空格 |
| `#if defined` | 按条件裁剪代码 | 一套库通吃全系列芯片 |
| `->` 与位掩码 | 通过指针改寄存器某一位 | `SET_BIT`/`CLEAR_BIT` |
| 函数声明 vs 定义 | 声明只签名、定义有函数体 | 声明在 .h，定义在 .c |
| 弱函数 | 有默认实现、可被覆盖 | 库给模板，用户填装修 |

**本文件里 C 语言的全部家当，就是这两页纸。** 学完这一篇，你在 STM32 里看到 90% 的头文件都不会再慌——因为所有 ST 头文件都是同一套骨架。

---

## 五、怎么用好这个头文件（初学者指南）

1. **不用背，更不用翻**：它只是"大厅"。你平时写代码用的是各外设头文件（`HAL_GPIO_`、`HAL_UART_`…），它们内部都 `#include` 了这个大厅，所以你在 main.c 里只要 `#include "main.h"`，全库都通了。
2. **务必认识的 3 个函数**：
   - `HAL_Init()` —— main() 第一句，开馆仪式
   - `HAL_Delay(ms)` —— 点灯练手天天用，**忙等**（CPU 空转）
   - `HAL_GetTick()` —— 看"当前时刻"，以后做非阻塞延时、按键消抖都靠它
3. **真正值得研究的是它门口的 conf 纸条**：同目录的 `stm32f1xx_hal_conf.h`。想加串口/定时器外设时去那里打开对应开关（如 `HAL_UART_MODULE_ENABLED`）——新手编译报 `undefined reference` 或找不到函数声明，一半是忘了开这个开关。
4. **看见 DBGMCU 那段直接跳过**：200 行的调试开关，点灯项目用不到，知道"存在"即可。
5. **学会用悬停**：VS Code 里把鼠标放在 `HAL_GetTick` 上，弹出的说明就来自这篇 Doxygen 注释——这是官方给的最好的文档入口。
6. **顺着宏往深处追**：在 `HAL_Delay(500)` 上 F12 跳转，一路往下会看到它最终调 `HAL_GetTick()`、读写 `uwTick`——把"宏函数 → 函数 → 寄存器"这条链走通一遍，嵌入式的地基就打下了。

---

## 六、练习（动手才能记住）

> [!example] 练习 1（10 分钟）：语法点归位
> 不看上文，说出下面每段代码用到的**语法点名称**（提示：共 5 个）：
> ```c
> #ifndef __STM32F1xx_HAL_H
> #define __STM32F1xx_HAL_H
> ```
> ```c
> typedef enum { A = 1U, B = 2U } MyEnum;
> ```
> ```c
> #define FOO(x) ((x) + 1)
> ```
> ```c
> extern __IO uint32_t uwTick;
> ```

> [!example] 练习 2（10 分钟）：概念复述
> 不看笔记，用你自己的话回答：
> ① 为什么头文件要有 include guard？没有会怎样？
> ② `extern` 变量声明和 `volatile` 分别是防什么？
> ③ 宏函数和普通函数的最大区别是什么？（提示：想"什么时候执行"）
> ④ `HAL_StatusTypeDef` 是什么？为什么函数要返回它？

> [!example] 练习 3（15 分钟）：追根溯源（VS Code）
> 1. 打开 `DDM_test/Core/Src/main.c`，找到 `HAL_Init()`，F12 跳转
> 2. 再 F12 进入 `stm32f1xx_hal.c` 的实现，找到它对 `uwTick` 的赋值（搜 `uwTick =`）
> 3. 再搜 `HAL_IncTick` 的实现，看它做了什么
> 4. 最后回答：`uwTick` 是**谁**在哪个**中断**里被加 1 的？（提示：找 `SysTick_Handler`）
> 5. 写一句话：从 `HAL_Delay(500)` 到你 CPU 的时钟，中间隔着几层？

> [!example] 练习 4（进阶挑战，20 分钟）：把大厅的钟改快
> 1. 查 `stm32f1xx_hal_conf.c` 或 `stm32f1xx_hal.c` 里 `HAL_InitTick` 的调用，找到时基初始化的地方
> 2. 试试在 main 里调用 `HAL_SetTickFreq(HAL_TICK_FREQ_100HZ)`，再烧录，观察 `HAL_Delay(1000)` 的实际表现
> 3. **先写预测再烧录**：`HAL_Delay(1000)` 在 100Hz 时域上真的等了 1 秒吗？为什么？（提示：tick 频率变了，HAL_Delay 内部还是按"1ms 一格"算吗？）

> [!example] 练习 5（5 分钟）：术语自检
> 从「二、语法点清单」的 15 个术语里随机挑 5 个，不看笔记，给每个写一句话定义。写不出来的就是没吃透的，回去再看对应 §。

---

## 关联

- 上一课：[[教学-STM32/lessons/0002-CubeMX工程结构解剖-DianDengMaster逐文件精读|0002 工程结构解剖]]
- 下一篇精读建议：`stm32f1xx_hal_conf.h`（门口的 conf 纸条，加外设的钥匙）
- 术语表：[[教学-STM32/reference/术语表|STM32 课程术语表]]
- 任务书：[[教学-STM32/MISSION.md|Mission]]
- 今日进度：[[每日日志/每日日志|每日日志索引]]
- 索引：[[30天学习 Index|30天学习 Index]]
