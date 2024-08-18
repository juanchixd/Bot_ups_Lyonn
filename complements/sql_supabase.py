"""
Created on 2024
@Creator: Juan Bautista Gonzalez
@Position: Student electronic engineering and programmer part-time
@Contact:
    - Email: contacto@juangonzalez.com.ar
"""
import os
import time
from dotenv import load_dotenv, dotenv_values
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_supabase(status):
    data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'battery_charge': status['battery_charge'],
        'battery_voltage': status['battery_voltage'],
        'input_voltage': status['input_voltage'],
        'output_voltage': status['output_voltage'],
        'ups_load': status['ups_load'],
        'ups_status': status['ups_status']
    }
    supabase.table('ups_status').insert(data).execute()


if __name__ == '__main__':
    status = {
        'battery_charge': 100.0,
        'battery_voltage': 13.6,
        'input_voltage': 235.2,
        'output_voltage': 235.2,
        'ups_load': 27.0,
        'ups_status': 'OL'
    }
    upload_supabase(status)
