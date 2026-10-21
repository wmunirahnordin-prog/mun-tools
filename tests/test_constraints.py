from timetabling.models import (
    Course, Day, Lecturer, Room, ScheduledSession, StudentGroup, TimeSlot, Timetable,
)
from timetabling.constraints import find_clashes, would_clash, check_room_capacity, ClashType


def _slot(day=Day.MONDAY, hour=9, minute=0, duration=60):
    return TimeSlot(day=day, start_hour=hour, start_minute=minute, duration_minutes=duration)


L1 = Lecturer("L1", "Dr. A")
L2 = Lecturer("L2", "Dr. B")
G1 = StudentGroup("G1", "CS1", 50)
G2 = StudentGroup("G2", "CS2", 40)
R1 = Room("R1", "Hall A", 100)
R2 = Room("R2", "Hall B", 80)


def test_room_clash():
    c1 = Course("C1", "Intro", L1, (G1,))
    c2 = Course("C2", "Data", L2, (G2,))
    s1 = ScheduledSession(c1, _slot(hour=9), R1)
    s2 = ScheduledSession(c2, _slot(hour=9), R1)

    clashes = find_clashes(Timetable(sessions=[s1, s2]))
    assert len(clashes) == 1
    assert clashes[0].clash_type == ClashType.ROOM


def test_lecturer_clash():
    c1 = Course("C1", "Intro", L1, (G1,))
    c2 = Course("C2", "Data", L1, (G2,))
    s1 = ScheduledSession(c1, _slot(hour=9), R1)
    s2 = ScheduledSession(c2, _slot(hour=9), R2)

    clashes = find_clashes(Timetable(sessions=[s1, s2]))
    assert len(clashes) == 1
    assert clashes[0].clash_type == ClashType.LECTURER


def test_student_group_clash():
    c1 = Course("C1", "Intro", L1, (G1,))
    c2 = Course("C2", "Data", L2, (G1,))
    s1 = ScheduledSession(c1, _slot(hour=9), R1)
    s2 = ScheduledSession(c2, _slot(hour=9), R2)

    clashes = find_clashes(Timetable(sessions=[s1, s2]))
    assert len(clashes) == 1
    assert clashes[0].clash_type == ClashType.STUDENT_GROUP


def test_no_clash():
    c1 = Course("C1", "Intro", L1, (G1,))
    c2 = Course("C2", "Data", L2, (G2,))
    s1 = ScheduledSession(c1, _slot(hour=9), R1)
    s2 = ScheduledSession(c2, _slot(hour=10), R2)

    assert find_clashes(Timetable(sessions=[s1, s2])) == []


def test_would_clash():
    c1 = Course("C1", "Intro", L1, (G1,))
    c2 = Course("C2", "Data", L2, (G1,))
    s1 = ScheduledSession(c1, _slot(hour=9), R1)
    s2 = ScheduledSession(c2, _slot(hour=9), R2)

    tt = Timetable(sessions=[s1])
    assert len(would_clash(s2, tt)) == 1


def test_room_capacity_warning():
    big_group = StudentGroup("G1", "CS1", 200)
    c = Course("C1", "Intro", L1, (big_group,))
    s = ScheduledSession(c, _slot(hour=9), R1)
    warning = check_room_capacity(s)
    assert warning is not None
    assert "too small" in warning


def test_room_capacity_ok():
    c = Course("C1", "Intro", L1, (G1,))
    s = ScheduledSession(c, _slot(hour=9), R1)
    assert check_room_capacity(s) is None
