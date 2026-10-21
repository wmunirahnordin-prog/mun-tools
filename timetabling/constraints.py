from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from timetabling.models import ScheduledSession, Timetable


class ClashType(Enum):
    ROOM = auto()
    LECTURER = auto()
    STUDENT_GROUP = auto()


@dataclass(frozen=True)
class Clash:
    clash_type: ClashType
    session_a: ScheduledSession
    session_b: ScheduledSession
    detail: str

    def __str__(self) -> str:
        return (
            f"[{self.clash_type.name}] {self.detail}\n"
            f"  -> {self.session_a}\n"
            f"  -> {self.session_b}"
        )


def find_clashes(timetable: Timetable) -> list[Clash]:
    clashes: list[Clash] = []
    sessions = timetable.sessions

    for i, a in enumerate(sessions):
        for b in sessions[i + 1 :]:
            if not a.time_slot.overlaps(b.time_slot):
                continue

            if a.room == b.room:
                clashes.append(
                    Clash(
                        ClashType.ROOM,
                        a,
                        b,
                        f"Room '{a.room.name}' double-booked",
                    )
                )

            if a.course.lecturer == b.course.lecturer:
                clashes.append(
                    Clash(
                        ClashType.LECTURER,
                        a,
                        b,
                        f"Lecturer '{a.course.lecturer.name}' double-booked",
                    )
                )

            common_groups = set(a.course.student_groups) & set(
                b.course.student_groups
            )
            for group in common_groups:
                clashes.append(
                    Clash(
                        ClashType.STUDENT_GROUP,
                        a,
                        b,
                        f"Student group '{group.name}' double-booked",
                    )
                )

    return clashes


def would_clash(
    session: ScheduledSession, timetable: Timetable
) -> list[Clash]:
    temp = Timetable(sessions=timetable.sessions + [session])
    return [
        c
        for c in find_clashes(temp)
        if c.session_a == session or c.session_b == session
    ]


def check_room_capacity(session: ScheduledSession) -> str | None:
    if session.room.capacity == 0:
        return None
    total = sum(g.size for g in session.course.student_groups)
    if total > session.room.capacity:
        return (
            f"Room '{session.room.name}' (capacity {session.room.capacity}) "
            f"too small for '{session.course.name}' ({total} students)"
        )
    return None
