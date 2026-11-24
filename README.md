# Python Habit Tracker

A small command-line habit tracker. Add the habits you want to build, check them
off each day, and watch your streaks grow. Data is stored in a JSON file and the
tool uses only the Python standard library.

## Features

- Add and remove habits
- Check a habit off for today (or any date with `--date`), or undo a check
- Current and longest streak for every habit
- 7-day overview grid
- JSON storage, path configurable with `--file`

## Usage

```bash
python3 habit_tracker.py add "Read 20 minutes"
python3 habit_tracker.py add Exercise

python3 habit_tracker.py check Exercise          # done today
python3 habit_tracker.py --date 2026-11-23 check Exercise   # back-fill a day
python3 habit_tracker.py uncheck Exercise        # undo today's check

python3 habit_tracker.py list
python3 habit_tracker.py week
python3 habit_tracker.py remove Exercise
```

```
$ python3 habit_tracker.py list
Habit            Current  Longest  Total
Exercise               1        3      4
Read 20 minutes        5        5      5

$ python3 habit_tracker.py week
                 We Th Fr Sa Su Mo Tu
Exercise         ✔  ✔  ✔  ·  ·  ✔  ·
Read 20 minutes  ·  ·  ✔  ✔  ✔  ✔  ✔
```

The current streak counts consecutive days up to today. If you haven't checked a
habit off yet today, the streak from yesterday is still shown, so it doesn't
reset in the morning.

Data is saved to `habits.json` in the current directory; use `--file` to choose
another location.

## Tests

```bash
python3 -m unittest test_habits.py
```
