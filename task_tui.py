import curses
import sys
from curses import wrapper
from typing import List, Tuple, Dict
from enum import Enum

from task_model import Priority, TaskManager, TaskStatus


class SortMode(Enum):
    NONE = 0
    PRIORITY_ASC = 1
    PRIORITY_DESC = 2
    DATE_ASC = 3
    DATE_DESC = 4


class TaskTUI:
    def __init__(self, stdscr, task_manager: TaskManager):
        self.stdscr = stdscr
        self.task_manager = task_manager
        self.current_row = 0
        self.top_line = 0
        self.filter_status = TaskStatus.TODO  # Default: show only todos
        self.sort_mode = SortMode.PRIORITY_DESC  # Default: sort by priority descending
        self.running = True
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # Default
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Done
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Medium priority
        curses.init_pair(4, curses.COLOR_RED, -1)  # High priority
        curses.init_pair(5, curses.COLOR_CYAN, -1)  # Selected row
        
        # Hide cursor
        curses.curs_set(0)
        
        # Set up key handling
        self.stdscr.keypad(True)
        self.stdscr.timeout(100)  # For handling resize

    def get_priority_color(self, priority: Priority) -> int:
        if priority == Priority.HIGH:
            return curses.color_pair(4)
        elif priority == Priority.MEDIUM:
            return curses.color_pair(3)
        else:
            return curses.color_pair(1)

    def get_status_color(self, status: TaskStatus) -> int:
        if status == TaskStatus.DONE:
            return curses.color_pair(2)
        else:
            return curses.color_pair(1)

    def get_filtered_and_sorted_tasks(self) -> List:
        """Get tasks with both filtering and sorting applied, including original indices"""
        # First, get all tasks with their original indices
        all_tasks_with_indices = [(i, task) for i, task in enumerate(self.task_manager.tasks)]
        
        # Apply filtering if needed
        if self.filter_status is not None:
            all_tasks_with_indices = [(i, task) for i, task in all_tasks_with_indices 
                                     if task.status == self.filter_status]
        
        # Apply sorting if needed
        if self.sort_mode != SortMode.NONE:
            if self.sort_mode == SortMode.PRIORITY_ASC:
                all_tasks_with_indices = sorted(all_tasks_with_indices, key=lambda x: x[1].priority.value)
            elif self.sort_mode == SortMode.PRIORITY_DESC:
                all_tasks_with_indices = sorted(all_tasks_with_indices, key=lambda x: x[1].priority.value, reverse=True)
            elif self.sort_mode == SortMode.DATE_ASC:
                all_tasks_with_indices = sorted(all_tasks_with_indices, key=lambda x: x[1].creation_date)
            elif self.sort_mode == SortMode.DATE_DESC:
                all_tasks_with_indices = sorted(all_tasks_with_indices, key=lambda x: x[1].creation_date, reverse=True)
        
        return all_tasks_with_indices

    def get_visible_tasks(self) -> List:
        tasks = self.get_filtered_and_sorted_tasks()
        max_y, _ = self.stdscr.getmaxyx()
        return tasks[self.top_line:self.top_line + max_y - 4]  # Leave space for header and footer

    def get_original_index(self, display_index: int) -> int:
        """Gets the original task list index from the display index (accounts for sorting and filtering)"""
        tasks = self.get_filtered_and_sorted_tasks()
        if 0 <= display_index < len(tasks):
            # The first element of each tuple is the original index
            return tasks[display_index][0]
        return -1

    def cycle_sort_mode(self, sort_type: str) -> None:
        # Reset cursor position when changing sort mode
        self.current_row = 0
        self.top_line = 0
        
        if sort_type == 'priority':
            if self.sort_mode == SortMode.PRIORITY_ASC:
                self.sort_mode = SortMode.PRIORITY_DESC
            elif self.sort_mode == SortMode.PRIORITY_DESC:
                self.sort_mode = SortMode.NONE
            else:
                self.sort_mode = SortMode.PRIORITY_ASC
        elif sort_type == 'date':
            if self.sort_mode == SortMode.DATE_ASC:
                self.sort_mode = SortMode.DATE_DESC
            elif self.sort_mode == SortMode.DATE_DESC:
                self.sort_mode = SortMode.NONE
            else:
                self.sort_mode = SortMode.DATE_ASC

    def add_task_prompt(self) -> None:
        # Get task title
        curses.echo()
        curses.curs_set(1)
        self.stdscr.addstr(0, 0, "Enter task title (ESC to cancel): ".ljust(curses.COLS))
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        
        # Get user input for title
        title = ""
        while True:
            key = self.stdscr.getch()
            if key == 27:  # ESC
                curses.noecho()
                curses.curs_set(0)
                return
            elif key == 10:  # Enter
                if title.strip():
                    break
            elif key == curses.KEY_BACKSPACE or key == 127:
                title = title[:-1]
                self.stdscr.addstr(0, len("Enter task title (ESC to cancel): "), title.ljust(curses.COLS - len("Enter task title (ESC to cancel): ")))
            elif 32 <= key <= 126:  # Printable characters
                title += chr(key)
            
            self.stdscr.addstr(0, len("Enter task title (ESC to cancel): "), title.ljust(curses.COLS - len("Enter task title (ESC to cancel): ")))
            self.stdscr.clrtoeol()
            self.stdscr.refresh()
        
        # Get priority
        self.stdscr.addstr(1, 0, "Select priority (1=Low, 2=Medium, 3=High): ".ljust(curses.COLS))
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        
        priority = Priority.LOW
        while True:
            key = self.stdscr.getch()
            if key == 27:  # ESC
                curses.noecho()
                curses.curs_set(0)
                return
            elif key == 49:  # 1
                priority = Priority.LOW
                break
            elif key == 50:  # 2
                priority = Priority.MEDIUM
                break
            elif key == 51:  # 3
                priority = Priority.HIGH
                break
        
        # Add the task
        self.task_manager.add_task(title, priority)
        curses.noecho()
        curses.curs_set(0)

    def edit_task_title_prompt(self) -> None:
        tasks = self.get_filtered_and_sorted_tasks()
        if not tasks or not (0 <= self.current_row < len(tasks)):
            return
        
        # Get the original task index
        task_index = self.get_original_index(self.current_row)
        if task_index < 0:
            return
            
        current_title = tasks[self.current_row][1].title
        
        # Show prompt
        curses.echo()
        curses.curs_set(1)
        prompt = "Edit task title (ESC to cancel): "
        self.stdscr.addstr(0, 0, prompt.ljust(curses.COLS))
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        
        # Get user input with current title as default
        title = current_title
        self.stdscr.addstr(0, len(prompt), title)
        
        while True:
            key = self.stdscr.getch()
            if key == 27:  # ESC
                curses.noecho()
                curses.curs_set(0)
                return
            elif key == 10:  # Enter
                if title.strip():
                    break
            elif key == curses.KEY_BACKSPACE or key == 127:
                title = title[:-1]
                self.stdscr.addstr(0, len(prompt), title.ljust(curses.COLS - len(prompt)))
            elif 32 <= key <= 126:  # Printable characters
                title += chr(key)
            
            self.stdscr.addstr(0, len(prompt), title.ljust(curses.COLS - len(prompt)))
            self.stdscr.clrtoeol()
            self.stdscr.refresh()
        
        # Update the task title
        if title != current_title:
            self.task_manager.update_task_title(task_index, title)
        
        curses.noecho()
        curses.curs_set(0)

    def edit_task_priority_prompt(self) -> None:
        tasks = self.get_filtered_and_sorted_tasks()
        if not tasks or not (0 <= self.current_row < len(tasks)):
            return
            
        # Get the original task index
        task_index = self.get_original_index(self.current_row)
        if task_index < 0:
            return
            
        current_priority = tasks[self.current_row][1].priority
        
        # Show prompt
        prompt = f"Current priority: {current_priority.name}. Select new priority (1=Low, 2=Medium, 3=High, ESC to cancel): "
        self.stdscr.addstr(0, 0, prompt.ljust(curses.COLS))
        self.stdscr.clrtoeol()
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key == 27:  # ESC
                return
            elif key == 49:  # 1
                new_priority = Priority.LOW
                break
            elif key == 50:  # 2
                new_priority = Priority.MEDIUM
                break
            elif key == 51:  # 3
                new_priority = Priority.HIGH
                break
        
        # Update the task priority
        if new_priority != current_priority:
            self.task_manager.update_task_priority(task_index, new_priority)

    def handle_input(self) -> None:
        tasks = self.get_filtered_and_sorted_tasks()
        key = self.stdscr.getch()
        
        if key == curses.KEY_RESIZE:
            # Handle terminal resize
            self.stdscr.clear()
        elif key == ord('q'):
            self.running = False
        elif key == ord('j') or key == curses.KEY_DOWN:
            if self.current_row < len(tasks) - 1:
                self.current_row += 1
                max_y, _ = self.stdscr.getmaxyx()
                if self.current_row >= self.top_line + max_y - 4:
                    self.top_line += 1
        elif key == ord('k') or key == curses.KEY_UP:
            if self.current_row > 0:
                self.current_row -= 1
                if self.current_row < self.top_line:
                    self.top_line -= 1
        elif key == ord('a'):
            self.add_task_prompt()
        elif key == ord('e'):
            self.edit_task_title_prompt()
        elif key == ord('p'):
            self.edit_task_priority_prompt()
        elif key == ord('d'):
            if tasks and 0 <= self.current_row < len(tasks):
                # Get the original task index for deletion
                task_index = self.get_original_index(self.current_row)
                if task_index >= 0:
                    self.task_manager.delete_task(task_index)
                    # Adjust cursor if needed
                    tasks_after = self.get_filtered_and_sorted_tasks()
                    if self.current_row >= len(tasks_after):
                        self.current_row = max(0, len(tasks_after) - 1)
        elif key == ord(' '):
            if tasks and 0 <= self.current_row < len(tasks):
                # Get the original task index for toggle
                task_index = self.get_original_index(self.current_row)
                if task_index >= 0:
                    # Toggle the status
                    self.task_manager.toggle_task_status(task_index)
                    
                    # If filtering by status, the toggled task may disappear
                    # Adjust the selection if needed
                    if self.filter_status is not None:
                        tasks_after = self.get_filtered_and_sorted_tasks()
                        if self.current_row >= len(tasks_after):
                            self.current_row = max(0, len(tasks_after) - 1)
        elif key == ord('t'):
            if self.filter_status == TaskStatus.TODO:
                self.filter_status = None
            else:
                self.filter_status = TaskStatus.TODO
            self.current_row = 0
            self.top_line = 0
        elif key == ord('f'):
            if self.filter_status == TaskStatus.DONE:
                self.filter_status = None
            else:
                self.filter_status = TaskStatus.DONE
            self.current_row = 0
            self.top_line = 0
        elif key == ord('s'):
            self.cycle_sort_mode('priority')
        elif key == ord('c'):
            self.cycle_sort_mode('date')

    def draw_screen(self) -> None:
        self.stdscr.clear()
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Draw header
        header = "Task Manager"
        self.stdscr.addstr(0, (max_x - len(header)) // 2, header, curses.A_BOLD)
        
        # Show filter and sort information
        filter_status = "All Tasks"
        if self.filter_status == TaskStatus.TODO:
            filter_status = "Todo Tasks"
        elif self.filter_status == TaskStatus.DONE:
            filter_status = "Done Tasks"
        
        sort_status = ""
        if self.sort_mode == SortMode.PRIORITY_ASC:
            sort_status = "Sort: Priority ↑"
        elif self.sort_mode == SortMode.PRIORITY_DESC:
            sort_status = "Sort: Priority ↓"
        elif self.sort_mode == SortMode.DATE_ASC:
            sort_status = "Sort: Date ↑"
        elif self.sort_mode == SortMode.DATE_DESC:
            sort_status = "Sort: Date ↓"
        
        self.stdscr.addstr(1, 0, f"Filter: {filter_status}", curses.A_BOLD)
        if sort_status:
            self.stdscr.addstr(1, max_x - len(sort_status) - 1, sort_status, curses.A_BOLD)
        
        self.stdscr.addstr(2, 0, "=" * (max_x - 1))
        
        # Draw tasks
        visible_tasks = self.get_visible_tasks()
        all_tasks = self.get_filtered_and_sorted_tasks()
        
        for i, (_, task) in enumerate(visible_tasks):
            row_position = i + 3  # Start after header
            
            # Skip if we're outside the visible area
            if row_position >= max_y - 1:
                break
            
            status_symbol = "[ ]"
            if task.status == TaskStatus.DONE:
                status_symbol = "[✓]"
            
            # Format the task line with proper truncation
            task_line = f"{status_symbol} {task.title}"
            date_str = f"({task.creation_date.split('T')[0]})"
            priority_str = f"[{task.priority.name}]"
            
            # Calculate space available for title
            space_for_title = max_x - len(status_symbol) - len(date_str) - len(priority_str) - 4
            if len(task.title) > space_for_title:
                task_line = f"{status_symbol} {task.title[:space_for_title-3]}..."
            
            # Add each part with appropriate color
            is_selected = self.current_row == i + self.top_line
            attr = curses.A_REVERSE if is_selected else 0
            
            # Status
            self.stdscr.addstr(row_position, 0, status_symbol, self.get_status_color(task.status) | attr)
            
            # Title
            title_x = len(status_symbol) + 1
            title_width = min(len(task.title), space_for_title)
            self.stdscr.addstr(row_position, title_x, task.title[:title_width], attr)
            
            # Fill any spaces
            if len(task.title) < space_for_title:
                self.stdscr.addstr(row_position, title_x + len(task.title), " " * (space_for_title - len(task.title)), attr)
            
            # Date
            date_x = max_x - len(date_str) - len(priority_str) - 1
            self.stdscr.addstr(row_position, date_x, date_str, attr)
            
            # Priority
            priority_x = max_x - len(priority_str) - 1
            self.stdscr.addstr(row_position, priority_x, priority_str, self.get_priority_color(task.priority) | attr)
        
        # Draw footer with help
        footer_text = "a:Add  e:Edit  p:Priority  s:Sort Priority  c:Sort Date  Space:Toggle  d:Delete  t:Todo  f:Done  q:Quit"
        footer_y = max_y - 1
        self.stdscr.addstr(footer_y, 0, "=" * (max_x - 1))
        if len(footer_text) < max_x:
            self.stdscr.addstr(footer_y, 0, footer_text)
        
        # Draw scrollbar if needed
        if len(all_tasks) > max_y - 4:
            scrollbar_height = max(1, (max_y - 4) * (max_y - 4) // len(all_tasks))
            scrollbar_top = 3 + (max_y - 4 - scrollbar_height) * self.top_line // max(1, len(all_tasks) - (max_y - 4))
            for i in range(scrollbar_height):
                if scrollbar_top + i < max_y - 1:
                    self.stdscr.addstr(scrollbar_top + i, max_x - 1, "█")
        
        self.stdscr.refresh()

    def run(self) -> None:
        while self.running:
            self.draw_screen()
            self.handle_input()


def main(stdscr):
    task_manager = TaskManager()
    app = TaskTUI(stdscr, task_manager)
    app.run()


if __name__ == "__main__":
    try:
        wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0) 