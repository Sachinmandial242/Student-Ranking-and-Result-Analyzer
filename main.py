
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import time

# File path
DATA_FILE = os.path.join(os.path.dirname(__file__), "students.json")

# Subject names
DEFAULT_SUBJECTS = [
    "Python",
    "DAA",
    "ADBMS",
    "Data Science",
    "AIP"
]

subjects = DEFAULT_SUBJECTS.copy()
students = []


# Load JSON data
def load_students():
    global subjects, students

    try:
        if not os.path.exists(DATA_FILE):
            subjects = DEFAULT_SUBJECTS.copy()
            students = []
            save_students()
            return

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Support the new JSON format
        if isinstance(data, dict):
            subjects = data.get("subjects", DEFAULT_SUBJECTS)
            students = data.get("students", [])

        # Support the older JSON list format
        elif isinstance(data, list):
            subjects = DEFAULT_SUBJECTS.copy()
            students = data

        if len(subjects) != 5:
            subjects = DEFAULT_SUBJECTS.copy()

        # Validate records
        students = [
            s for s in students
            if isinstance(s, dict)
            and "roll" in s
            and "name" in s
            and isinstance(s.get("marks"), list)
            and len(s["marks"]) == 5
        ]

    except (json.JSONDecodeError, OSError, TypeError) as error:
        messagebox.showerror(
            "File Error",
            f"Could not load students.json:\n{error}"
        )
        subjects = DEFAULT_SUBJECTS.copy()
        students = []


# Save JSON data
def save_students():
    data = {
        "subjects": subjects,
        "students": students
    }

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        messagebox.showerror(
            "Save Error",
            f"Could not save data:\n{error}"
        )


# Calculate result
def calculate_result(marks):
    total = sum(marks)
    percentage = total / 5

    if any(mark < 33 for mark in marks):
        grade = "F"
        status = "Fail"
    else:
        status = "Pass"

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "E"

    return total, percentage, grade, status


# Bubble Sort algorithm
def bubble_sort(records):
    result = records.copy()
    n = len(result)

    for i in range(n):
        swapped = False

        for j in range(0, n - i - 1):
            p1 = calculate_result(result[j]["marks"])[1]
            p2 = calculate_result(result[j + 1]["marks"])[1]

            if p1 < p2:
                result[j], result[j + 1] = result[j + 1], result[j]
                swapped = True

        if not swapped:
            break

    return result


# Refresh table
def display_records(records=None):
    for item in table.get_children():
        table.delete(item)

    if records is None:
        records = students

    ranked = bubble_sort(records)

    for rank, student in enumerate(ranked, start=1):
        total, percentage, grade, status = calculate_result(
            student["marks"]
        )

        values = (
            rank,
            student["roll"],
            student["name"],
            *student["marks"],
            total,
            f"{percentage:.2f}%",
            grade,
            status
        )

        table.insert("", "end", values=values)


# Add a student
def add_student():
    roll = roll_entry.get().strip()
    name = name_entry.get().strip()

    if not roll or not name:
        messagebox.showwarning(
            "Missing Details",
            "Please enter roll number and student name."
        )
        return

    if any(s["roll"] == roll for s in students):
        messagebox.showerror(
            "Duplicate Roll Number",
            "This roll number already exists."
        )
        return

    try:
        marks = []

        for entry in mark_entries:
            value = entry.get().strip()

            if not value:
                raise ValueError("Enter marks for all five subjects.")

            mark = int(value)

            if mark < 0 or mark > 100:
                raise ValueError("Marks must be between 0 and 100.")

            marks.append(mark)

    except ValueError as error:
        messagebox.showerror("Invalid Marks", str(error))
        return

    students.append({
        "roll": roll,
        "name": name,
        "marks": marks
    })

    save_students()
    display_records()
    clear_form()

    messagebox.showinfo("Success", "Student added successfully!")


# Clear input fields
def clear_form():
    roll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)

    for entry in mark_entries:
        entry.delete(0, tk.END)


# Delete selected student
def delete_student():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select a student from the table."
        )
        return

    values = table.item(selected[0], "values")
    roll = str(values[1])

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Delete student with roll number {roll}?"
    )

    if confirm:
        global students
        students = [
            s for s in students
            if str(s["roll"]) != roll
        ]

        save_students()
        display_records()
        messagebox.showinfo("Deleted", "Student deleted successfully.")


