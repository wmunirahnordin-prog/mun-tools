from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from timetabling.models import (
    Course,
    Day,
    Lecturer,
    Room,
    StudentGroup,
    TimeSlot,
)
from timetabling.scheduler import ScheduleRequest, schedule
from timetabling.constraints import find_clashes


def _load_data(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


DAY_MAP = {d.value.lower(): d for d in Day}


def _parse_input(data: dict) -> ScheduleRequest:
    rooms = {
        r["id"]: Room(id=r["id"], name=r["name"], capacity=r.get("capacity", 0))
        for r in data["rooms"]
    }

    lecturers = {
        l["id"]: Lecturer(id=l["id"], name=l["name"])
        for l in data["lecturers"]
    }

    groups = {
        g["id"]: StudentGroup(id=g["id"], name=g["name"], size=g.get("size", 0))
        for g in data["student_groups"]
    }

    courses = []
    for c in data["courses"]:
        preferred = tuple(rooms[rid] for rid in c.get("preferred_rooms", []))
        courses.append(
            Course(
                id=c["id"],
                name=c["name"],
                lecturer=lecturers[c["lecturer"]],
                student_groups=tuple(groups[gid] for gid in c["student_groups"]),
                sessions_per_week=c.get("sessions_per_week", 1),
                duration_minutes=c.get("duration_minutes", 60),
                preferred_rooms=preferred,
            )
        )

    slots = []
    for s in data["available_slots"]:
        day = DAY_MAP[s["day"].lower()]
        slots.append(
            TimeSlot(
                day=day,
                start_hour=s["start_hour"],
                start_minute=s.get("start_minute", 0),
                duration_minutes=s.get("duration_minutes", 60),
            )
        )

    return ScheduleRequest(courses=courses, rooms=list(rooms.values()), available_slots=slots)


def _format_timetable(result) -> str:
    lines = []
    if result.success:
        lines.append("Schedule generated successfully!\n")
    else:
        lines.append("Partial schedule generated (some courses could not be placed).\n")

    lines.append(f"{'Course':<25} {'Day':<12} {'Time':<14} {'Room':<15}")
    lines.append("-" * 66)

    sorted_sessions = sorted(
        result.timetable.sessions,
        key=lambda s: (
            list(Day).index(s.time_slot.day),
            s.time_slot.start_total_minutes,
        ),
    )

    for s in sorted_sessions:
        time_str = (
            f"{s.time_slot.start_hour:02d}:{s.time_slot.start_minute:02d}-"
            f"{s.time_slot.end_hour:02d}:{s.time_slot.end_minute:02d}"
        )
        lines.append(
            f"{s.course.name:<25} {s.time_slot.day.value:<12} {time_str:<14} {s.room.name:<15}"
        )

    if result.unscheduled:
        lines.append(f"\nUnscheduled courses ({len(result.unscheduled)}):")
        for c in result.unscheduled:
            lines.append(f"  - {c.name}")

    if result.warnings:
        lines.append(f"\nWarnings ({len(result.warnings)}):")
        for w in result.warnings:
            lines.append(f"  - {w}")

    clashes = find_clashes(result.timetable)
    if clashes:
        lines.append(f"\nClashes detected ({len(clashes)}):")
        for clash in clashes:
            lines.append(f"  {clash}")
    else:
        lines.append("\nNo clashes detected.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="timetable",
        description="Generate a clash-free timetable from a JSON input file.",
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the JSON file describing courses, rooms, lecturers, groups and available slots.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write the resulting timetable as JSON to this file.",
    )

    args = parser.parse_args(argv)
    data = _load_data(args.input_file)
    request = _parse_input(data)
    result = schedule(request)

    print(_format_timetable(result))

    if args.output:
        output = {
            "scheduled": [
                {
                    "course": s.course.id,
                    "course_name": s.course.name,
                    "day": s.time_slot.day.value,
                    "start_hour": s.time_slot.start_hour,
                    "start_minute": s.time_slot.start_minute,
                    "duration_minutes": s.time_slot.duration_minutes,
                    "room": s.room.id,
                    "room_name": s.room.name,
                    "lecturer": s.course.lecturer.name,
                }
                for s in result.timetable.sessions
            ],
            "unscheduled": [c.id for c in result.unscheduled],
            "clash_free": len(find_clashes(result.timetable)) == 0,
        }
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nJSON output written to {args.output}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
