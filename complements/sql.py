"""
Created on 2024
@Creator: Juan Bautista Gonzalez
@Position: Student electronic engineering and programmer part-time
@Contact:
    - Email: contacto@juangonzalez.com.ar
"""

import sqlite3

# Variable global
# Global variable
NAME = 'ups_data.db'

# Inicializar la base de datos
# Initialize the database


def init_db():
    # Conectar a la base de datos (o crearla si no existe)
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('ups_data.db')
    cursor = conn.cursor()

    # Crear la tabla para almacenar los datos
    # Create the table to store the data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ups_status (
            timestamp DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, '-3 hours')),
            battery_charge FLOAT,
            battery_voltage FLOAT,
            input_voltage FLOAT,
            output_voltage FLOAT,
            ups_load FLOAT,
            ups_status TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Guardar el estado de la UPS en la base de datos
# Save the UPS status in the database


def save_status(data):
    # Conectar a la base de datos
    # Connect to the database
    conn = sqlite3.connect(NAME)
    cursor = conn.cursor()

    # Insertar los datos en la tabla
    # Insert the data into the table
    cursor.execute('''
        INSERT INTO ups_status (battery_charge, battery_voltage, input_voltage, output_voltage, ups_load, ups_status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['battery_charge'], data['battery_voltage'], data['input_voltage'], data['output_voltage'], data['ups_load'], data['ups_status']))

    conn.commit()
    conn.close()


def last_24():
    conn = sqlite3.connect(NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, output_voltage, battery_charge, ups_load
        FROM ups_status WHERE timestamp >= datetime('now', '-1 day')
    ''')
    data = cursor.fetchall()
    conn.close()
    return data


def last():
    conn = sqlite3.connect(NAME)
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM ups_status ORDER BY timestamp DESC LIMIT 1''')
    row = cursor.fetchone()
    conn.close()
    data = {
        "timestamp": row[0],
        "battery_charge": row[1],
        "battery_voltage": row[2],
        "input_voltage": row[3],
        "output_voltage": row[4],
        "ups_load": row[5],
        "ups_status": row[6]
    }
    return data


# Testing the database initialization and data saving
if __name__ == '__main__':
    init_db()
    print('Database initialized!')
    save_status({
        'battery_charge': 100.0,
        'battery_voltage': 13.5,
        'input_voltage': 220.0,
        'output_voltage': 220.0,
        'ups_load': 50.0,
        'ups_status': 'ONLINE'
    })
