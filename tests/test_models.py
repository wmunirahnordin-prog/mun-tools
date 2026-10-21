from timetabling.models import Day, TimeSlot, Room, Lecturer, StudentGroup, Course, Timetable, ScheduledSession


def _slot(day=Day.MONDAY, hour=9, minute=0, duration=60):
    return TimeSlot(day=day, start_hour=hour, start_minute=minute, duration_minutes=duration)


def test_timeslot_end():
    s = _slot(hour=9, minute=30, duration=90)
    assert s.end_hour == 11
    assert s.end_minute == 0


def test_timeslot_overlap_same_day():
    a = _slot(hour=9, duration=60)
    b = _slot(hour=9, minute=30, duration=60)
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_timeslot_no_overlap_adjacent():
    a = _slot(hour=9, duration=60)
    b = _slot(hour=10, duration=60)
    assert not a.overlaps(b)


def test_timeslot_no_overlap_different_day():
    a = _slot(day=Day.MONDAY, hour=9)
    b = _slot(day=Day.TUESDAY, hour=9)
    assert not a.overlaps(b)


def test_timetable_queries():
    lec = Lecturer("L1", "Dr. A")
    grp = StudentGroup("G1", "CS1", 50)
    room1 = Room("R1", "Hall A", 100)
    room2 = Room("R2", "Hall B", 100)
    c1 = Course("C1", "Intro", lec, (grp,))
    c2 = Course("C2", "Data", Lecturer("L2", "Dr. B"), (grp,))

    s1 = ScheduledSession(c1, _slot(hour=9), room1)
    s2 = ScheduledSession(c2, _slot(hour=10), room2)

    tt = Timetable(sessions=[s1, s2])

    assert tt.sessions_for_lecturer(lec) == [s1]
    assert len(tt.sessions_for_group(grp)) == 2
    assert tt.sessions_for_room(room1) == [s1]
