"""气象站核心逻辑：传感器、观测窗口、数据和校准。"""

import json
import random

FIXED_SEED = 48


def new_game():
    return {
        "sensors": {},
        "data": {},
        "windows": {},
        "storage_capacity": 100,
        "calibrated": {},
        "fault": False,
        "storm": False,
        "day": 1,
        "weather_seq": ["clear", "cloudy", "storm"],
        "weather_idx": 0,
        "rng_state": random.Random(FIXED_SEED).getstate(),
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    return json.loads(text)


def calibrate(state, sensor_id):
    """校准传感器；重复校准返回 False（幂等，不重复生效）。"""
    if state["calibrated"].get(sensor_id):
        return False
    state["sensors"][sensor_id] = True
    state["calibrated"][sensor_id] = True
    return True


def _used_storage(state):
    """数据占用按字节累计，空数据为 0。"""
    return sum(state["data"].values())


def data_capacity(state):
    return _used_storage(state)


def _fits(state, sensor_id, size):
    if size < 0:
        return False
    projected = _used_storage(state) - state["data"].get(sensor_id, 0) + size
    return projected <= state["storage_capacity"]


def observe(state, sensor_id, size):
    """外场观测：暴雨拒绝；容量按字节校验；同传感器重复观测幂等覆盖。"""
    if state.get("storm"):
        return False
    if not _fits(state, sensor_id, size):
        return False
    state["data"][sensor_id] = size
    state["windows"][sensor_id] = "booked"
    return True


def cancel_observe(state, sensor_id):
    """取消观测并释放窗口；重复取消幂等。"""
    state["data"].pop(sensor_id, None)
    state["windows"][sensor_id] = "open"
    return True


def record(state, sensor_id, size):
    """结算记录：设备故障拒绝；容量按字节校验；重复记录幂等覆盖。"""
    if state.get("fault"):
        return False
    if not _fits(state, sensor_id, size):
        return False
    state["data"][sensor_id] = size
    return True


def next_weather(state):
    """按固定顺序推进天气：clear -> cloudy -> storm 循环。"""
    seq = state["weather_seq"]
    weather = seq[state["weather_idx"] % len(seq)]
    state["weather_idx"] = (state["weather_idx"] + 1) % len(seq)
    state["storm"] = weather == "storm"
    return weather


def _cmd_calibrate(state, args):
    if len(args) != 1:
        return "用法: calibrate <sensor>"
    return "ok" if calibrate(state, args[0]) else "已校准，忽略重复校准"


def _cmd_observe(state, args):
    if len(args) != 2:
        return "用法: observe <sensor> <size>"
    try:
        size = int(args[1])
    except ValueError:
        return "size 必须是整数"
    return "ok" if observe(state, args[0], size) else "观测被拒绝（暴雨或容量不足）"


def _cmd_capacity(state, args):
    if args:
        return "用法: capacity"
    return "已用 %d/%d 字节" % (data_capacity(state), state["storage_capacity"])


def _cmd_cancel(state, args):
    if len(args) != 1:
        return "用法: cancel <sensor>"
    cancel_observe(state, args[0])
    return "ok"


def _cmd_record(state, args):
    if len(args) != 2:
        return "用法: record <sensor> <size>"
    try:
        size = int(args[1])
    except ValueError:
        return "size 必须是整数"
    return "ok" if record(state, args[0], size) else "记录被拒绝（设备故障或容量不足）"


def _cmd_weather(state, args):
    if args:
        return "用法: weather"
    return next_weather(state)


COMMANDS = {
    "calibrate": _cmd_calibrate,
    "observe": _cmd_observe,
    "capacity": _cmd_capacity,
    "cancel": _cmd_cancel,
    "record": _cmd_record,
    "weather": _cmd_weather,
}


def dispatch(state, raw):
    parts = raw.split()
    if not parts:
        return "空命令"
    name, args = parts[0], parts[1:]
    handler = COMMANDS.get(name)
    if handler is None:
        return "非法命令: %s" % name
    return handler(state, args)


def main():
    state = new_game()
    print("气象站 - 命令: calibrate/observe/capacity/cancel/record/weather/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        print(dispatch(state, raw))


if __name__ == "__main__":
    main()
