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
import complements.sql as sql
from dotenv import load_dotenv, dotenv_values
from subprocess import Popen, PIPE

load_dotenv()
# Variables
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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

# Guardar el estado de la UPS en la base de datos
# Save the UPS status in the database


def save_ups_status():
    while True:
        try:
            status = get_ups_status()
            sql.save_status(status)
            time.sleep(300)
        except Exception as e:
            bot.send_message(
                CHAT_ID, f"Ocurrió un error al guardar el estado de la UPS: {e}")
            time.sleep(300)


threading.Thread(target=save_ups_status, daemon=True).start()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, "¡Hola! Soy un bot que te permite saber el estado de la UPS. ¡Escribe /status para obtener la información!")


@bot.message_handler(commands=['status'])
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

        plt.figure(figsize=(10, 8))

        plt.subplot(3, 1, 1)
        plt.plot(timestamps, output_voltages,
                 label='Voltaje de salida (V)', color='blue')
        plt.title('Voltaje de salida de la UPS')
        plt.ylabel('Voltaje (V)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(timestamps, battery_charges,
                 label='Carga de la batería (%)', color='green')
        plt.title('Carga de la batería de la UPS')
        plt.ylabel('Carga (%)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(timestamps, ups_loads,
                 label='Carga de la UPS (%)', color='red')
        plt.title('Carga de la UPS')
        plt.ylabel('Carga (%)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.savefig('graph.png', bbox_inches='tight')
        plt.close()

        with open('graph.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
    else:
        bot.reply_to(
            message, "No hay datos disponibles para generar el gráfico")


bot.infinity_polling()
