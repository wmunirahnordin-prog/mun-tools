from __future__ import annotations

from dataclasses import dataclass, field

from timetabling.models import (
    Course,
    Room,
    ScheduledSession,
    TimeSlot,
    Timetable,
)
from timetabling.constraints import would_clash, check_room_capacity


@dataclass
class ScheduleRequest:
    courses: list[Course]
    rooms: list[Room]
    available_slots: list[TimeSlot]


@dataclass
class ScheduleResult:
    timetable: Timetable
    unscheduled: list[Course] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.unscheduled) == 0


def _candidate_rooms(course: Course, rooms: list[Room]) -> list[Room]:
    if course.preferred_rooms:
        preferred = [r for r in course.preferred_rooms if r in rooms]
        others = [r for r in rooms if r not in preferred]
        return preferred + others
    return list(rooms)


def schedule(request: ScheduleRequest) -> ScheduleResult:
    timetable = Timetable()
    unscheduled: list[Course] = []
    warnings: list[str] = []

    sorted_courses = sorted(
        request.courses,
        key=lambda c: (
            -len(c.student_groups),
            -c.sessions_per_week,
            len(c.preferred_rooms),
        ),
    )

    for course in sorted_courses:
        sessions_placed = 0

        for _ in range(course.sessions_per_week):
            placed = False
            candidate_rooms = _candidate_rooms(course, request.rooms)

            for slot in request.available_slots:
                if slot.duration_minutes != course.duration_minutes:
                    continue

                for room in candidate_rooms:
                    candidate = ScheduledSession(
                        course=course, time_slot=slot, room=room
                    )

                    if would_clash(candidate, timetable):
                        continue

                    cap_warning = check_room_capacity(candidate)
                    if cap_warning:
                        warnings.append(cap_warning)

                    timetable.add(candidate)
                    placed = True
                    sessions_placed += 1
                    break

                if placed:
                    break

            if not placed and sessions_placed < course.sessions_per_week:
                unscheduled.append(course)

    return ScheduleResult(
        timetable=timetable,
        unscheduled=unscheduled,
        warnings=warnings,
    )
