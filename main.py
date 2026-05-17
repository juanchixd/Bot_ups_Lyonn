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
import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
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
            if not isinstance(status, dict):
                if len(status) > 4000:
                    status = status[:4000] + "..."
                # Enviar mensaje de error al chat de Telegram
                # Send error message to Telegram chat
                bot.send_message(
                    CHAT_ID, f"Ocurrió un error al obtener el estado de la UPS: {status}")
                time.sleep(10)
                continue
            # Verificar si pasó a batería
            if status['ups_status'] != 'OL' and previous_status == 'OL':
                try:
                    input_voltage = float(status['input_voltage'])
                except ValueError:
                    input_voltage = None

                # Determinar la causa: falta de luz o sobretensión
                if input_voltage is not None:
                    if input_voltage < 170:
                        causa = "Falta de energía eléctrica (bajo voltaje)"
                    elif input_voltage > 260:
                        causa = "Sobretensión en la línea"
                    else:
                        causa = "Causa desconocida (voltaje dentro de rango)"
                else:
                    causa = "No se pudo leer el voltaje de entrada"

                bot.send_message(
                    CHAT_ID,
                    f"⚠️ ¡ALERTA! ¡La UPS pasó a modo batería!\nMotivo: {causa}\nVoltaje de entrada: {status['input_voltage']} V"
                )
                previous_status = status['ups_status']

            else:
                # Detectar si volvió a modo normal
                if status['ups_status'] == 'OL' and previous_status != 'OL':
                    bot.send_message(
                        CHAT_ID, f"✅ ¡La UPS volvió a modo normal!"
                    )
                    previous_status = status['ups_status']
            time.sleep(10)
        except Exception as e:
            if len(str(e)) > 4000:
                e = str(e)[:4000] + "..."
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
    # time_now = time.time()
    data = sql.last_24()
    # time_post_query = time.time()
    if not data:
        bot.reply_to(message, "No hay datos disponibles para generar el gráfico.")
        return

    # Desempaquetar datos
    timestamps_str, output_voltages, battery_charges, ups_loads = zip(*data)
    
    # Armamos un DataFrame y borramos duplicados de tiempo exacto (necesario para poder suavizar las curvas)
    df = pd.DataFrame({
        'ts': pd.to_datetime(timestamps_str, format='mixed'),
        'volt': output_voltages,
        'bat': battery_charges,
        'load': ups_loads
    }).drop_duplicates(subset=['ts']).sort_values(by='ts')

    # Convertir las fechas a formato numérico para la matemática de la curva
    x_num = mdates.date2num(df['ts'])
    # Crear un eje X súper denso (300 puntos) para que la curva se dibuje fluida
    x_smooth = np.linspace(x_num.min(), x_num.max(), 300)
    timestamps_smooth = mdates.num2date(x_smooth)

    # Configuración de estilo Light Mode amigable
    plt.style.use('default')
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    
    # Color de fondo blanco tiza
    bg_color = '#f8f9fa'
    fig.patch.set_facecolor(bg_color)
    
    # Paleta de colores estéticos
    c_volt = '#0077b6' # Azul Océano
    c_bat = '#2a9d8f'  # Verde Esmeralda apagado
    c_load = '#e76f51' # Naranja Terracota

    def marcar_extremos(ax, x_real, y_real, color, unidad):
        max_y, min_y = max(y_real), min(y_real)
        idx_max, idx_min = list(y_real).index(max_y), list(y_real).index(min_y)
        max_x, min_x = x_real.iloc[idx_max], x_real.iloc[idx_min]
        
        # Puntos resaltados (se marcan sobre los datos reales, no los suavizados)
        ax.plot(max_x, max_y, marker='o', color=color, markersize=7, markeredgecolor='white', markeredgewidth=1.5)
        ax.plot(min_x, min_y, marker='o', color=color, markersize=7, markeredgecolor='white', markeredgewidth=1.5)
        
        # Textos con fondo semitransparente para que no se pisen con las líneas
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8)
        ax.annotate(f'Max: {max_y}{unidad}', xy=(max_x, max_y), xytext=(0, 10), 
                    textcoords='offset points', ha='center', color=color, fontsize=9, fontweight='bold', bbox=bbox_props)
        ax.annotate(f'Min: {min_y}{unidad}', xy=(min_x, min_y), xytext=(0, -18), 
                    textcoords='offset points', ha='center', color=color, fontsize=9, fontweight='bold', bbox=bbox_props)

    # Configurar cada subgráfico
    graficos = [
        (axs[0], df['volt'], c_volt, 'Voltaje de salida (V)', 'V'),
        (axs[1], df['bat'], c_bat, 'Carga de la batería (%)', '%'),
        (axs[2], df['load'], c_load, 'Consumo de la UPS (%)', '%')
    ]

    for ax, y_data, color, titulo, unidad in graficos:
        ax.set_facecolor(bg_color)
        
        # Magia matemática: Crear la curva suave usando interpolación PCHIP
        interpolador = PchipInterpolator(x_num, y_data)
        y_smooth = interpolador(x_smooth)
        
        # Dibujar la curva suave y rellenar abajo
        ax.plot(timestamps_smooth, y_smooth, color=color, linewidth=2.5)
        ax.fill_between(timestamps_smooth, y_smooth, color=color, alpha=0.1)
        
        # Títulos
        ax.set_title(titulo, color='#333333', pad=12, fontsize=12, fontweight='bold')
        
        # Grilla clarita
        ax.grid(color='#e9ecef', linestyle='-', linewidth=1.2)
        
        # Ocultar bordes innecesarios (estilo dashboard minimalista)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#ced4da')
        ax.spines['bottom'].set_color('#ced4da')
        ax.tick_params(colors='#6c757d')
        
        marcar_extremos(ax, df['ts'], y_data, color, unidad)

    # Formato del eje X (Fechas)
    axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45, color='#6c757d')

    plt.tight_layout()
    
    # Guardar imagen
    plt.savefig('graph.png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=120)
    plt.close()
    # time_post_graph = time.time()
    # Enviar foto
    with open('graph.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

    # bot.send_message(message.chat.id, f"Tiempo para consulta: {time_post_query - time_now:.2f} segundos\nTiempo para generar gráfico: {time_post_graph - time_post_query:.2f} segundos")

bot.infinity_polling()
