import argparse
import sys
import termios
import tty

import serial

# 固件限位 (DDM_test: sscanf 解析后钳制 500-2500)
SERVO_MIN = 500
SERVO_MAX = 2500
CENTER_INIT = 1500  # 理论中点, 标定后会得到实际值

HELP = """
舵机标定工具: 单轴步进扫描, 找到 中立位 / 机械限位
  键位 (X轴: a/d 减小/增大;  Y轴: w/s 减小/增大)
  步长切换: 1=细(5us) 2=中(20us) 3=粗(100us)
  标记: z=中立位  l=最小安全位  r=最大安全位  (可反复覆盖)
  q=退出并打印标定结果
操作流程: 先切粗步长扫到机械极限前停下 → 标记 l/r →
          再扫回中心找到水平/竖直位 → 标记 z → q
警告: 接近机械极限时用细步长, 听到堵转声立即反向步进!
"""


def main():
    parser = argparse.ArgumentParser(description="servo calibration")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    args = parser.parse_args()

    ser = serial.Serial(args.port, 115200, timeout=0.1)
    print(f"connected: {args.port} @115200")
    print(HELP)

    pos_x = CENTER_INIT
    pos_y = CENTER_INIT
    step = 100
    cal = {"x": {"min": None, "center": None, "max": None},
           "y": {"min": None, "center": None, "max": None}}

    def clamp(v):
        return max(SERVO_MIN, min(SERVO_MAX, v))

    # 双轴同时标定: 标 X 时 Y 停在中心, 标 Y 时 X 停在中心
    last_x = CENTER_INIT
    last_y = CENTER_INIT

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        while True:
            print(f"\rX={pos_x:>4}  Y={pos_y:>4}  step={step:>3} | "
                  f"x:[{cal['x']['min']},{cal['x']['center']},{cal['x']['max']}] "
                  f"y:[{cal['y']['min']},{cal['y']['center']},{cal['y']['max']}]", end="")
            ch = sys.stdin.read(1).lower()
            print()

            if ch == "q":
                break
            elif ch == "a":
                pos_x = clamp(pos_x - step)
                ser.write(f"{pos_x - last_x},0\n".encode())
                last_x = pos_x
            elif ch == "d":
                pos_x = clamp(pos_x + step)
                ser.write(f"{pos_x - last_x},0\n".encode())
                last_x = pos_x
            elif ch == "w":
                pos_y = clamp(pos_y - step)
                ser.write(f"0,{pos_y - last_y}\n".encode())
                last_y = pos_y
            elif ch == "s":
                pos_y = clamp(pos_y + step)
                ser.write(f"0,{pos_y - last_y}\n".encode())
                last_y = pos_y
            elif ch == "1":
                step = 5
            elif ch == "2":
                step = 20
            elif ch == "3":
                step = 100
            elif ch == "z":
                cal["x"]["center"] = pos_x
                cal["y"]["center"] = pos_y
                print(f"  标记中立位: X={pos_x} Y={pos_y}")
            elif ch == "l":
                cal["x"]["min"] = pos_x
                cal["y"]["min"] = pos_y
                print(f"  标记最小限位: X={pos_x} Y={pos_y}")
            elif ch == "r":
                cal["x"]["max"] = pos_x
                cal["y"]["max"] = pos_y
                print(f"  标记最大限位: X={pos_x} Y={pos_y}")
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        ser.close()

    print("\n标定结果:")
    print(f"  X轴: min={cal['x']['min']} center={cal['x']['center']} max={cal['x']['max']}")
    print(f"  Y轴: min={cal['y']['min']} center={cal['y']['center']} max={cal['y']['max']}")
    print("把数值填入 ball_track.py 的 SERVO_* 配置")


if __name__ == "__main__":
    main()
