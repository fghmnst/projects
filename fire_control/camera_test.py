import argparse

import cv2


def main():
    parser = argparse.ArgumentParser(description="camera test: show live frame")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--flip", action="store_true", default=True,
                        help="mirror flip (default on, like a mirror)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.index)
    if not cap.isOpened():
        print(f"cannot open camera {args.index}")
        return

    # this camera outputs broken colors in YUYV, must use MJPG
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(3, 640)  # width
    cap.set(4, 480)  # height
    print(f"camera {args.index} opened, size 640x480, 'q' to quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("frame read failed")
            break

        if args.flip:
            frame = cv2.flip(frame, 1)

        cv2.imshow("camera test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("bye")


if __name__ == "__main__":
    main()
