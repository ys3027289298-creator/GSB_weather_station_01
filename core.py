"""气象站核心逻辑：传感器、观测窗口、数据和校准。"""

import json

COMMANDS = ("calibrate", "observe", "capacity", "cancel", "record", "weather", "quit")


def new_game():
    return {
        "sensors": {},
        "data": {},
        "windows": {},
        "storage_capacity": 100,
        "calibrated": {},
        "day": 1,
        "weather_seq": ["clear", "cloudy", "storm"],
        "weather_idx": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    return json.loads(text)


def calibrate(state, sensor_id):
    if state["calibrated"].get(sensor_id):
        return False
    state["sensors"][sensor_id] = True
    state["calibrated"][sensor_id] = True
    return True


def data_capacity(state):
    return sum(state["data"].values())


def can_store(state, size, sensor_id=None):
    used = data_capacity(state) - state["data"].get(sensor_id, 0)
    return used + size <= state["storage_capacity"]


def observe(state, sensor_id, size):
    if state.get("storm"):
        return False
    if size <= 0:
        return False
    if sensor_id in state["data"]:
        return state["data"][sensor_id] == size
    if not can_store(state, size):
        return False
    state["data"][sensor_id] = size
    return True


def cancel_observe(state, window_id):
    windows = state.setdefault("windows", {})
    if windows.get(window_id) == "booked":
        windows[window_id] = "open"
        return True
    return windows.get(window_id) == "open"


def record(state, sensor_id, size):
    if state.get("fault"):
        return False
    if size <= 0:
        return False
    if not can_store(state, size, sensor_id):
        return False
    state["data"][sensor_id] = size
    return True


def next_weather(state):
    seq = state["weather_seq"]
    weather = seq[state["weather_idx"] % len(seq)]
    state["weather_idx"] += 1
    state["storm"] = weather == "storm"
    return weather


def handle_command(state, raw):
    parts = raw.split()
    if not parts:
        return "error: empty command"
    cmd, args = parts[0], parts[1:]
    if cmd not in COMMANDS:
        return "error: unknown command"
    if cmd == "quit":
        return "quit"
    if cmd == "calibrate" and len(args) == 1:
        return "ok" if calibrate(state, args[0]) else "error: already calibrated"
    if cmd == "observe" and len(args) == 2:
        return "ok" if observe(state, args[0], _parse_size(args[1])) else "error: observe rejected"
    if cmd == "capacity" and not args:
        return "capacity: %d/%d" % (data_capacity(state), state["storage_capacity"])
    if cmd == "cancel" and len(args) == 1:
        return "ok" if cancel_observe(state, args[0]) else "error: cancel rejected"
    if cmd == "record" and len(args) == 2:
        return "ok" if record(state, args[0], _parse_size(args[1])) else "error: record rejected"
    if cmd == "weather" and not args:
        return next_weather(state)
    return "error: bad arguments"


def _parse_size(text):
    try:
        return int(text)
    except ValueError:
        return -1


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
        result = handle_command(state, raw)
        if result == "quit":
            break
        print(result)


if __name__ == "__main__":
    main()
