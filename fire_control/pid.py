import time


class PID:
    """PID 控制器。参考仓库 pid.py 的复刻版。

    参考仓库的隐藏 bug：`ki` 定义了但从未使用，积分项根本没实现。
    本版实现完整积分累积（默认 ki=0，视觉追踪通常用 PD 即可）。
    """

    def __init__(self, kp, ki, kd):
        self.kp = kp  # 比例（动力）：误差越大输出越大
        self.ki = ki  # 积分（纠偏）：累积历史误差，消除稳态误差
        self.kd = kd  # 微分（阻尼/防抖）：误差变化率，抑制过冲

        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()
        self.first = True  # 首帧标志: 跳过 D 项 (没有"上次误差"可比)

    def compute(self, error):
        current_time = time.time()
        delta_time = current_time - self.last_time

        # 防止时间过短导致除以 0
        if delta_time <= 0:
            delta_time = 0.001

        # P: 比例项
        p_out = self.kp * error

        # I: 积分项 (累积误差 × 时间)
        self.integral += error * delta_time
        i_out = self.ki * self.integral

        # D: 微分项 (本次误差 - 上次误差) / 时间
        if self.first:
            # 首帧没有"上次误差"，D 强制为 0，否则刚创建的微小 Δt 会让 D 爆炸
            derivative = 0
            self.first = False
        else:
            derivative = (error - self.last_error) / delta_time
        d_out = self.kd * derivative

        # 总输出
        output = p_out + i_out + d_out

        # 更新状态
        self.last_error = error
        self.last_time = current_time

        return output


def _demo():
    """离线模拟：喂一组递减误差（模拟球从偏 100px 被追到中心），
    对比纯 P 和 PD 的输出，理解 D 项的刹车作用。"""
    print("=" * 60)
    print("离线模拟：误差序列 [100, 80, 60, 40, 20, 0, -10]（球逐渐回中心）")
    print("=" * 60)

    # 纯 P: 只有动力，没有刹车
    pid_p = PID(kp=0.12, ki=0, kd=0)
    # PD: 动力 + 刹车
    pid_pd = PID(kp=0.12, ki=0, kd=0.005)

    print(f"{'error':>6} | {'P_out':>8} | {'PD_out':>8} | D 项作用")
    print("-" * 60)

    errors = [100, 80, 60, 40, 20, 0, -10]
    prev_error = 100
    for e in errors:
        p_out = pid_p.compute(e)
        pd_out = pid_pd.compute(e)

        # 模拟真实摄像头帧率 (30fps → 每帧间隔约 33ms)
        # D 项 = kd * Δerror/Δt，Δt 越小 D 项越大；
        # 离线循环间隔微秒级会让 D 项爆炸 (几万)，真实环境 33ms 才正常
        time.sleep(0.033)

        # D 项作用解读: 误差在减小 (error 变小时) D 为负 = 刹车
        if prev_error - e > 0:
            note = "误差在减小 → D 刹车"
        elif prev_error - e < 0:
            note = "误差在增大 → D 加速"
        else:
            note = "误差不变 → D 归零"
        prev_error = e

        print(f"{e:>6} | {p_out:>8.2f} | {pd_out:>8.2f} | {note}")

    print("-" * 60)
    print("结论：PD_out 在误差递减时小于 P_out（被 D 拉住），"
          "所以 Kd 能抑制抖动；但太大也会拖慢响应。")
    print("参数直觉：Kp 大→追得快但抖；Kd 大→稳但肉。视觉追踪常用 PD(ki=0)。")


if __name__ == "__main__":
    _demo()
