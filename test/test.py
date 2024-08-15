import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sqlite3
import complements.sql as sql


def send_voltage_graph():
    conn = sqlite3.connect('ups_data.db')
    cursor = conn.cursor()

    # Seleccionar los datos de las últimas 24 horas
    cursor.execute('''
        SELECT timestamp, output_voltage, battery_charge, ups_load FROM ups_status
        WHERE timestamp >= datetime('now', '-24 hours')
    ''')
    data = cursor.fetchall()
    conn.close()

    if data:
        timestamps, output_voltages, battery_charges, ups_loads = zip(*data)

        # Convertir timestamps a objetos datetime
        timestamps = [mdates.datestr2num(ts) for ts in timestamps]

        plt.figure(figsize=(10, 8))

        # Configurar formato del eje X
        locator = mdates.HourLocator(interval=2)
        formatter = mdates.DateFormatter('%H:%M')

        # Gráfico del voltaje de salida
        plt.subplot(3, 1, 1)
        plt.plot(timestamps, output_voltages,
                 label='Voltaje de salida (V)', color='blue')
        plt.ylabel('Voltaje (V)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        # Marcar el punto máximo y mínimo del voltaje de salida
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

        # Gráfico de la carga de la batería
        plt.subplot(3, 1, 2)
        plt.plot(timestamps, battery_charges,
                 label='Carga de la batería (%)', color='green')
        plt.ylabel('Carga (%)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        # Marcar el punto máximo y mínimo de la carga de la batería
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

        # Gráfico del consumo (carga de la UPS)
        plt.subplot(3, 1, 3)
        plt.plot(timestamps, ups_loads,
                 label='Consumo de la UPS (%)', color='red')
        plt.ylabel('Consumo (%)')
        plt.xlabel('Hora')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.gca().xaxis.set_major_locator(locator)
        plt.gca().xaxis.set_major_formatter(formatter)

        # Marcar el punto máximo y mínimo del consumo de la UPS
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


if __name__ == '__main__':
    send_voltage_graph()
    print('Graph saved!')
