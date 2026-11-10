import csv
import os
import math
import random
from datetime import datetime, timedelta

TASKS_FILE = os.path.join("data", "tasks.csv")
FIELDNAMES = ["id", "name", "priority", "minutes", "status", "created"]
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_tasks():
    """Load tasks from CSV. Returns empty list on any failure."""
    try:
        with open(TASKS_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            tasks = []
            for row in reader:
                try: 
                    row["priority"] = int(row["priority"])
                    row["minutes"] = int(row["minutes"])
                    row["created"] = datetime.strptime(row["created"],DATETIME_FORMAT) # "created" becomes a datetime object built from the text using DATETIME FORMAT.
                except(ValueError, TypeError, KeyError):
                    continue 
                tasks.append(row)
            return tasks
    except FileNotFoundError: 
            return []
    except PermissionError: 
            print("Warning: Could not read tasks file — permission denied.")
            return []
    except csv.Error:
            print("Warning: Tasks file is malformed — starting with empty list")
            return []


def save_tasks(tasks):
    """Save the current task list to CSV. Warns on failure, does not crash."""
    try: 
        with open(TASKS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for task in tasks: 
                task_copy = task.copy()
                task_copy["created"] = task["created"].strftime(DATETIME_FORMAT) # The "created" value goes into the CSV as text in DATETIME_FORMAT.
                writer.writerow(task_copy)
    except PermissionError: 
        print("Warning: Could not save tasks — permission denied.")
    except OSError: 
        print("Warning: Could not save tasks — disk error.")

    
def get_valid_index(prompt, max_index):
    """Collect and return a valid integer index. Retries on bad input."""
    while True: 
        try: 
            number = int(input(prompt))
        except ValueError:
            print("Please enter a valid number.")
            continue
        if number < 1 or number > max_index: 
            print(f"Please enter a number between 1 and {max_index}.")
            continue
        return number 


def get_valid_task_name(seen_names):
    """Collect and return a non-empty task name."""
    while True:
        raw = input("Enter task name: ")
        name = raw.strip().capitalize()
        if not name:
            print("Error: Task name cannot be empty.")
            continue
        if name.lower() in seen_names:
            print("Duplicate task name — not added.")
            continue
        return name


def get_valid_priority():
    """Collect and return a valid integer priority (1, 2, or 3)."""
    while True:
        priority_input = input("Enter priority (1, 2, or 3): ")
        if priority_input in ["1","2","3"]:
            return int(priority_input)
        print("Error: priority must be 1, 2 or 3")

        
def get_valid_minutes():
    """Collect and return a valid positive integer of minutes."""
    while True:
        minutes_input = input("Estimated minutes: ") 
        if minutes_input.isdigit() and int(minutes_input) > 0: 
            return int(minutes_input)
        print("Error: Enter a positive whole number. Try again.")             

        
def get_priority_label(priority):
    """Take an integer priority, return the label string."""
    if priority == 1:
        return "HIGH"
    elif priority == 2: 
        return "MEDIUM"
    else:  
        return "LOW"

    
def display_task_summary(name, priority, minutes):
    """Print a formatted task summary."""
    priority_label = get_priority_label(priority)

    print("--- Task Summary ---")
    print(f"Task name: {name}")
    print(f"Priority: {priority} - {priority_label}") 
    print(f"Minutes: {minutes}") 


def get_valid_task(seen_names):
    """Call the three collection functions and return all values as a tuple."""
    # Call get_valid_task_name(), get_valid_priority(), get_valid_minutes()
    # Return all three values as a tuple: return name, priority, minutes
    name = get_valid_task_name(seen_names)
    priority = get_valid_priority()
    minutes = get_valid_minutes()

    return name, priority, minutes #save as tuples 


def add_task(tasks, seen_names):
    name, priority, minutes = get_valid_task(seen_names)  
    task = {
        "id": random.randint(1000,9999), 
        "created": datetime.now(), # return a DATETIME OBJECT 
        "name": name,
        "priority": priority,
        "minutes": minutes,
        "status": "pending"
    }
    tasks.append(task)
    seen_names.add(name.lower())
    return True


def task_age_display(task): 
    """Return a string describing how long ago the task was created."""
    time_now = datetime.now()
    time_task_created = task["created"]
    time_diff = time_now - time_task_created
    # Under one full day old: "Created today"
    if time_diff.days == 0:
         return "Created today"
    # Between one and two full days old: "Created yesterday"
    elif time_diff.days == 1 or time_diff.days == 2:
        return "Created yesterday"
    # Anything older: "Created N days ago", where N is the number of full days. A task five days old gives "Created 5 days ago"
    else:
        return (f"Created {time_diff.days} days ago")


## task_stats(tasks)
# Takes the full list and prints exactly three lines
def task_stats(tasks):
    total_tasks = len(tasks)

    total_minutes = 0 
    for task in tasks: 
        total_minutes += task["minutes"]

    total_hours = math.ceil(total_minutes/60)

    print(f"Total tasks : {total_tasks}")
    print(f"Total minutes : {total_minutes}")
    print(f"Total hours : {total_hours}")


def display_all_tasks(tasks):
    priorities = {}

    for task in tasks:
        priority = task["priority"] 

        if priority in priorities:
            priorities[priority].append(task)
        else:
            priorities[priority] = [task]

    for priority, priority_tasks in sorted(priorities.items()):
        print(f"Priority: {get_priority_label(priority)}")
        for task in priority_tasks:
            display_task(task) 
            print()


def display_task(task):
    """Print a formatted aligned summary of a single task dictionary."""
    print(f" {'ID':<12} {task["id"]}")
    print(f" {'Name':<12} {task['name']}")
    print(f" {'Priority':<12} {task['priority']}")
    print(f" {'Minutes':<12} {task['minutes']}")
    print(f" {'Status':<12} {task['status'].upper()}")
    print(f" {'Age':<12} {task_age_display(task)}")


def search_tasks(tasks, query):
    """Search tasks by name substring. Case-insensitive."""
    normalized = query.strip().lower()
    results = [t for t in tasks if normalized in t["name"].lower()]
    if not results:
        print("No matching tasks found.")
    for task in results:
        display_task(task)


## Menu
def show_menu(tasks, seen_names): 
    while True:
        print(" ---- Menu ---- ")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Remove Task")
        print("4. Task Count")
        print("5. Search Tasks")
        print("6. Stats")
        print("7. Random Task")
        print("8. Quit")

        choice = get_valid_index("Choose an option: ", 8)  

        if choice == 1:
            added = add_task(tasks, seen_names)
            
            if added:
                print("Task added.")
                save_tasks(tasks)
            else:
                print("Duplicate task name — not added.")

        elif choice == 2:
            display_all_tasks(tasks)
            if not tasks: 
                print("List is empty.")

        elif choice == 3:
            if not tasks:
                print("No tasks to remove.")
            else:
                for i, task in enumerate(tasks, start=1):
                    print(f"{i}. {task['name']}")
                number = get_valid_index("Task number: ", len(tasks))
                removed_task = tasks.pop(number - 1)
                seen_names.remove(removed_task["name"].lower())
                print(f"Removed: {removed_task['name']}.")
                save_tasks(tasks)

        elif choice == 4:
            num_task = 0 
            total_est_minutes = 0 

            for task in tasks: 
                num_task += 1
                total_est_minutes += task["minutes"] 

            print(f"Number of tasks: {num_task}")
            print(f"Total estimated minutes: {total_est_minutes}")

        elif choice == 5:
            query = input("Enter task name to search: ")
            search_tasks(tasks, query)

        # "Stats" calls task_stats()
        elif choice == 6: 
            task_stats(tasks)

        # "Random Task" picks one task at random from the list and shows it with display_task().
        elif choice == 7: 
            if not tasks:
                print("List is empty")
            else: 
                display_task(random.choice(tasks))

        # Quit 
        elif choice == 8:
            save_tasks(tasks)
            print("Goodbye!")
            break

        else: 
            print("That's an invalid choice.")


def main():
    os.makedirs("data", exist_ok=True)
    tasks = load_tasks()
    seen_names = {task["name"].lower() for task in tasks}
    show_menu(tasks, seen_names)

 
if __name__ == "__main__":       
    main()






