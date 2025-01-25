from database import Database

class BookingCalendar:
    def __init__(self, db_connection):
        self.db = Database(db_connection)

        def add_time_slot(self, user_id, start_time, end_time, title="", description="", status=""):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        if self.check_conflict(user_id, start_time, end_time):
            raise ValueError("El time slot entra en conflicto con una reserva existente.")
        self.db.add_time_slot(user_id, start_time, end_time, title, description, status)

    def set_doctor_buffer(self, user_id, buffer_minutes):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        self.db.set_doctor_buffer(user_id, buffer_minutes)

    def get_doctor_buffer(self, user_id):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        return self.db.get_doctor_buffer(user_id)

    def check_conflict(self, user_id, start_time, end_time):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        return self.db.check_conflict(user_id, start_time, end_time)

    def cancel_reservation(self, user_id, start_time, end_time):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        # Buscar la reserva y cambiar su estado a 'CANCELLED'
        self.db.set_status(user_id, start_time, end_time, "CANCELLED")

    def edit_reservation(self, user_id, start_time, end_time, new_start_time=None, new_end_time=None, title=None,
                         description=None):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")

        # Edita la reserva
        self.db.edit_time_slot(user_id, start_time, end_time, new_start_time, new_end_time, title, description)
        print("Reserva editada exitosamente.")

    def add_unavailable_slot(self, user_id, start_time, end_time):
        if not self.db._is_valid_uuid(user_id):
            raise ValueError("El user_id debe ser un UUID válido.")
        self.db.add_time_slot(user_id, start_time, end_time, status="UNAVAILABLE")
