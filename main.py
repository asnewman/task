#!/usr/bin/env python3
import sys
import os
import argparse
from curses import wrapper

from task_model import TaskManager
from task_tui import TaskTUI


def parse_args():
    parser = argparse.ArgumentParser(description="Terminal-based Task Manager")
    parser.add_argument(
        "-f", "--file",
        default="tasks.json",
        help="Path to task data file (default: tasks.json)"
    )
    return parser.parse_args()


def main(stdscr):
    args = parse_args()
    file_path = args.file
    
    # Make sure directory exists
    file_dir = os.path.dirname(file_path)
    if file_dir and not os.path.exists(file_dir):
        os.makedirs(file_dir)
        
    task_manager = TaskManager(file_path=file_path)
    app = TaskTUI(stdscr, task_manager)
    app.run()


if __name__ == "__main__":
    try:
        wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0) 