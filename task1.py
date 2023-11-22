import datetime

TASKS_FILE = 'tasks.txt'
PROJECT_DURATION_FILE = 'project_duration.txt'
START_DATE_FILE = 'start_date.txt'

def calculate_task_duration(optimistic, pessimistic, most_likely):
    return (optimistic + 4 * most_likely + pessimistic) / 6

def calculate_project_duration(tasks, dependency_graph):
    project_duration = 0

    for task in tasks:
        task_duration = calculate_task_duration(task['optimistic'], task['pessimistic'], task['most_likely'])
        dependencies = dependency_graph.get(task['name'], [])

        if dependencies:
            max_dependency_completion_time = max([project_duration for project_duration in dependencies])
            task_start_time = max_dependency_completion_time
        else:
            task_start_time = 0

        project_duration = max(project_duration, task_start_time + task_duration)

    return project_duration

def load_tasks_from_file():
    try:
        with open(TASKS_FILE, 'r') as file:
            tasks = []
            for line in file:
                task_info = line.strip().split(' - ')
                task_details = task_info[1].split()
                dependencies = task_info[3].split(',') if len(task_info) > 3 else []
                tasks.append({
                    'name': task_info[0],
                    'optimistic': float(task_details[0]),
                    'pessimistic': float(task_details[2]),
                    'most_likely': float(task_details[4]),
                    'assigned_to': task_details[3],
                    'dependencies': dependencies,
                    'priority': int(task_info[2]) if len(task_info) > 2 else 0
                })
            return tasks
    except FileNotFoundError:
        return []

def save_tasks_to_file(tasks):
    with open(TASKS_FILE, 'w') as file:
        for task in tasks:
            dependencies = ','.join(task['dependencies']) if task['dependencies'] else ''
            file.write(f"{task['name']} - {task['optimistic']} days - {task['priority']} - {task['assigned_to']} - {dependencies}\n")

def calculate_task_duration_from_list(tasks, task_name):
    task = next((task for task in tasks if task['name'] == task_name), None)
    if task:
        total_duration = 0

        if not task['dependencies']:
            return task['optimistic']

        for dep_task_name in task['dependencies']:
            dep_duration = calculate_task_duration_from_list(tasks, dep_task_name)
            if dep_duration is not None:
                total_duration += dep_duration
            else:
                print(f"Dependency task '{dep_task_name}' for task '{task_name}' not found.")
                return None

        return total_duration + task['optimistic']
    else:
        return None

def display_tasks(tasks):
    if not tasks:
        print("No tasks added yet.")
    else:
        print("Tasks:")
        for idx, task in enumerate(tasks, start=1):
            dependencies = ', '.join(task['dependencies']) if task['dependencies'] else 'None'
            print(f"{idx}. {task['name']} - {task['optimistic']} days - Priority: {task['priority']} - Assigned to: {task['assigned_to']} - Dependencies: {dependencies}")

def edit_task(tasks):
    display_tasks(tasks)
    try:
        task_idx = int(input("Enter the task number to edit: ")) - 1
        if 0 <= task_idx < len(tasks):
            new_name = input("Enter new task name (leave blank to keep the same): ")
            new_optimistic = input(f"Enter new optimistic estimate for Task {new_name} (leave blank to keep the same): ")
            new_pessimistic = input(f"Enter new pessimistic estimate for Task {new_name} (leave blank to keep the same): ")
            new_most_likely = input(f"Enter new most likely estimate for Task {new_name} (leave blank to keep the same): ")
            new_assigned_to = input("Enter new assigned team member (leave blank to keep the same): ")
            new_dependencies = input("Enter new task dependencies (comma-separated, leave blank for none): ")
            new_priority = input("Enter new task priority (integer value, leave blank to keep the same): ")

            if new_name:
                tasks[task_idx]['name'] = new_name
            if new_optimistic:
                tasks[task_idx]['optimistic'] = float(new_optimistic)
            if new_pessimistic:
                tasks[task_idx]['pessimistic'] = float(new_pessimistic)
            if new_most_likely:
                tasks[task_idx]['most_likely'] = float(new_most_likely)
            if new_assigned_to:
                tasks[task_idx]['assigned_to'] = new_assigned_to
            if new_dependencies:
                tasks[task_idx]['dependencies'] = [dep.strip() for dep in new_dependencies.split(',')]
            if new_priority:
                tasks[task_idx]['priority'] = int(new_priority)

            print("Task edited successfully.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input for task number, estimates, or priority.")

