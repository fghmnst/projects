import argparse

import cv2
import numpy as np

# 用 color_picker.py 调出来的数值 (2026-08-22 两次实调, 最终: Lower=[0,120,100] Upper=[25,255,255])
HSV_LOWER = np.array([0, 120, 100])
HSV_UPPER = np.array([25, 255, 255])
MIN_AREA = 500  # 面积门槛: 比这小的轮廓当作噪点


def main():
    parser = argparse.ArgumentParser(description="detect orange ball, draw box + center")
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.index)
    if not cap.isOpened():
        print(f"cannot open camera {args.index}")
        return
    # 本机摄像头 YUYV 输出偏色，必须用 MJPG
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(3, 640)
    cap.set(4, 480)

    print("detecting orange ball... 'q' to quit")

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

        # 3. 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # 4. 十字准星: 画面中心 (视场中心 = 云台瞄准目标)
        FRAME_CX, FRAME_CY = 320, 240
        cv2.line(img, (FRAME_CX - 30, FRAME_CY), (FRAME_CX + 30, FRAME_CY), (0, 255, 255), 1)
        cv2.line(img, (FRAME_CX, FRAME_CY - 30), (FRAME_CX, FRAME_CY + 30), (0, 255, 255), 1)

        # 5. 找面积最大的轮廓 (避免把背景噪点当球)
        found = False
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(cnt)
            if area > MIN_AREA:
                found = True
                # 6. 画框和中心点
                x, y, w, h = cv2.boundingRect(cnt)
                cx = x + w // 2
                cy = y + h // 2
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(img, f"area={int(area)}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 7. 核心: 计算误差 (球心 - 画面中心), 并画出误差向量
                error_x = cx - FRAME_CX
                error_y = cy - FRAME_CY
                cv2.line(img, (FRAME_CX, FRAME_CY), (cx, cy), (255, 0, 255), 2)
                cv2.putText(img, f"Err: {error_x},{error_y}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            else:
                cv2.putText(img, "no target", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(img, "no target", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.imshow("ball detect", img)
        cv2.imshow("mask", mask)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("bye")


if __name__ == "__main__":
    main()
