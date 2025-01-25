import pytest
from datetime import datetime, timedelta
import sqlite3
from calendar_1 import BookingCalendar

@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    return conn

@pytest.fixture
def calendar(db_connection):
    calendar = BookingCalendar(db_connection)
    calendar.db.conn.execute("DELETE FROM time_slots")
    calendar.db.conn.execute("DELETE FROM doctor_buffer")
    return calendar

def test_add_time_slot(calendar):
    start_time = datetime(2025, 1, 25, 10, 0)
    end_time = datetime(2025, 1, 25, 10, 30)

    calendar.add_time_slot("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time, 'RESERVED')

    cursor = calendar.db.conn.cursor()
    cursor.execute("SELECT * FROM time_slots WHERE user_id = ?", ("5a78af51-8f88-4b8b-8b21-27334997d2b2",))
    result = cursor.fetchone()

    assert result is not None
    assert result[1] == "5a78af51-8f88-4b8b-8b21-27334997d2b2"
    assert result[2] == start_time.isoformat()
    assert result[3] == end_time.isoformat()
    assert result[4] == "RESERVED"

def test_add_time_slot_with_conflict(calendar):
    start_time = datetime(2025, 1, 25, 10, 0)
    end_time = datetime(2025, 1, 25, 10, 40)

    calendar.add_time_slot("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time)

    with pytest.raises(ValueError, match="El time slot entra en conflicto con una reserva existente."):
        calendar.add_time_slot("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time + timedelta(minutes=15))

def test_set_doctor_buffer(calendar):
    calendar.set_doctor_buffer("5a78af51-8f88-4b8b-8b21-27334997d2b2", 15)

    buffer = calendar.get_doctor_buffer("5a78af51-8f88-4b8b-8b21-27334997d2b2")
    assert buffer == 15

def test_check_conflict(calendar):
    start_time = datetime(2025, 1, 25, 10, 0)
    end_time = datetime(2025, 1, 25, 10, 30)

    calendar.add_time_slot("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time)

    conflict = calendar.check_conflict("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time + timedelta(minutes=30),
                                       end_time + timedelta(minutes=60))
    assert not conflict

    conflict = calendar.check_conflict("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time,
                                       end_time + timedelta(minutes=10))
    assert conflict

def test_cancel_reservation(calendar):
    start_time = datetime(2025, 1, 25, 10, 0)
    end_time = datetime(2025, 1, 25, 10, 30)

    calendar.add_time_slot("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time)

    calendar.cancel_reservation("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time)

    cursor = calendar.db.conn.cursor()
    cursor.execute("SELECT status FROM time_slots WHERE user_id = ? AND start_time = ?",
                   ("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time.isoformat()))
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == "CANCELLED"

def test_edit_reservation(calendar):
    start_time = datetime(2025, 1, 25, 10, 0)
    end_time = datetime(2025, 1, 25, 10, 30)
    new_start_time = datetime(2025, 1, 25, 11, 0)
    new_end_time = datetime(2025, 1, 25, 11, 30)

    calendar.add_time_slot("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time)

    calendar.edit_reservation("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time, end_time, new_start_time, new_end_time)

    cursor = calendar.db.conn.cursor()
    cursor.execute("SELECT start_time, end_time FROM time_slots WHERE user_id = ? AND start_time = ?",
                   ("5a78af51-8f88-4b8b-8b21-27334997d2b2", new_start_time.isoformat()))
    result = cursor.fetchone()

    assert result is not None
    assert result[0] == new_start_time.isoformat()
    assert result[1] == new_end_time.isoformat()

    cursor.execute("SELECT start_time, end_time FROM time_slots WHERE user_id = ? AND start_time = ?",
                   ("5a78af51-8f88-4b8b-8b21-27334997d2b2", start_time.isoformat()))
    result = cursor.fetchone()

    assert result is None
