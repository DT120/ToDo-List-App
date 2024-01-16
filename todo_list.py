import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import json

# CustomTkinter settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ToDoApp:
    def __init__(self, root):
        self.root = root
        root.title("Weekly To-Do List")
        root.geometry("800x600")
        root.resizable(False, False)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        self.week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.current_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.tasks = {}

        self.nav_frame = ctk.CTkFrame(root, corner_radius=10)
        self.nav_frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)

        self.prev_week_button = ctk.CTkButton(self.nav_frame, text="<", command=self.prev_week, width=40)
        self.prev_week_button.grid(row=0, column=0, sticky="w", padx=10)

        self.next_week_button = ctk.CTkButton(self.nav_frame, text=">", command=self.next_week, width=40)
        self.next_week_button.grid(row=0, column=2, sticky="e", padx=10)

        self.week_frame = ctk.CTkFrame(self.nav_frame, corner_radius=10)
        self.week_frame.grid(row=0, column=1, sticky="new", padx=10, pady=10)

        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.scheduler_frame = ctk.CTkFrame(self.notebook, corner_radius=10)
        self.notebook.add(self.scheduler_frame, text='Schedule')

        self.todo_list_frame = ctk.CTkFrame(self.notebook, corner_radius=10)
        self.notebook.add(self.todo_list_frame, text='To-Do List')

        self.task_list_frame = ctk.CTkFrame(self.scheduler_frame, corner_radius=10)
        self.task_list_frame.grid(sticky="nsew", padx=10, pady=10)

        # Create a frame for the bottom buttons
        self.bottom_button_frame = ctk.CTkFrame(root, corner_radius=10)
        self.bottom_button_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        # Configure grid column weights
        self.bottom_button_frame.grid_columnconfigure(0, weight=1)
        self.bottom_button_frame.grid_columnconfigure(1, weight=0)
        self.bottom_button_frame.grid_columnconfigure(2, weight=0)
        self.bottom_button_frame.grid_columnconfigure(3, weight=1)

        # Place the Add Scheduled Task button in the middle-left
        self.add_scheduled_task_button = ctk.CTkButton(self.bottom_button_frame, text="Add Scheduled Task", 
                                                       command=lambda: self.open_new_task_window('Scheduled'))
        self.add_scheduled_task_button.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        # Place the Add To-Do Task button in the middle-right
        self.add_todo_task_button = ctk.CTkButton(self.bottom_button_frame, text="Add To-Do Task", 
                                                  command=lambda: self.open_new_task_window('To-Do'))
        self.add_todo_task_button.grid(row=0, column=2, pady=10, padx=10, sticky="ew")


        self.load_tasks()
        self.setup_week_view()
        self.show_day_tasks(str(self.current_week_start))
        self.notebook.select(self.scheduler_frame)

    def setup_week_view(self):
        for widget in self.week_frame.winfo_children():
            widget.destroy()

        for i, day in enumerate(self.week_days):
            date = self.current_week_start + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            btn = ctk.CTkButton(self.week_frame, text=f"{day}\n{date_str}", 
                                command=lambda d=date_str: self.show_day_tasks(d))
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="ew")

        for i in range(len(self.week_days)):
            self.week_frame.grid_columnconfigure(i, weight=1)

        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        today = datetime.now().date()
        for widget in self.week_frame.winfo_children():
            date_str = widget.cget("text").split("\n")[1]
            widget_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if widget_date == today:
                widget.configure(fg_color="#00b4d8")
            elif widget_date < today:
                widget.configure(fg_color="#caf0f8")
            else:
                widget.configure(fg_color="#90e0ef")

        for widget in self.week_frame.winfo_children():
            widget.configure(text_color="black")

        self.prev_week_button.configure(text_color="black")
        self.next_week_button.configure(text_color="black")

    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self.setup_week_view()

    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.setup_week_view()

    def show_day_tasks(self, date):
        for frame in [self.task_list_frame, self.todo_list_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

        self.selected_date = date
        date_tasks = self.tasks.get(date, {'todo': [], 'schedule': []})
        sorted_schedule = sorted(date_tasks['schedule'], key=lambda x: x['time'])

        for task in sorted_schedule:
            task_frame = ctk.CTkFrame(self.task_list_frame, corner_radius=10)
            task_frame.pack(pady=2, fill="x", expand=True)
            
            # Convert 24-hour format to 12-hour format for display
            display_time = datetime.strptime(task['time'], '%H:%M').strftime('%I:%M %p').lstrip('0')
            task_label = ctk.CTkLabel(task_frame, text=f"{display_time} - {task['name']}")
            task_label.pack(side="left", fill="x", expand=True)
            remove_button = ctk.CTkButton(task_frame, text="Remove",
                                        command=lambda t=task: self.remove_task(t), width=10)
            remove_button.pack(side="right")

        sorted_todo = sorted(date_tasks['todo'], key=lambda x: x['name'])
        for task in sorted_todo:
            task_frame = ctk.CTkFrame(self.todo_list_frame, corner_radius=10)
            task_frame.pack(pady=2, fill="x", expand=True)
            
            # Create a checkbox and associate it with the task's 'completed' status
            completed = tk.BooleanVar(value=task.get("completed", False))
            check_button = ctk.CTkCheckBox(task_frame, variable=completed, text="",
                                           command=lambda t=task: self.toggle_task_completion(t, completed))
            check_button.pack(side="left")
            
            # Now pack the label and remove button alongside the checkbox
            task_label = ctk.CTkLabel(task_frame, text=task['name'])
            task_label.pack(side="left", fill="x", expand=True)
            remove_button = ctk.CTkButton(task_frame, text="Remove",
                                          command=lambda t=task: self.remove_task(t), width=10)
            remove_button.pack(side="right")

        if date == str(datetime.now().date()):
            self.notebook.select(self.scheduler_frame)
        else:
            self.notebook.select(self.todo_list_frame)

    def open_new_task_window(self, task_type):
        self.new_task_window = tk.Toplevel(self.root)
        self.new_task_window.title(f"Create New {task_type} Task")
        self.new_task_window.geometry("400x300")
        
        task_name_label = ctk.CTkLabel(self.new_task_window, text="Task Name:")
        task_name_label.pack(pady=2)
        self.task_name_entry = ctk.CTkEntry(self.new_task_window, placeholder_text="Enter task name")
        self.task_name_entry.pack(pady=2, fill="x")
        self.task_name_entry.focus()

        if task_type == 'Scheduled':
            task_time_label = ctk.CTkLabel(self.new_task_window, text="Task Time:")
            task_time_label.pack(pady=2)
            self.hour_var = tk.StringVar(self.new_task_window)
            self.minute_var = tk.StringVar(self.new_task_window)
            self.am_pm_var = tk.StringVar(self.new_task_window)

            hour_menu = ttk.Combobox(self.new_task_window, textvariable=self.hour_var, 
                                        values=[f"{h:02d}" for h in range(1, 13)])
            hour_menu.pack(pady=2, fill="x")

            minute_menu = ttk.Combobox(self.new_task_window, textvariable=self.minute_var, 
                                        values=[f"{m:02d}" for m in range(60)])
            minute_menu.pack(pady=2, fill="x")

            am_pm_menu = ttk.Combobox(self.new_task_window, textvariable=self.am_pm_var, values=['AM', 'PM'])
            am_pm_menu.pack(pady=2, fill="x")
            
            # Define self.time_vars here after creating the comboboxes
            self.time_vars = {
                'hour_var': self.hour_var,
                'minute_var': self.minute_var,
                'am_pm_var': self.am_pm_var
            }            

        create_task_button = ctk.CTkButton(self.new_task_window, text="Create Task", 
                                            command=lambda: self.create_task(task_type))
        create_task_button.pack(pady=10)

        # Bind the Enter key to the create_task function
        self.new_task_window.bind('<Return>', lambda event: self.create_task(task_type))
            
    def create_task(self, task_type, event=None):
        task_name = self.task_name_entry.get()
        task_date = str(self.selected_date)

        if task_type == 'Scheduled':
            hour = self.time_vars['hour_var'].get()
            minute = self.time_vars['minute_var'].get()
            am_pm = self.time_vars['am_pm_var'].get()
            
            # Ensure hour, minute, and AM/PM are selected
            if not hour or not minute or not am_pm:
                messagebox.showerror("Error", "Please select hour, minute, and AM/PM.")
                return

            # Ensure hour is in 1-12 range and minute is in 0-59 range
            if not (1 <= int(hour) <= 12) or not (0 <= int(minute) <= 59):
                messagebox.showerror("Error", "Please select a valid hour (1-12) and minute (0-59).")
                return

            task_time = f"{hour}:{minute} {am_pm}"
            print(f"Task Time before conversion: '{task_time}'")  # Debug print
            try:
                # Convert 12-hour time to 24-hour format for internal storage
                task_time_24hr = datetime.strptime(task_time, '%I:%M %p').strftime('%H:%M')
                test_parse = datetime.strptime(task_time_24hr, '%H:%M')
                print(f"Test parsing 24-hour format: '{test_parse}'")  # Debug print
            except ValueError as e:
                print(f"Error in parsing 24-hour time: {e}")  # Debug print
                return

            if not self.validate_task_input(task_name, task_time_24hr, task_date):
                return

            if task_date not in self.tasks:
                self.tasks[task_date] = {'schedule': [], 'todo': []}
            
            for existing_task in self.tasks[task_date]['schedule']:
                if task_time_24hr == existing_task['time']:
                    messagebox.showerror("Error", "Time slot already occupied.")
                    return

            self.tasks[task_date]['schedule'].append({"name": task_name, "time": task_time_24hr})
        
        else:  # For To-Do tasks, no time is necessary
            if not task_name:
                messagebox.showerror("Error", "Task name cannot be empty.")
                return

            if task_date not in self.tasks:
                self.tasks[task_date] = {'schedule': [], 'todo': []}

            self.tasks[task_date]['todo'].append({"name": task_name})

        self.save_tasks()
        self.new_task_window.destroy()
        self.show_day_tasks(task_date)

        

            

    def validate_task_input(self, task_name, task_time, task_date):
        if not task_name:
            messagebox.showerror("Error", "Task name cannot be empty.")
            return False

        try:
            # Check if the time is in the correct 24-hour format by trying to parse it
            datetime.strptime(task_time, '%H:%M')
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please select a valid time.")
            return False

        # Additional validation for checking time slot overlaps can go here
        # ...

        return True


    def toggle_task_completion(self, task, completed_var):
            # Update the task's 'completed' status based on the checkbox
            task['completed'] = completed_var.get()
            self.save_tasks()  # Save the updated tasks to file
            
    def remove_task(self, task):
        task_date_str = str(self.selected_date)
        if task in self.tasks[task_date_str]['todo']:
            self.tasks[task_date_str]['todo'].remove(task)
        elif task in self.tasks[task_date_str]['schedule']:
            self.tasks[task_date_str]['schedule'].remove(task)
        self.save_tasks()
        self.show_day_tasks(task_date_str)

    def save_tasks(self):
        try:
            print("Saving tasks...")  # Debug print
            print(json.dumps(self.tasks, indent=4))  # Debug print of tasks being saved
            with open('tasks.json', 'w') as file:
                json.dump(self.tasks, file, indent=4)
            print("Tasks saved successfully.")  # Debug print
        except Exception as e:
            print(f"Error saving tasks: {e}")  # Debug print

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as file:
                self.tasks = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = {}
            
root = tk.Tk()
app = ToDoApp(root)
root.mainloop()

