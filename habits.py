"""Habit tracking logic and JSON storage."""

import json
from datetime import date, timedelta
from pathlib import Path


class HabitError(Exception):
    pass


def current_streak(days, today):
    """Consecutive checked days ending today (or yesterday, if today isn't checked yet)."""
    checked = set(days)
    day = today if today in checked else today - timedelta(days=1)
    streak = 0
    while day in checked:
        streak += 1
        day -= timedelta(days=1)
    return streak


def longest_streak(days):
    longest = run = 0
    previous = None
    for day in sorted(set(days)):
        run = run + 1 if previous is not None and day - previous == timedelta(days=1) else 1
        longest = max(longest, run)
        previous = day
    return longest


class HabitTracker:
    """Habits are stored as {"name": ["YYYY-MM-DD", ...]} in a JSON file."""

    def __init__(self, path):
        self.path = Path(path)
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.habits = {name: {date.fromisoformat(d) for d in days} for name, days in raw.items()}
        else:
            self.habits = {}

    def save(self):
        data = {name: sorted(d.isoformat() for d in days) for name, days in self.habits.items()}
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _get(self, name):
        if name not in self.habits:
            raise HabitError(f"no habit named {name!r}")
        return self.habits[name]

    def add(self, name):
        name = name.strip()
        if not name:
            raise HabitError("habit name cannot be empty")
        if name in self.habits:
            raise HabitError(f"habit {name!r} already exists")
        self.habits[name] = set()

    def remove(self, name):
        self._get(name)
        del self.habits[name]

    def check(self, name, day):
        days = self._get(name)
        if day in days:
            raise HabitError(f"{name!r} is already checked for {day}")
        days.add(day)

    def uncheck(self, name, day):
        days = self._get(name)
        if day not in days:
            raise HabitError(f"{name!r} is not checked for {day}")
        days.remove(day)

    def stats(self, today):
        """Return [(name, current_streak, longest_streak, total_days)] sorted by name."""
        return [(name, current_streak(days, today), longest_streak(days), len(days))
                for name, days in sorted(self.habits.items())]

    def week(self, name, today):
        """Return 7 booleans for the last 7 days, oldest first."""
        days = self._get(name)
        return [today - timedelta(days=offset) in days for offset in range(6, -1, -1)]
