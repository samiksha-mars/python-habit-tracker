"""Command-line interface for the habit tracker."""

import argparse
import sys
from datetime import date, timedelta

from habits import HabitError, HabitTracker

DEFAULT_FILE = "habits.json"


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date {value!r}, use YYYY-MM-DD")


def build_parser():
    parser = argparse.ArgumentParser(description="Track daily habits and streaks.")
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"data file (default: {DEFAULT_FILE})")
    parser.add_argument("--date", type=parse_date, default=None,
                        help="act as if today were this date (YYYY-MM-DD)")
    sub = parser.add_subparsers(dest="command", required=True)
    for command, help_text in [("add", "add a new habit"), ("remove", "delete a habit"),
                               ("check", "mark a habit done for the day"),
                               ("uncheck", "undo a check for the day")]:
        sub.add_parser(command, help=help_text).add_argument("name")
    sub.add_parser("list", help="show streaks for all habits")
    sub.add_parser("week", help="show the last 7 days for all habits")
    return parser


def print_list(tracker, today):
    rows = tracker.stats(today)
    if not rows:
        print("No habits yet. Add one with: habit_tracker.py add \"Read 20 minutes\"")
        return
    width = max(len("Habit"), *(len(name) for name, *_ in rows))
    print(f"{'Habit':<{width}}  Current  Longest  Total")
    for name, current, longest, total in rows:
        print(f"{name:<{width}}  {current:>7}  {longest:>7}  {total:>5}")


def print_week(tracker, today):
    names = sorted(tracker.habits)
    if not names:
        print("No habits yet.")
        return
    width = max(len(name) for name in names)
    header = " ".join((today - timedelta(days=offset)).strftime("%a")[:2] for offset in range(6, -1, -1))
    print(f"{'':<{width}}  {header}")
    for name in names:
        marks = "  ".join("✔" if done else "·" for done in tracker.week(name, today))
        print(f"{name:<{width}}  {marks}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    today = args.date or date.today()

    try:
        tracker = HabitTracker(args.file)
        if args.command == "add":
            tracker.add(args.name)
            message = f"Added habit {args.name!r}."
        elif args.command == "remove":
            tracker.remove(args.name)
            message = f"Removed habit {args.name!r}."
        elif args.command == "check":
            tracker.check(args.name, today)
            message = f"Checked {args.name!r} for {today}."
        elif args.command == "uncheck":
            tracker.uncheck(args.name, today)
            message = f"Unchecked {args.name!r} for {today}."
        elif args.command == "list":
            print_list(tracker, today)
            return 0
        elif args.command == "week":
            print_week(tracker, today)
            return 0
        tracker.save()
    except HabitError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Error: cannot write {args.file}: {e.strerror or e}", file=sys.stderr)
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
