import argparse

import cv2
import numpy as np
import serial

from pid import PID

# ================= 用户配置区域 (实机调参重点) =================
# HSV 阈值 (2026-08-22 桌面背景实测; 换光照/背景需用 color_picker.py 重调)
HSV_LOWER = np.array([0, 105, 193])
HSV_UPPER = np.array([179, 255, 255])

MIN_AREA = 500  # 面积门槛: 比这小的轮廓当作噪点
DEAD_ZONE = 40  # 软件死区: 误差小于此值不调整 (SG90 虚位大, 防止来回抖)

# PID 参数 (调参重点!)
# Kp: 反应速度。太小追不上, 太大疯狂抖。建议 0.1 - 0.2
# Kd: 刹车力度。消除抖动。建议 0.002 - 0.01
PID_KP = 0.12
PID_KD = 0.005

# 串口增量限幅: 单帧最大发送增量, 防止舵机抽风
MOVE_LIMIT = 60

# 方向翻转 (与 servo_test.py 同款): 实机发现方向反了就改这两个
FLIP_X = False
FLIP_Y = True
# ============================================================


def main():
    parser = argparse.ArgumentParser(description="ball tracking closed loop")
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--no-serial", action="store_true",
                        help="只跑视觉+PID 不连串口 (纯看输出)")
    args = parser.parse_args()

    ser = None
    if not args.no_serial:
        try:
            ser = serial.Serial(args.port, 115200, timeout=0.1)
            print(f"connected: {args.port} @115200")
        except Exception as e:
            print(f"cannot open serial {args.port}: {e}")
            print("fallback to --no-serial mode")
            ser = None

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("cannot open camera 0")
        return
    # 本机摄像头 YUYV 输出偏色, 必须用 MJPG
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(3, 640)
    cap.set(4, 480)

    flip_x = -1 if FLIP_X else 1
    flip_y = -1 if FLIP_Y else 1

    pid_x = PID(kp=PID_KP, ki=0, kd=PID_KD)
    pid_y = PID(kp=PID_KP, ki=0, kd=PID_KD)

    FRAME_CX, FRAME_CY = 320, 240
    print("tracking... 'q' to quit")

    while True:
        ok, img = cap.read()
        if not ok:
            break

        # 1. 镜像翻转
        img = cv2.flip(img, 1)

        # 2. 图像处理: 模糊 -> HSV -> 掩膜 -> 形态学去噪
        imgBlur = cv2.GaussianBlur(img, (7, 7), 1)
        imgHsv = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHsv, HSV_LOWER, HSV_UPPER)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # 3. 十字准星
        cv2.line(img, (FRAME_CX - 30, FRAME_CY), (FRAME_CX + 30, FRAME_CY), (0, 255, 255), 1)
        cv2.line(img, (FRAME_CX, FRAME_CY - 30), (FRAME_CX, FRAME_CY + 30), (0, 255, 255), 1)

        found = False
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)
            if area > MIN_AREA:
                found = True
                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w // 2
                cy = y + h // 2
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)

                # 4. 计算误差 (球心 - 画面中心), 图像坐标: y 向下为正
                error_x = cx - FRAME_CX
                error_y = cy - FRAME_CY
                cv2.line(img, (FRAME_CX, FRAME_CY), (cx, cy), (255, 0, 255), 2)

                # 5. PID 计算, 乘方向翻转
                move_x = int(pid_x.compute(error_x) * flip_x)
                move_y = int(pid_y.compute(error_y) * flip_y)

                # 6. 软件死区: 误差小到一定范围就停手 (防 SG90 虚位抖动)
                if abs(error_x) < DEAD_ZONE:
                    move_x = 0
                if abs(error_y) < DEAD_ZONE:
                    move_y = 0

                # 7. 限幅
                move_x = max(-MOVE_LIMIT, min(MOVE_LIMIT, move_x))
                move_y = max(-MOVE_LIMIT, min(MOVE_LIMIT, move_y))

                # 8. 发送给 STM32: "X增量,Y增量\n"
                if ser:
                    ser.write(f"{move_x},{move_y}\n".encode())

                cv2.putText(img, f"Err: {error_x},{error_y}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                cv2.putText(img, f"PID: {move_x},{move_y}", (20, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            else:
                cv2.putText(img, "no target", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("tracking", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    if ser:
        ser.close()
    cap.release()
    cv2.destroyAllWindows()
    print("bye")


if __name__ == "__main__":
    main()
