import cv2
import numpy as np


def empty(a):
    pass


# 1. 创建一个窗口，放 6 个滑动条
cv2.namedWindow("HSV Setting")
cv2.resizeWindow("HSV Setting", 640, 240)

# 橙色的经验初值 (你可以基于这个微调)
cv2.createTrackbar("H Min", "HSV Setting", 0, 179, empty)  # 色调最小值
cv2.createTrackbar("H Max", "HSV Setting", 25, 179, empty)  # 色调最大值
cv2.createTrackbar("S Min", "HSV Setting", 120, 255, empty)  # 饱和度最小值 (要高点，滤掉白墙)
cv2.createTrackbar("S Max", "HSV Setting", 255, 255, empty)
cv2.createTrackbar("V Min", "HSV Setting", 100, 255, empty)  # 亮度最小值
cv2.createTrackbar("V Max", "HSV Setting", 255, 255, empty)

# 打开摄像头
cap = cv2.VideoCapture(0)
# 本机摄像头 YUYV 输出偏色，必须用 MJPG
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(3, 640)  # 宽
cap.set(4, 480)  # 高

print("正在启动摄像头... 请拿出你的橙色小球！")
print("任务目标：拖动滑块，让'Mask'窗口里，只有球是【白色】，其他全是【黑色】。")

while True:
    success, img = cap.read()
    if not success:
        break

    # 镜像翻转 (让画面操作符合直觉)
    img = cv2.flip(img, 1)

    # 转换颜色空间 BGR -> HSV
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 获取滑动条当前的值
    h_min = cv2.getTrackbarPos("H Min", "HSV Setting")
    h_max = cv2.getTrackbarPos("H Max", "HSV Setting")
    s_min = cv2.getTrackbarPos("S Min", "HSV Setting")
    s_max = cv2.getTrackbarPos("S Max", "HSV Setting")
    v_min = cv2.getTrackbarPos("V Min", "HSV Setting")
    v_max = cv2.getTrackbarPos("V Max", "HSV Setting")

    # 创建掩膜 (Mask): 在范围内的变白，不在范围内的变黑
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHsv, lower, upper)

    # 显示结果
    cv2.imshow("Original", img)  # 原图
    cv2.imshow("Mask", mask)  # 黑白图 (调试看这个！)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print(f"\n✅ 记录下这一组完美的数值 (Lower ~ Upper):")
        print(f"Lower = [{h_min}, {s_min}, {v_min}]")
        print(f"Upper = [{h_max}, {s_max}, {v_max}]")
        break

cap.release()
cv2.destroyAllWindows()
