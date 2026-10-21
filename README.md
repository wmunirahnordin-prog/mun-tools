# mun-tools

## Timetabling Clash Avoidance System

A Python tool for generating university/school timetables that automatically avoids scheduling clashes.

### Features

- **Clash detection** across three dimensions:
  - **Room clashes** — no room is double-booked
  - **Lecturer clashes** — no lecturer teaches two classes at once
  - **Student group clashes** — no student group has overlapping classes
- **Automatic scheduling** with constraint-based placement
- **Room capacity checking** with warnings
- **Preferred room support** per course
- **Multi-session courses** (e.g. 2 lectures + 1 lab per week)
- **JSON input/output** for easy integration
- **CLI interface** for quick use

### Quick Start

1. Generate an example input file:

```bash
python -m timetabling.example_data
```

2. Run the scheduler:

```bash
python main.py example_input.json
```

3. Save the result as JSON:

```bash
python main.py example_input.json -o schedule_output.json
```

### Input Format

The input JSON file has five sections:

```json
{
  "rooms": [
    {"id": "R1", "name": "Lecture Hall A", "capacity": 120}
  ],
  "lecturers": [
    {"id": "L1", "name": "Dr. Ahmad"}
  ],
  "student_groups": [
    {"id": "G1", "name": "CS Year 1", "size": 100}
  ],
  "courses": [
    {
      "id": "C1",
      "name": "Intro to Programming",
      "lecturer": "L1",
      "student_groups": ["G1"],
      "sessions_per_week": 2,
      "duration_minutes": 60,
      "preferred_rooms": ["R1"]
    }
  ],
  "available_slots": [
    {"day": "Monday", "start_hour": 9, "start_minute": 0, "duration_minutes": 60}
  ]
}
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Using as a Library

```python
from timetabling import schedule, find_clashes
from timetabling.models import *
from timetabling.scheduler import ScheduleRequest

# Define your data
rooms = [Room("R1", "Hall A", 100)]
lecturers = [Lecturer("L1", "Dr. Ahmad")]
groups = [StudentGroup("G1", "CS Year 1", 80)]
courses = [Course("C1", "Intro", lecturers[0], (groups[0],), sessions_per_week=2)]

slots = [
    TimeSlot(Day.MONDAY, 9),
    TimeSlot(Day.MONDAY, 10),
    TimeSlot(Day.TUESDAY, 9),
]

# Schedule
result = schedule(ScheduleRequest(courses, rooms, slots))

# Check results
print(f"Scheduled: {len(result.timetable.sessions)}")
print(f"Clashes: {len(find_clashes(result.timetable))}")
```
