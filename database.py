import uuid
from datetime import datetime, timedelta

class Database:
    def __init__(self, connection):
        if connection is None:
            raise ValueError("A valid SQLite connection must be provided.")
        self.conn = connection
        self._setup()

    def _setup(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS time_slots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    start_time TEXT NOT NULL, 
                    end_time TEXT NOT NULL,
                    title TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'AVAILABLE'
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS doctor_buffer (
                    user_id TEXT PRIMARY KEY,
                    buffer_minutes INTEGER DEFAULT 0
                )
            """)

    def set_doctor_buffer(self, user_id, buffer_minutes):
        if not self._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        with self.conn:
            self.conn.execute("""
                INSERT INTO doctor_buffer (user_id, buffer_minutes)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET buffer_minutes = excluded.buffer_minutes
            """, (user_id, buffer_minutes))

    def get_doctor_buffer(self, user_id):
        if not self._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT buffer_minutes
            FROM doctor_buffer
            WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

    def add_time_slot(self, user_id, start_time, end_time, title="", description="", status=""):
        if not self._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")

        with self.conn:
            cursor = self.conn.execute("""
            SELECT buffer_minutes
            FROM doctor_buffer
            WHERE user_id = ?
        """, (user_id,))
            result = cursor.fetchone()
            buffer_minutes = result[0] if result else 0

            buffered_end_time = end_time + timedelta(minutes=buffer_minutes)

            if self.check_conflict(user_id, start_time, buffered_end_time):
                raise ValueError("Conflict detected for the time slot.")

            self.conn.execute("""
                INSERT INTO time_slots (user_id, start_time, end_time, title, description, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, start_time.isoformat(), end_time.isoformat(), title, description, status))

    def set_status(self, user_id, start_time, end_time, status):
        if status not in ['AVAILABLE', 'UNAVAILABLE', 'RESERVED', 'CANCELLED']:
            raise ValueError("El status debe ser 'AVAILABLE', 'UNAVAILABLE' o 'RESERVED'.")

        if not self._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        with self.conn:
            self.conn.execute("""
                UPDATE time_slots
                SET status = ?
                WHERE user_id = ? AND start_time = ? AND end_time = ?
            """, (status, user_id, start_time.isoformat(), end_time.isoformat()))

    def check_conflict(self, user_id, start_time, end_time):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT start_time, end_time FROM time_slots WHERE user_id = ?
        """, (user_id,))
        existing_slots = cursor.fetchall()

        for existing_start, existing_end in existing_slots:
            existing_start = datetime.fromisoformat(existing_start)
            existing_end = datetime.fromisoformat(existing_end)

            if (start_time < existing_end and end_time > existing_start):
                return True  # Hay conflicto
        return False  # No hay conflicto

    def edit_time_slot(self, user_id, start_time, end_time, new_start_time=None, new_end_time=None, title=None,
                       description=None):
        if not self._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")

        time_slot_id = self.find_time_slot(user_id, start_time, end_time)
        if time_slot_id is None:
            raise ValueError("No se encontró una reserva con los datos proporcionados.")

        if new_start_time and new_end_time:
            start_time = new_start_time
            end_time = new_end_time

        with self.conn:
            self.conn.execute("""
                UPDATE time_slots
                SET start_time = ?, end_time = ?, title = ?, description = ?
                WHERE id = ?
            """, (start_time.isoformat(), end_time.isoformat(), title or "", description or "", time_slot_id))

    @staticmethod
    def _is_valid_uuid(value):
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

    def find_time_slot(self, user_id, start_time, end_time):
        if not self._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id
            FROM time_slots
            WHERE user_id = ? AND start_time = ? AND end_time = ?
        """, (user_id, start_time.isoformat(), end_time.isoformat()))

        result = cursor.fetchone()
        if result:
            return result[0]  # Devuelve el id de la reserva encontrada
        return None
