from timetabling.models import (
    Course, Day, Lecturer, Room, StudentGroup, TimeSlot,
)
from timetabling.scheduler import ScheduleRequest, schedule
from timetabling.constraints import find_clashes


L1 = Lecturer("L1", "Dr. A")
L2 = Lecturer("L2", "Dr. B")
L3 = Lecturer("L3", "Dr. C")
G1 = StudentGroup("G1", "CS1", 50)
G2 = StudentGroup("G2", "CS2", 40)
R1 = Room("R1", "Hall A", 100)
R2 = Room("R2", "Hall B", 80)


def _slots(days=None, hours=None, duration=60):
    days = days or [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY]
    hours = hours or [8, 9, 10, 11, 14, 15, 16]
    return [
        TimeSlot(day=d, start_hour=h, duration_minutes=duration) for d in days for h in hours
    ]


def test_basic_schedule():
    courses = [
        Course("C1", "Intro", L1, (G1,), sessions_per_week=1),
        Course("C2", "Data", L2, (G2,), sessions_per_week=1),
    ]
    req = ScheduleRequest(courses=courses, rooms=[R1, R2], available_slots=_slots())
    result = schedule(req)

    assert result.success
    assert len(result.timetable.sessions) == 2
    assert find_clashes(result.timetable) == []


def test_avoids_lecturer_clash():
    courses = [
        Course("C1", "Intro", L1, (G1,), sessions_per_week=2),
        Course("C2", "Advanced", L1, (G2,), sessions_per_week=2),
    ]
    req = ScheduleRequest(courses=courses, rooms=[R1, R2], available_slots=_slots())
    result = schedule(req)

    assert result.success
    assert find_clashes(result.timetable) == []


def test_avoids_student_group_clash():
    courses = [
        Course("C1", "Intro", L1, (G1,), sessions_per_week=2),
        Course("C2", "Lab", L2, (G1,), sessions_per_week=2),
    ]
    req = ScheduleRequest(courses=courses, rooms=[R1, R2], available_slots=_slots())
    result = schedule(req)

    assert result.success
    assert find_clashes(result.timetable) == []


def test_avoids_room_clash():
    courses = [
        Course("C1", "Intro", L1, (G1,), sessions_per_week=3),
        Course("C2", "Data", L2, (G2,), sessions_per_week=3),
    ]
    req = ScheduleRequest(
        courses=courses,
        rooms=[R1],
        available_slots=_slots(),
    )
    result = schedule(req)

    assert result.success
    assert find_clashes(result.timetable) == []


def test_reports_unscheduled():
    courses = [
        Course("C1", "A", L1, (G1,), sessions_per_week=1),
        Course("C2", "B", L1, (G1,), sessions_per_week=1),
    ]
    req = ScheduleRequest(
        courses=courses,
        rooms=[R1],
        available_slots=[TimeSlot(Day.MONDAY, 9)],
    )
    result = schedule(req)

    assert not result.success
    assert len(result.unscheduled) == 1


def test_preferred_rooms():
    courses = [
        Course("C1", "Lab", L1, (G1,), preferred_rooms=(R2,)),
    ]
    req = ScheduleRequest(courses=courses, rooms=[R1, R2], available_slots=_slots())
    result = schedule(req)

    assert result.success
    assert result.timetable.sessions[0].room == R2


def test_full_example():
    """Schedule a larger set of courses and verify clash-free."""
    courses = [
        Course("C1", "Intro", L1, (G1,), sessions_per_week=2),
        Course("C2", "Data", L1, (G2,), sessions_per_week=2),
        Course("C3", "Networks", L2, (G1, G2), sessions_per_week=1),
        Course("C4", "OS", L3, (G2,), sessions_per_week=2),
        Course("C5", "Web", L2, (G1,), sessions_per_week=1),
    ]
    req = ScheduleRequest(courses=courses, rooms=[R1, R2], available_slots=_slots())
    result = schedule(req)

    assert result.success
    assert find_clashes(result.timetable) == []
    assert len(result.timetable.sessions) == 8
