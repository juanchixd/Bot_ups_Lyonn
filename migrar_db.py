"""
Created on 2026
@Creator: Juan Bautista Gonzalez
@Position: Student electronic engineering and programmer part-time
@Contact:
    - Email: contacto@juangonzalez.com.ar
"""
import sqlite3
from datetime import datetime
from complements.sql import init_db, SessionLocal, UPSStatus

def migrar():
    print("Iniciando migración de SQLite a PostgreSQL con SQLAlchemy...")
    
    init_db()
    
    sqlite_conn = sqlite3.connect('ups_data.db')
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT timestamp, battery_charge, battery_voltage, input_voltage, output_voltage, ups_load, ups_status FROM ups_status")
    filas = sqlite_cursor.fetchall()
    
    db = SessionLocal()
    try:
        for fila in filas:
            # Casteo del string de fecha de SQLite a un objeto datetime de Python
            try:
                dt = datetime.strptime(fila[0], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Fallback por si la base original guardó microsegundos
                dt = datetime.fromisoformat(fila[0])

            nuevo_estado = UPSStatus(
                timestamp=dt,
                battery_charge=fila[1],
                battery_voltage=fila[2],
                input_voltage=fila[3],
                output_voltage=fila[4],
                ups_load=fila[5],
                ups_status=fila[6]
            )
            db.add(nuevo_estado)
        
        # Comiteamos todo el bloque junto (más rápido)
        db.commit()
        print(f"Migración completa! Se copiaron {len(filas)} registros a Postres.")
    except Exception as e:
        db.rollback()
        print(f"Error durante la migración: {e}")
    finally:
        db.close()
        sqlite_conn.close()

if __name__ == "__main__":
    migrar()