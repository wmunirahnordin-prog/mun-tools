"""Generate an example JSON input file for the timetabling system."""
from __future__ import annotations

import json
from pathlib import Path


EXAMPLE = {
    "rooms": [
        {"id": "R1", "name": "Lecture Hall A", "capacity": 120},
        {"id": "R2", "name": "Lecture Hall B", "capacity": 80},
        {"id": "R3", "name": "Lab 1", "capacity": 40},
        {"id": "R4", "name": "Lab 2", "capacity": 40},
        {"id": "R5", "name": "Seminar Room 1", "capacity": 30},
    ],
    "lecturers": [
        {"id": "L1", "name": "Dr. Ahmad"},
        {"id": "L2", "name": "Dr. Siti"},
        {"id": "L3", "name": "Prof. Lee"},
        {"id": "L4", "name": "Dr. Tan"},
        {"id": "L5", "name": "Dr. Rahim"},
    ],
    "student_groups": [
        {"id": "G1", "name": "CS Year 1", "size": 100},
        {"id": "G2", "name": "CS Year 2", "size": 80},
        {"id": "G3", "name": "CS Year 3", "size": 60},
        {"id": "G4", "name": "IT Year 1", "size": 70},
        {"id": "G5", "name": "IT Year 2", "size": 50},
    ],
    "courses": [
        {
            "id": "C1",
            "name": "Intro to Programming",
            "lecturer": "L1",
            "student_groups": ["G1"],
            "sessions_per_week": 2,
            "duration_minutes": 60,
            "preferred_rooms": ["R1"],
        },
        {
            "id": "C2",
            "name": "Data Structures",
            "lecturer": "L1",
            "student_groups": ["G2"],
            "sessions_per_week": 2,
            "duration_minutes": 60,
        },
        {
            "id": "C3",
            "name": "Database Systems",
            "lecturer": "L2",
            "student_groups": ["G2", "G5"],
            "sessions_per_week": 2,
            "duration_minutes": 60,
        },
        {
            "id": "C4",
            "name": "Operating Systems",
            "lecturer": "L3",
            "student_groups": ["G3"],
            "sessions_per_week": 2,
            "duration_minutes": 60,
        },
        {
            "id": "C5",
            "name": "Web Development",
            "lecturer": "L4",
            "student_groups": ["G1", "G4"],
            "sessions_per_week": 1,
            "duration_minutes": 60,
        },
        {
            "id": "C6",
            "name": "Computer Networks",
            "lecturer": "L5",
            "student_groups": ["G3"],
            "sessions_per_week": 2,
            "duration_minutes": 60,
        },
        {
            "id": "C7",
            "name": "Programming Lab",
            "lecturer": "L1",
            "student_groups": ["G1"],
            "sessions_per_week": 1,
            "duration_minutes": 120,
            "preferred_rooms": ["R3", "R4"],
        },
        {
            "id": "C8",
            "name": "IT Fundamentals",
            "lecturer": "L4",
            "student_groups": ["G4"],
            "sessions_per_week": 2,
            "duration_minutes": 60,
        },
        {
            "id": "C9",
            "name": "Software Engineering",
            "lecturer": "L2",
            "student_groups": ["G3"],
            "sessions_per_week": 1,
            "duration_minutes": 60,
        },
        {
            "id": "C10",
            "name": "Networking Lab",
            "lecturer": "L5",
            "student_groups": ["G5"],
            "sessions_per_week": 1,
            "duration_minutes": 120,
            "preferred_rooms": ["R3", "R4"],
        },
    ],
    "available_slots": [],
}


def _generate_slots() -> list[dict]:
    slots = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    hours_60 = [8, 9, 10, 11, 14, 15, 16]
    hours_120 = [8, 10, 14, 16]

    for day in days:
        for h in hours_60:
            slots.append(
                {"day": day, "start_hour": h, "start_minute": 0, "duration_minutes": 60}
            )
        for h in hours_120:
            slots.append(
                {"day": day, "start_hour": h, "start_minute": 0, "duration_minutes": 120}
            )

    return slots


def generate_example(path: Path | None = None) -> dict:
    data = dict(EXAMPLE)
    data["available_slots"] = _generate_slots()

    if path:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    return data


if __name__ == "__main__":
    generate_example(Path("example_input.json"))
    print("Written example_input.json")
