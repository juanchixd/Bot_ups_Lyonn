"""
Created on 2024
@Creator: Juan Bautista Gonzalez
@Position: Student electronic engineering and programmer part-time
@Contact:
    - Email: contacto@juangonzalez.com.ar
"""
# Importar librerías / Import libraries
import telebot
import os
import subprocess
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import complements.api as api
import complements.sql as sql

from dotenv import load_dotenv, dotenv_values
from subprocess import Popen, PIPE

load_dotenv()
# Variables
previous_status = None
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
SUPABASE = os.getenv('SUPABASE')

# Inicializar la api / Initialize the api
threading.Thread(target=api.main, daemon=True).start()

# Inicializar el bot de Telegram / Initialize the Telegram bot
bot = telebot.TeleBot(TOKEN)

# Inicializar la base de datos / Initialize the database
sql.init_db()


def get_ups_status():
    try:
        # Obtener el estado de la UPS
        # Get the UPS status
        result = subprocess.run(
            ['upsc', 'ups@localhost'], capture_output=True, text=True)
        output = result.stdout.splitlines()

        # Extraer los datos del estado de la UPS
        # Extract the UPS status data
        status_data = {}
        status_data['battery_charge'] = [line.split(
            ": ")[1] for line in output if "battery.charge:" in line][0]
        status_data['battery_voltage'] = [line.split(
            ": ")[1] for line in output if "battery.voltage:" in line][0]
        status_data['input_voltage'] = [line.split(
            ": ")[1] for line in output if "input.voltage:" in line][0]
        status_data['output_voltage'] = [line.split(
            ": ")[1] for line in output if "output.voltage:" in line][0]
        status_data['ups_load'] = [line.split(
            ": ")[1] for line in output if "ups.load:" in line][0]
        status_data['ups_status'] = [line.split(
            ": ")[1] for line in output if "ups.status:" in line][0]
        return status_data
    except Exception as e:
        return str(e)


def notify_ups_status():
    global previous_status
    while True:
        try:
            status = get_ups_status()
            if status['ups_status'] != 'OL' and previous_status == 'OL':
                bot.send_message(
                    CHAT_ID, f"¡ALERTA! ¡La UPS paso a modo batería!")
                previous_status = status['ups_status']
            else:
                if status['ups_status'] == 'OL' and previous_status != 'OL':
                    bot.send_message(
                        CHAT_ID, f"¡La UPS volvió a modo normal!")
                    previous_status = status['ups_status']
            time.sleep(10)
        except Exception as e:
            bot.send_message(
                CHAT_ID, f"Ocurrió un error al consultar el estado de la UPS: {e}")
            time.sleep(10)


# Guardar el estado de la UPS en la base de datos
# Save the UPS status in the database

def save_ups_status():
    while True:
        try:
            status = get_ups_status()
            sql.save_status(status)
            if SUPABASE == "True":
                import complements.sql_supabase as sql_supabase
                sql_supabase.upload_supabase(status)
            time.sleep(300)
        except Exception as e:
            bot.send_message(
                CHAT_ID, f"Ocurrió un error al guardar el estado de la UPS: {e}")
            time.sleep(300)


threading.Thread(target=notify_ups_status, daemon=True).start()
threading.Thread(target=save_ups_status, daemon=True).start()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, """¡Hola! 🤖
Soy un bot que te permite saber el estado de la UPS Lyonn. 
¡Escribe /read para obtener la información!
¡Escribe /graph para obtener un gráfico de las últimas 24 horas!
Creado por Juan Bautista Gonzalez
Codigo fuente: https://github.com/juanchixd/Bot_ups_Lyonn""")


@bot.message_handler(commands=['read'])
def send_status(message):
    # Obtener el estado de la UPS
    # Get the UPS status

    status_data = get_ups_status()
    # Verificar que sea una respuesta válida
    # Check if it's a valid response
    if isinstance(status_data, dict):
        response = f"Estado de la UPS:\n\n"
        response += f"Carga de la batería: {status_data['battery_charge']}%\n"
        response += f"Voltaje de la batería: {status_data['battery_voltage']} V\n"
        response += f"Voltaje de entrada: {status_data['input_voltage']} V\n"
        response += f"Voltaje de salida: {status_data['output_voltage']} V\n"
        consumo = str(800 * float(status_data['ups_load'])/100) + " W"
        response += f"Carga de la UPS: {status_data['ups_load']}% = {consumo}\n"
        status = "Online" if status_data['ups_status'] == 'OL' else "Offline"
        response += f"Estado de la UPS: {status}\n"
    else:
        response = f"Ocurrió un error al obtener el estado de la UPS: {status_data}"
    # Responder al mensaje
    bot.reply_to(message, response)