def delete_task(tasks):
    display_tasks(tasks)
    try:
        task_idx = int(input("Enter the task number to delete: ")) - 1
        if 0 <= task_idx < len(tasks):
            del tasks[task_idx]
            print("Task deleted successfully.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input for task number.")

def generate_gantt_chart(tasks):
    if not tasks:
        print("No tasks added yet.")
        return

    tasks.sort(key=lambda x: x['assigned_to'])
    for assigned_to in set(task['assigned_to'] for task in tasks):
        print(f"{'=' * 30}")
        print(f"Team Member: {assigned_to}")
        print(f"{'=' * 30}")

        tasks_assigned = [task for task in tasks if task['assigned_to'] == assigned_to]
        tasks_assigned.sort(key=lambda x: x['optimistic'], reverse=True)

        for task in tasks_assigned:
            print(f"{task['name']}: {'#' * int(task['optimistic'])}")

def add_task(tasks):
    task_name = input("Enter task name: ")
    try:
        optimistic = float(input("Enter optimistic estimate in days: "))
        pessimistic = float(input("Enter pessimistic estimate in days: "))
        most_likely = float(input("Enter most likely estimate in days: "))
        assigned_to = input("Enter team member name: ")
        dependencies = input("Enter task dependencies (comma-separated, leave blank for none): ")
        task_dependencies = [dep.strip() for dep in dependencies.split(',')] if dependencies else []
        priority = int(input("Enter task priority (integer value, 0 being lowest): "))
        
        tasks.append({
            'name': task_name,
            'optimistic': optimistic,
            'pessimistic': pessimistic,
            'most_likely': most_likely,
            'assigned_to': assigned_to,
            'dependencies': task_dependencies,
            'priority': priority
        })
        print("Task added successfully.")
    except ValueError:
        print("Please enter valid numeric values for estimates or priority.")

def main():
    tasks = load_tasks_from_file()

    while True:
        print("\nOptions:")
        print("1. Add Task")
        print("2. Display Tasks")
        print("3. Calculate Task Duration")
        print("4. Edit Task")
        print("5. Delete Task")
        print("6. Generate Gantt Chart")
        print("7. Calculate Project Duration")
        print("8. Save Tasks to File")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_task(tasks)

        elif choice == '2':
            display_tasks(tasks)

        elif choice == '3':
            task_name = input("Enter the task name to calculate duration: ")
            duration = calculate_task_duration_from_list(tasks, task_name)
            if duration is not None:
                print(f"Duration for task '{task_name}': {duration} days")
            else:
                print(f"Task '{task_name}' not found.")

        elif choice == '4':
            edit_task(tasks)

        elif choice == '5':
            delete_task(tasks)

        elif choice == '6':
            generate_gantt_chart(tasks)

        elif choice == '7':
            dependency_graph = {}
            for task in tasks:
                dependency_graph[task['name']] = task['dependencies']
            project_duration = calculate_project_duration(tasks, dependency_graph)
            print(f"The expected project duration is: {project_duration:.2f} days.")

        elif choice == '8':
            save_tasks_to_file(tasks)
            print("Tasks saved to file 'tasks.txt'")

        elif choice == '9':
            save_tasks_to_file(tasks)
            break

        else:
            print("Invalid choice. Please select a valid option.")

#if _name_ == "main":
main()