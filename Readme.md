# Booking Calendar Library

This library allows you to manage a booking calendar for doctors, with support for buffers (extra time between appointments), conflict management, and adding time slots. It is designed to work with an SQLite database.
## Requirements

- Python 3.x
- SQLite 
- Necessary libraries:
    - `datetime`
    - `uuid`

## Installation

1. Clone or download the repository.
2. Make sure that Python 3.x is installed.
3. No external libraries need to be installed.

## Library structure

The library consists of two main classes:
- **Database**: Responsible for database interaction, creating and maintaining tables, and managing time slots in the database.
- **BookingCalendar**: Provides a high-level interface for managing bookings, configuring buffers, and checking conflicts.

## Usage

### Connection to the database
First, it's necessary to establish an SQLite connection for using the library.

```python
import sqlite3
from datetime import datetime

#  Connect to an SQLite database (the database will be created if it doesn't exist)
connection = sqlite3.connect('calendar.sqlite')

# Create an instance of BookingCalendar
from calendar_1 import BookingCalendar
calendar = BookingCalendar(connection)
```

## Configuring buffer time for a doctor

Each doctor can have a buffer (extra time) between appointments, which can be configured in minutes. 
```python
user_id = '18294d49-553b-4d72-a16b-8e62609b03cf'  # The doctor's ID, which must be a valid UUID
buffer_minutes = 15  # Buffer time in minutes
calendar.set_doctor_buffer(user_id, buffer_minutes)

```

## Getting the configured buffer for a doctor
Puedes obtener el tiempo de buffer configurado para un doctor con el siguiente método:


```python
buffer = calendar.get_doctor_buffer(user_id)
print(f"Buffer configurado para el doctor: {buffer} minutos")
```
## Adding a time slot
You can add a time slot for a doctor by specifying their ID, start time, end time, and optionally a title and description.
```python
start_time = datetime(2025, 1, 24, 9, 0) 
end_time = datetime(2025, 1, 24, 10, 0)   

calendar.add_time_slot(user_id, start_time, end_time, title="Consulta General", description="Consulta de rutina")
```

If a booking already exists that overlaps with this time slot, a "ValueError" will be raised indicating a conflict.

## Checking if conflicts exist

You can check for conflicts before adding a new appointment. The library checks if there are existing bookings with the status "RESERVED", "BLOCKED", or "CANCELLED" that overlap with the new time slot.
```python
if calendar.check_conflict(user_id, start_time, end_time):
    print("¡Conflicto encontrado! El espacio de tiempo ya está ocupado.")
else:
    calendar.add_time_slot(user_id, start_time, end_time, title="Consulta General", description="Consulta de rutina")
```

## Cambiar el estado de una reserva

Puedes cambiar el estado de una cita a "AVAILABLE", "UNAVAILABLE", "RESERVED" o "CANCELLED". Por ejemplo, para marcar una cita como no disponible:
```python
calendar.set_status(user_id, start_time, end_time, "UNAVAILABLE")
```

## Editar una reserva

Puedes editar una reserva existente modificando su hora de inicio, hora de fin, título y descripción.
```python
new_start_time = datetime(2025, 1, 24, 10, 0)  # Nuevo inicio
new_end_time = datetime(2025, 1, 24, 11, 0)    # Nuevo fin
calendar.edit_reservation(user_id, start_time, end_time, new_start_time, new_end_time, title="Consulta Revisada")
```

### UUID Validation

Some methods require a valid `user_id:`, which must be a UUID. To verify that a `user_id:` is valid, you can use the following static method:
```python
from booking_calendar import BookingCalendar

user_id = 'doctor-uuid'

if BookingCalendar._is_valid_uuid(user_id):
    print("El UUID es válido.")
else:
    print("El UUID no es válido.")
```

## Estructura de la base de datos
La base de datos SQLite contiene las siguientes tablas:

1. **time_slots:** 
- `id:` ID de la cita (autoincremental).
- `user_id:` ID del usuario (UUID).
- `start_time:` Hora de inicio de la cita.
- `end_time:` Hora de fin de la cita.
- `title:` Título de la cita.
- `description:` Descripción de la cita.
- `status:` Estado de la cita (por ejemplo, 'AVAILABLE', 'UNAVAILABLE', 'RESERVED', 'CANCELLED').
- `doctor_buffer:` Almacena el tiempo de buffer configurado para cada doctor.
- 
2. **doctor_buffer:** 
- `user_id:` ID del usuario (UUID).
- `buffer_minutes:` El tiempo de buffer en minutos.