@bot.message_handler(commands=['graph'])
def send_graph(message):
    data = sql.last_24()
    if data:
        timestamps, output_voltages, battery_charges, ups_loads = zip(*data)

        # Convertir timestamps a objetos datetime / Convert timestamps to datetime objects
        timestamps = [mdates.datestr2num(ts) for ts in timestamps]

        plt.figure(figsize=(10, 8))

        # Configurar formato del eje X / Configure X axis format
        locator = mdates.HourLocator(interval=2)
        formatter = mdates.DateFormatter('%H:%M')

        # Gráfico del voltaje de salida / Output voltage graph
        plt.subplot(3, 1, 1)
        plt.plot(timestamps, output_voltages,
                 label='Voltaje de salida (V)', color='blue')
        plt.ylabel('Voltaje (V)')
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.gca().xaxis.set_ticklabels([])

        # Marcar el punto máximo y mínimo del voltaje de salida / Mark the maximum and minimum output voltage point
        max_voltage = max(output_voltages)
        min_voltage = min(output_voltages)
        max_time_voltage = timestamps[output_voltages.index(max_voltage)]
        min_time_voltage = timestamps[output_voltages.index(min_voltage)]
        plt.plot(max_time_voltage, max_voltage, 'ro')
        plt.plot(min_time_voltage, min_voltage, 'go')
        plt.annotate(f'Max: {max_voltage}V', xy=(max_time_voltage, max_voltage), xytext=(max_time_voltage, max_voltage + 2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))
        plt.annotate(f'Min: {min_voltage}V', xy=(min_time_voltage, min_voltage), xytext=(min_time_voltage, min_voltage - 2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))

        # Gráfico de la carga de la batería / Battery charge graph
        plt.subplot(3, 1, 2)
        plt.plot(timestamps, battery_charges,
                 label='Carga de la batería (%)', color='green')
        plt.ylabel('Carga (%)')
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.gca().xaxis.set_ticklabels([])

        # Marcar el punto máximo y mínimo de la carga de la batería / Mark the maximum and minimum battery charge point
        max_charge = max(battery_charges)
        min_charge = min(battery_charges)
        max_time_charge = timestamps[battery_charges.index(max_charge)]
        min_time_charge = timestamps[battery_charges.index(min_charge)]
        plt.plot(max_time_charge, max_charge, 'ro')
        plt.plot(min_time_charge, min_charge, 'go')
        plt.annotate(f'Max: {max_charge}%', xy=(max_time_charge, max_charge), xytext=(max_time_charge, max_charge + 2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))
        plt.annotate(f'Min: {min_charge}%', xy=(min_time_charge, min_charge), xytext=(min_time_charge, min_charge - 2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))

        # Gráfico del consumo (carga de la UPS) / UPS load graph
        plt.subplot(3, 1, 3)
        plt.plot(timestamps, ups_loads,
                 label='Consumo de la UPS (%)', color='red')
        plt.ylabel('Consumo (%)')
        plt.xlabel('Hora')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        # Marcar el punto máximo y mínimo del consumo de la UPS / Mark the maximum and minimum UPS load point
        max_load = max(ups_loads)
        min_load = min(ups_loads)
        max_time_load = timestamps[ups_loads.index(max_load)]
        min_time_load = timestamps[ups_loads.index(min_load)]
        plt.plot(max_time_load, max_load, 'ro')
        plt.plot(min_time_load, min_load, 'go')
        plt.annotate(f'Max: {max_load}%', xy=(max_time_load, max_load), xytext=(max_time_load, max_load + 2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))
        plt.annotate(f'Min: {min_load}%', xy=(min_time_load, min_load), xytext=(min_time_load, min_load - 2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5))

        plt.tight_layout()
        plt.savefig('graph.png', bbox_inches='tight')
        plt.close()

        with open('graph.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.reply_to(
            message, "No hay datos disponibles para generar el gráfico")


bot.infinity_polling()
