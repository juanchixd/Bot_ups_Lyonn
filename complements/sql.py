"""
Created on 2024
@Creator: Juan Bautista Gonzalez
@Position: Student electronic engineering and programmer part-time
@Contact:
    - Email: contacto@juangonzalez.com.ar
"""

import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Float, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Conexión a PostgreSQL
DATABASE_URL = os.getenv('POSTGRES_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la base de datos
class UPSStatus(Base):
    __tablename__ = 'ups_status'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, default=datetime.now)
    battery_charge = Column(Float)
    battery_voltage = Column(Float)
    input_voltage = Column(Float)
    output_voltage = Column(Float)
    ups_load = Column(Float)
    ups_status = Column(String)

def init_db():
    # Crea las tablas si no existen
    Base.metadata.create_all(bind=engine)

def save_status(data):
    db = SessionLocal()
    try:
        nuevo_estado = UPSStatus(
            battery_charge=float(data['battery_charge']),
            battery_voltage=float(data['battery_voltage']),
            input_voltage=float(data['input_voltage']),
            output_voltage=float(data['output_voltage']),
            ups_load=float(data['ups_load']),
            ups_status=data['ups_status']
        )
        db.add(nuevo_estado)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error guardando en Postgres: {e}")
    finally:
        db.close()

def last_24():
    db = SessionLocal()
    try:
        hace_24h = datetime.now() - timedelta(days=1)
        registros = db.query(UPSStatus).filter(UPSStatus.timestamp >= hace_24h).order_by(UPSStatus.timestamp.asc()).all()
        return [(str(r.timestamp), r.output_voltage, r.battery_charge, r.ups_load) for r in registros]
    finally:
        db.close()

def last():
    db = SessionLocal()
    try:
        r = db.query(UPSStatus).order_by(UPSStatus.timestamp.desc()).first()
        if r:
            return {
                "timestamp": str(r.timestamp),
                "battery_charge": r.battery_charge,
                "battery_voltage": r.battery_voltage,
                "input_voltage": r.input_voltage,
                "output_voltage": r.output_voltage,
                "ups_load": r.ups_load,
                "ups_status": r.ups_status
            }
        return None
    finally:
        db.close()

def get_by_date_range(start_date: str, end_date: str):
    db = SessionLocal()
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        
        registros = db.query(UPSStatus).filter(UPSStatus.timestamp.between(start_dt, end_dt)).order_by(UPSStatus.timestamp.asc()).all()
        
        return [{
            "timestamp": str(r.timestamp),
            "battery_charge": r.battery_charge,
            "battery_voltage": r.battery_voltage,
            "input_voltage": r.input_voltage,
            "output_voltage": r.output_voltage,
            "ups_load": r.ups_load,
            "ups_status": r.ups_status
        } for r in registros]
    finally:
        db.close()