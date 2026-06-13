#!/usr/bin/env python3
"""Student record manager with fixed test scores and grade calculation."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DATA_FILE = "students.txt"
GRADE_SCALE = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


@dataclass
class Student:
    student_id: str
    name: str
    test_scores: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    average: float = 0.0
    grade: str = "F"

    def __post_init__(self) -> None:
        self.update_metrics()

    def update_metrics(self) -> None:
        self.average = sum(self.test_scores) / len(self.test_scores)
        self.grade = self.calculate_letter_grade()

    def calculate_letter_grade(self) -> str:
        for threshold, letter in GRADE_SCALE:
            if self.average >= threshold:
                return letter
        return "F"

    def set_scores(self, scores: List[float]) -> None:
        self.test_scores = scores
        self.update_metrics()

    def to_line(self) -> str:
        return (
            f"{self.name}|{self.student_id}|{self.test_scores[0]:.2f}|"
            f"{self.test_scores[1]:.2f}|{self.test_scores[2]:.2f}|{self.average:.2f}|{self.grade}"
        )

    @classmethod
    def from_line(cls, line: str) -> "Student":
        values = [value.strip() for value in line.split("|")]
        if len(values) < 7:
            raise ValueError("Invalid record line")
        name, student_id = values[0], values[1]
        scores = [float(values[i]) for i in range(2, 5)]
        return cls(student_id=student_id, name=name, test_scores=scores)


class StudentManager:
    def __init__(self) -> None:
        self.students: Dict[str, Student] = {}
        self.load()

    def add_student(self, student: Student) -> bool:
        if student.student_id in self.students:
            return False
        self.students[student.student_id] = student
        return True

    def remove_student(self, student_id: str) -> bool:
        return self.students.pop(student_id, None) is not None

    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)

    def list_students(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda record: record.student_id)

    def save(self) -> None:
        write_records(self.list_students())

    def load(self) -> None:
        self.students = read_records()


def read_records() -> Dict[str, Student]:
    records: Dict[str, Student] = {}
    if not os.path.exists(DATA_FILE):
        return records
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            for line in file:
                text = line.strip()
                if not text:
                    continue
                try:
                    student = Student.from_line(text)
                    records[student.student_id] = student
                except ValueError:
                    print(f"Skipping invalid record: {text}")
    except IOError:
        print(f"Error: Unable to read from {DATA_FILE}. Records cannot be loaded right now.")
    return records


def write_records(students: List[Student]) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            for student in students:
                file.write(student.to_line() + "\n")
    except IOError:
        print(f"Error: Unable to save records to {DATA_FILE}. Please check file permissions and try again.")


def prompt_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Invalid input. Please enter a non-empty value.")


def prompt_score(score_label: str) -> float:
    while True:
        raw = input(f"Enter {score_label} score (0-100): ").strip()
        try:
            score = float(raw)
            if 0 <= score <= 100:
                return score
            print("Score must be a number between 0 and 100.")
        except ValueError:
            print("Invalid score. Please enter a numeric value.")


def prompt_three_scores() -> List[float]:
    return [
        prompt_score("Test 1"),
        prompt_score("Test 2"),
        prompt_score("Test 3"),
    ]


def prompt_yes_no(prompt_text: str) -> bool:
    while True:
        choice = input(prompt_text).strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Please answer 'y' or 'n'.")


def display_student(student: Student) -> None:
    print("\nStudent Record")
    print(f"ID: {student.student_id}")
    print(f"Name: {student.name}")
    print(f"Test 1: {student.test_scores[0]:.2f}")
    print(f"Test 2: {student.test_scores[1]:.2f}")
    print(f"Test 3: {student.test_scores[2]:.2f}")
    print(f"Average: {student.average:.2f}")
    print(f"Grade: {student.grade}")


def show_summary(manager: StudentManager) -> None:
    if not manager.students:
        print("No student records available. Add a student using option 1.")
        return
    print("\nStudent Records Summary")
    print("ID   | Name                 | T1   | T2   | T3   | Avg   | Grade")
    print("-----+----------------------+------+------+------+------+-------")
    for student in manager.list_students():
        print(
            f"{student.student_id:>4} | {student.name:<20} | {student.test_scores[0]:6.2f} | {student.test_scores[1]:6.2f} | {student.test_scores[2]:6.2f} | {student.average:6.2f} | {student.grade:>5}"
        )


def add_student_flow(manager: StudentManager) -> None:
    while True:
        student_id = prompt_non_empty("Student ID: ")
        name = prompt_non_empty("Student name: ")
        scores = prompt_three_scores()
        student = Student(student_id=student_id, name=name, test_scores=scores)
        if manager.add_student(student):
            manager.save()
            print(f"Student added successfully: {name} ({student_id}).")
        else:
            print(f"A student with ID {student_id} already exists. Please use a different ID.")

        if not prompt_yes_no("Add another student? (y/n): "):
            break


def update_scores_flow(manager: StudentManager) -> None:
    student_id = prompt_non_empty("Student ID to update scores: ")
    student = manager.get_student(student_id)
    if not student:
        print(f"Student ID {student_id} not found.")
        return
    scores = prompt_three_scores()
    student.set_scores(scores)
    manager.save()
    print(f"Updated scores for {student.name}.")


def view_student_flow(manager: StudentManager) -> None:
    student_id = prompt_non_empty("Student ID to view: ")
    student = manager.get_student(student_id)
    if not student:
        print(f"Student ID {student_id} not found.")
        return
    display_student(student)


def remove_student_flow(manager: StudentManager) -> None:
    student_id = prompt_non_empty("Student ID to remove: ")
    if manager.remove_student(student_id):
        manager.save()
        print(f"Student {student_id} was removed successfully.")
    else:
        print(f"No student found with ID {student_id}. Nothing was removed.")


def menu() -> None:
    manager = StudentManager()
    options = {
        "1": ("Add a new student", add_student_flow),
        "2": ("Update student scores", update_scores_flow),
        "3": ("View a student record", view_student_flow),
        "4": ("List all students", lambda m: show_summary(m)),
        "5": ("Remove a student", remove_student_flow),
        "6": ("Quit", None),
    }
    while True:
        print("\nStudent Record Manager")
        for key, (description, _) in options.items():
            print(f"{key}. {description}")
        choice = input("Choose an option: ").strip()
        if choice == "6":
            print(f"Goodbye! Records saved to {DATA_FILE}.")
            break
        action = options.get(choice)
        if not action:
            print("Invalid option. Please choose a number from 1 to 6.")
            continue
        _, handler = action
        if handler:
            handler(manager)


if __name__ == "__main__":
    menu()