# Linear Search algorithm
def search_student():
    roll = search_entry.get().strip()

    if not roll:
        messagebox.showwarning(
            "Search",
            "Please enter a roll number."
        )
        return

    start = time.perf_counter()
    found = None

    for student in students:
        if str(student["roll"]) == roll:
            found = student
            break

    elapsed = time.perf_counter() - start

    if found:
        total, percentage, grade, status = calculate_result(
            found["marks"]
        )

        messagebox.showinfo(
            "Student Found",
            f"Roll Number: {found['roll']}\n"
            f"Name: {found['name']}\n\n"
            + "\n".join(
                f"{subject}: {mark}/100"
                for subject, mark in zip(subjects, found["marks"])
            )
            + f"\n\nTotal: {total}/500"
            + f"\nPercentage: {percentage:.2f}%"
            + f"\nGrade: {grade}"
            + f"\nStatus: {status}"
            + f"\nSearch Time: {elapsed:.8f} seconds"
        )
    else:
        messagebox.showinfo(
            "Not Found",
            f"No student found with roll number {roll}."
        )


# Show ranking
def show_rankings():
    ranked = bubble_sort(students)

    if not ranked:
        messagebox.showinfo("Ranking", "No student records available.")
        return

    lines = []

    for rank, student in enumerate(ranked, start=1):
        total, percentage, grade, status = calculate_result(
            student["marks"]
        )

        lines.append(
            f"{rank}. {student['name']} "
            f"({student['roll']}) - "
            f"{percentage:.2f}% - {grade} - {status}"
        )

    messagebox.showinfo("Student Rankings", "\n".join(lines))


# Analyze algorithms
def analyze_algorithms():
    start = time.perf_counter()
    bubble_sort(students)
    sort_time = time.perf_counter() - start

    start = time.perf_counter()

    for student in students:
        if str(student["roll"]) == "105":
            break

    search_time = time.perf_counter() - start

    messagebox.showinfo(
        "Algorithm Analysis",
        f"Bubble Sort Time: {sort_time:.8f} seconds\n"
        f"Bubble Sort Worst-Case Complexity: O(n²)\n\n"
        f"Linear Search Time: {search_time:.8f} seconds\n"
        f"Linear Search Worst-Case Complexity: O(n)"
    )


# Load data before creating the table
load_students()


# Main GUI window
root = tk.Tk()
root.title("Student Ranking and Result Analyzer")
root.geometry("1250x650")
root.minsize(950, 500)

title_label = tk.Label(
    root,
    text="Student Ranking and Result Analyzer",
    font=("Arial", 18, "bold")
)
title_label.pack(pady=10)


# Student input form
form = tk.LabelFrame(root, text="Student Details", padx=8, pady=8)
form.pack(fill="x", padx=10, pady=5)

tk.Label(form, text="Roll Number").grid(row=0, column=0, padx=5, pady=5)
roll_entry = tk.Entry(form, width=12)
roll_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(form, text="Student Name").grid(row=0, column=2, padx=5, pady=5)
name_entry = tk.Entry(form, width=18)
name_entry.grid(row=0, column=3, padx=5, pady=5)

mark_entries = []

for index, subject in enumerate(subjects):
    tk.Label(form, text=f"{subject} Marks").grid(
        row=1, column=index * 2, padx=4, pady=5
    )

    entry = tk.Entry(form, width=8)
    entry.grid(row=1, column=index * 2 + 1, padx=4, pady=5)
    mark_entries.append(entry)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

tk.Button(
    button_frame,
    text="Add Student",
    command=add_student,
    width=14
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="Delete Selected",
    command=delete_student,
    width=14
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="Show Rankings",
    command=show_rankings,
    width=14
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="Algorithm Analysis",
    command=analyze_algorithms,
    width=16
).pack(side="left", padx=5)

tk.Button(
    button_frame,
    text="Show All Students",
    command=display_records,
    width=14
).pack(side="left", padx=5)


# Search section
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

tk.Label(search_frame, text="Search by Roll Number:").pack(side="left", padx=5)

search_entry = tk.Entry(search_frame, width=15)
search_entry.pack(side="left", padx=5)

tk.Button(
    search_frame,
    text="Search",
    command=search_student
).pack(side="left", padx=5)


# Table with subject-wise marks
columns = (
    "Rank",
    "Roll No",
    "Name",
    "Python",
    "DAA",
    "ADBMS",
    "Data Science",
    "AIP",
    "Total",
    "Percentage",
    "Grade",
    "Status"
)

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=10)

table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for column in columns:
    table.heading(column, text=column)
    table.column(column, width=90, anchor="center")

table.column("Name", width=140)
table.column("Data Science", width=115)
table.column("Percentage", width=100)

vertical_scroll = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)
table.configure(yscrollcommand=vertical_scroll.set)

horizontal_scroll = ttk.Scrollbar(
    table_frame,
    orient="horizontal",
    command=table.xview
)
table.configure(xscrollcommand=horizontal_scroll.set)

table.grid(row=0, column=0, sticky="nsew")
vertical_scroll.grid(row=0, column=1, sticky="ns")
horizontal_scroll.grid(row=1, column=0, sticky="ew")

table_frame.rowconfigure(0, weight=1)
table_frame.columnconfigure(0, weight=1)


# Display JSON records when app starts
display_records()

root.mainloop()
