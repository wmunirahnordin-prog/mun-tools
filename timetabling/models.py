from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Day(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


@dataclass(frozen=True)
class TimeSlot:
    day: Day
    start_hour: int
    start_minute: int = 0
    duration_minutes: int = 60

    @property
    def end_hour(self) -> int:
        total = self.start_hour * 60 + self.start_minute + self.duration_minutes
        return total // 60

    @property
    def end_minute(self) -> int:
        total = self.start_hour * 60 + self.start_minute + self.duration_minutes
        return total % 60

    @property
    def start_total_minutes(self) -> int:
        return self.start_hour * 60 + self.start_minute

    @property
    def end_total_minutes(self) -> int:
        return self.start_total_minutes + self.duration_minutes

    def overlaps(self, other: TimeSlot) -> bool:
        if self.day != other.day:
            return False
        return (
            self.start_total_minutes < other.end_total_minutes
            and other.start_total_minutes < self.end_total_minutes
        )

    def __str__(self) -> str:
        return (
            f"{self.day.value} "
            f"{self.start_hour:02d}:{self.start_minute:02d}-"
            f"{self.end_hour:02d}:{self.end_minute:02d}"
        )


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int = 0

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Lecturer:
    id: str
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class StudentGroup:
    id: str
    name: str
    size: int = 0

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Course:
    id: str
    name: str
    lecturer: Lecturer
    student_groups: tuple[StudentGroup, ...]
    sessions_per_week: int = 1
    duration_minutes: int = 60
    preferred_rooms: tuple[Room, ...] = ()

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class ScheduledSession:
    course: Course
    time_slot: TimeSlot
    room: Room

    def __str__(self) -> str:
        return f"{self.course.name} | {self.time_slot} | {self.room.name}"


@dataclass
class Timetable:
    sessions: list[ScheduledSession] = field(default_factory=list)

    def add(self, session: ScheduledSession) -> None:
        self.sessions.append(session)

    def sessions_for_lecturer(self, lecturer: Lecturer) -> list[ScheduledSession]:
        return [s for s in self.sessions if s.course.lecturer == lecturer]

    def sessions_for_group(self, group: StudentGroup) -> list[ScheduledSession]:
        return [
            s
            for s in self.sessions
            if group in s.course.student_groups
        ]

    def sessions_for_room(self, room: Room) -> list[ScheduledSession]:
        return [s for s in self.sessions if s.room == room]

    def sessions_at_slot(self, slot: TimeSlot) -> list[ScheduledSession]:
        return [s for s in self.sessions if s.time_slot.overlaps(slot)]
