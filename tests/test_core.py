import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_calibrate(self):
        state = core.new_game()
        self.assertTrue(core.calibrate(state, "S1"))
        self.assertFalse(core.calibrate(state, "S1"))

    def test_02_no_observe_in_storm(self):
        state = core.new_game()
        state["storm"] = True
        result = core.observe(state, "S1", 10)
        self.assertFalse(result)

    def test_03_capacity_by_bytes(self):
        state = core.new_game()
        state["data"] = {"A": 30, "B": 30, "C": 30}
        self.assertEqual(core.data_capacity(state), 90)

    def test_04_calibrate_sets_flag(self):
        state = core.new_game()
        core.calibrate(state, "S1")
        self.assertTrue(state["calibrated"].get("S1"))

    def test_05_cancel_releases_window(self):
        state = core.new_game()
        state["windows"] = {"W1": "booked"}
        core.cancel_observe(state, "W1")
        self.assertEqual(state["windows"]["W1"], "open")

    def test_06_no_record_on_fault(self):
        state = core.new_game()
        state["fault"] = True
        result = core.record(state, "S1", 10)
        self.assertFalse(result)

    def test_07_weather_order(self):
        state = core.new_game()
        self.assertEqual(core.next_weather(state), "clear")

    def test_08_load_preserves_day(self):
        state = core.new_game()
        state["day"] = 5
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["day"], 5)


if __name__ == "__main__":
    unittest.main()
