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


class TestCoreExtra(unittest.TestCase):
    def test_09_illegal_command(self):
        state = core.new_game()
        self.assertIn("非法命令", core.dispatch(state, "hack the planet"))

    def test_10_empty_data_capacity(self):
        state = core.new_game()
        self.assertEqual(core.data_capacity(state), 0)

    def test_11_capacity_boundary(self):
        state = core.new_game()
        self.assertTrue(core.observe(state, "S1", 100))
        self.assertFalse(core.observe(state, "S2", 1))
        self.assertTrue(core.observe(state, "S1", 50))
        self.assertTrue(core.observe(state, "S2", 50))
        self.assertFalse(core.observe(state, "S3", 1))

    def test_12_observe_idempotent(self):
        state = core.new_game()
        self.assertTrue(core.observe(state, "S1", 10))
        self.assertTrue(core.observe(state, "S1", 10))
        self.assertEqual(core.data_capacity(state), 10)

    def test_13_cancel_idempotent(self):
        state = core.new_game()
        core.observe(state, "S1", 10)
        self.assertTrue(core.cancel_observe(state, "S1"))
        self.assertTrue(core.cancel_observe(state, "S1"))
        self.assertEqual(state["windows"]["S1"], "open")
        self.assertEqual(core.data_capacity(state), 0)

    def test_14_record_idempotent(self):
        state = core.new_game()
        self.assertTrue(core.record(state, "S1", 10))
        self.assertTrue(core.record(state, "S1", 10))
        self.assertEqual(core.data_capacity(state), 10)

    def test_15_duplicate_input_rejected(self):
        state = core.new_game()
        self.assertEqual(core.dispatch(state, "calibrate S1"), "ok")
        self.assertIn("重复", core.dispatch(state, "calibrate S1"))

    def test_16_negative_size_rejected(self):
        state = core.new_game()
        self.assertFalse(core.observe(state, "S1", -5))
        self.assertFalse(core.record(state, "S1", -5))

    def test_17_save_load_roundtrip(self):
        state = core.new_game()
        core.observe(state, "S1", 10)
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["data"], {"S1": 10})
        self.assertEqual(loaded["day"], state["day"])
