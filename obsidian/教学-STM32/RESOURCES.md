# STM32 火控云台 Resources

## Knowledge

- [复刻对象仓库：S90_aim_ball（GitHub）](https://github.com/edythieajahgsgshwtvwyvwfd-sketch/S90_aim_ball)
  本项目唯一主参考：可直接阅读的完整可运行代码（main.c + ball_track.py + pid.py + .ioc）。Use for: 每课对照实现、抄结构、排查预期行为。
- [知乎原文：STM32+OpenCV+PID 打造"视觉追踪火控云台"](https://zhuanlan.zhihu.com/p/1992580909858305860)
  硬件清单、架构图、踩坑点（视差补偿、死区、供电）。Use for: 全项目设计动机与硬件接线依据。
- [ST 官方：STM32F103 参考手册 RM0008](https://www.st.com/resource/en/reference_manual/rm0008-stm32f101xx-stm32f102xx-stm32f103xx-stm32f105xx-and-stm32f107xx-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)
  primary source，GPIO/PWM(定时器)/UART 章节的权威定义。Use for: 术语澄清、寄存器说明（HAL 之上按需查阅）。
- [ST 官方：STM32F103x8/xB datasheet](https://www.st.com/resource/en/datasheet/stm32f103c8.pdf)
  引脚图、电气参数、封装。Use for: 接线课时对照引脚编号。
- [ST 官方：STM32CubeMX 用户手册 UM1718](https://www.st.com/resource/en/user_manual/um1718-stm32cubemx-for-stm32-configuration-and-initialization-c-code-generation-stmicroelectronics.pdf)
  CubeMX 操作与代码生成机制。Use for: 工具链课时。
- [B 站 keysking：CLion+CubeMX 开发 STM32 配置教程](https://www.bilibili.com)
  参考仓库 README 推荐的入门视频（CLion 版）；我们改 vscode，但 CubeMX 操作与工程理解通用。Use for: 环境搭建的流程对照。
- [OpenCV 官方教程：HSV 颜色空间](https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html)
  `cvtColor`/`inRange` 权威说明。Use for: 视觉课时。
- [Brett Beauregard：Improving the Beginner's PID（系列 4 篇）](http://brettbeauregard.com/blog/2011/04/improving-the-beginner%e2%80%99s-pid-introduction/)
  PID 调参的经典权威系列，直接解释参考仓库 pid.py 的写法（死区、饱和、增量式）。Use for: PID 课时。
- [ST 官方：STM32CubeProgrammer 文档](https://www.st.com/en/development-tools/stm32cubeprog.html)
  SWD 烧录工具（CLI 版 STM32_Programmer_CLI）。Use for: 烧录课时。

## Wisdom (Communities)

- 学校机器人队（用户计划加入）：真实嵌入式实践与 mentor 反馈。Use for: 项目完成后展示、进阶指导。
- [r/STM32 (Reddit)](https://www.reddit.com/r/STM32/)：活跃的 STM32 提问与经验区，moderation 尚可。Use for: 卡壳超过 1 天时求助。
- [ST 社区论坛](https://community.st.com/)：官方员工偶尔回复，HAL 行为疑问的最佳去处。Use for: 官方 API 行为不符合预期时。

## Gaps

- vscode + CubeMX + CMake 的完整中文教程（参考仓库用 CLion；vscode 路线需自己拼装，工具链课时产出速查表补上）。
- WSL2 下 ST-Link 烧录通路的中文资料（usbipd-win 直通 vs Windows 侧 CLI 烧录，验证后写入 TIL）。
