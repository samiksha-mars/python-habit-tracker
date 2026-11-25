import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

from habit_tracker import main
from habits import HabitError, HabitTracker, current_streak, longest_streak

TODAY = date(2026, 11, 24)


def d(day):
    return date(2026, 11, day)


class StreakTest(unittest.TestCase):

    def test_current_streak_including_today(self):
        self.assertEqual(current_streak({d(22), d(23), d(24)}, TODAY), 3)

    def test_current_streak_counts_from_yesterday_if_today_unchecked(self):
        self.assertEqual(current_streak({d(22), d(23)}, TODAY), 2)

    def test_current_streak_broken(self):
        self.assertEqual(current_streak({d(20), d(21)}, TODAY), 0)

    def test_longest_streak(self):
        self.assertEqual(longest_streak({d(1), d(2), d(3), d(10), d(11)}), 3)
        self.assertEqual(longest_streak(set()), 0)

    def test_longest_streak_across_month_boundary(self):
        self.assertEqual(longest_streak({date(2026, 10, 31), date(2026, 11, 1)}), 2)


class TrackerTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "habits.json"
        self.tracker = HabitTracker(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_check_and_persist(self):
        self.tracker.add("Read")
        self.tracker.check("Read", d(23))
        self.tracker.check("Read", d(24))
        self.tracker.save()
        reloaded = HabitTracker(self.path)
        self.assertEqual(reloaded.stats(TODAY), [("Read", 2, 2, 2)])

    def test_duplicate_and_empty_names_rejected(self):
        self.tracker.add("Read")
        with self.assertRaises(HabitError):
            self.tracker.add("Read")
        with self.assertRaises(HabitError):
            self.tracker.add("  ")

    def test_double_check_and_bad_uncheck_rejected(self):
        self.tracker.add("Read")
        self.tracker.check("Read", TODAY)
        with self.assertRaises(HabitError):
            self.tracker.check("Read", TODAY)
        self.tracker.uncheck("Read", TODAY)
        with self.assertRaises(HabitError):
            self.tracker.uncheck("Read", TODAY)

    def test_unknown_habit(self):
        with self.assertRaises(HabitError):
            self.tracker.check("Nope", TODAY)

    def test_invalid_data_file_raises_habit_error(self):
        for content in ("{bad json", "[]", '{"Read": ["2026-13-01"]}', '{"Read": 5}'):
            self.path.write_text(content)
            with self.assertRaises(HabitError, msg=content):
                HabitTracker(self.path)

    def test_week_view(self):
        self.tracker.add("Run")
        self.tracker.check("Run", d(18))
        self.tracker.check("Run", d(24))
        self.assertEqual(self.tracker.week("Run", TODAY), [True, False, False, False, False, False, True])


class CliTest(unittest.TestCase):

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--file", str(self.path), *args])
        return code, out.getvalue() + err.getvalue()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "habits.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_flow(self):
        self.assertEqual(self.run_cli("add", "Read")[0], 0)
        self.assertEqual(self.run_cli("--date", "2026-11-23", "check", "Read")[0], 0)
        self.assertEqual(self.run_cli("--date", "2026-11-24", "check", "Read")[0], 0)
        code, output = self.run_cli("--date", "2026-11-24", "list")
        self.assertEqual(code, 0)
        self.assertRegex(output, r"Read\s+2\s+2\s+2")

    def test_error_exit_code(self):
        code, output = self.run_cli("check", "Missing")
        self.assertEqual(code, 1)
        self.assertIn("no habit named", output)

    def test_corrupt_file_is_reported_and_left_untouched(self):
        self.path.write_text("{bad json")
        code, output = self.run_cli("add", "Read")
        self.assertEqual(code, 1)
        self.assertIn("not a valid habits file", output)
        self.assertEqual(self.path.read_text(), "{bad json")

    def test_unwritable_file_is_reported(self):
        self.path = Path(self.tmp.name) / "missing-dir" / "habits.json"
        code, output = self.run_cli("add", "Read")
        self.assertEqual(code, 1)
        self.assertIn("cannot write", output)
        self.assertNotIn("Added", output)


if __name__ == "__main__":
    unittest.main()
