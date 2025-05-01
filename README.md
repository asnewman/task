# Task

![gif of Task](https://s4.gifyu.com/images/bLhET.gif)

A minimalist curses-based terminal task manager that allows you to manage your tasks with keyboard navigation.

## Features

- Simple task management with Todo/Done status
- Task prioritization (Low, Medium, High)
- Keyboard navigation
- Edit task title and priority
- Sort tasks by priority or creation date
- Filter tasks by status
- Data persistence in JSON format
- Custom data file path support

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Usage

Run the application:

```bash
# Use default tasks.json file
python main.py

# Use a custom data file
python main.py -f /path/to/custom-tasks.json
```

### Command Line Options

```
-f, --file FILE    Path to task data file (default: tasks.json)
```

### Demo Mode

The repository includes an example data file with sample tasks for demonstration:

```bash
python main.py -f example-tasks.json
```

### Keyboard Controls

- `j` or `↓`: Move down
- `k` or `↑`: Move up
- `a`: Add a new task
- `e`: Edit the selected task's title
- `p`: Edit the selected task's priority
- `s`: Sort by priority (ascending → descending → none)
- `c`: Sort by creation date (ascending → descending → none)
- `Space`: Toggle task status (Todo/Done)
- `d`: Delete selected task
- `t`: Filter Todo tasks (press again to show all)
- `f`: Filter Done tasks (press again to show all)
- `q`: Quit the application

## Code Architecture

The codebase consists of three main components:

1. **Data Model** (`task_model.py`): 
   - Defines task data structure and operations
   - Handles JSON file persistence

2. **User Interface** (`task_tui.py`):
   - Manages the curses-based terminal UI
   - Processes keyboard input and user interactions
   - Handles task display, sorting, and filtering

3. **Application Entry** (`main.py`):
   - Initializes the application
   - Sets up error handling
   - Processes command line arguments

All task data is automatically saved to the specified JSON file whenever changes are made.

## Task Properties

Each task has the following properties:
- Title: The name or description of the task
- Creation Date: Automatically set when the task is created
- Priority: Low, Medium, or High
- Status: Todo or Done
