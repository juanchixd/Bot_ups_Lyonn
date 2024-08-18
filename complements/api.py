"""
Created on 2024
@Creator: Juan Bautista Gonzalez
@Position: Student electronic engineering and programmer part-time
@Contact:
    - Email: contacto@juangonzalez.com.ar
"""
# Importar librerías / Import libraries

import uvicorn
from complements.sql import last
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go


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


tags_metadata = [
    {
        "name": "Hello World",
        "description": "Saludar al mundo",
    },
    {
        "name": "UPS",
        "description": "Obtener el estado de la UPS",
    },
    {"name": "Gauges",
        "description": "Obtener los indicadores de la UPS"
     }
]


app = FastAPI(
    title="UPS LYONN API",
    description="API para obtener el estado de la UPS LYONN",
    version="1.0.0",
    contact={
        "name": "Juan Bautista Gonzalez",
        "email": "contacto@juangonzalez.com.ar",
    },
    license_info={
        "name": "MIT",
        "identifier": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
)


@app.get("/", tags=["Hello World"])
async def root():
    return {"message": "Hello World"}


@app.get("/api/realtime_data", tags=["UPS"], responses={
    200: {
        "description": "Response",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2024-08-15 19:10:50",
                    "battery_charge": 100.0,
                    "battery_voltage": 13.6,
                    "input_voltage": 235.2,
                    "output_voltage": 235.2,
                    "ups_load": 27.0,
                    "ups_status": "OL"
                }
            }
        }
    }
})
def realtime_data():
    # Obtiene el último registro
    # Get the last record
    data = get_ups_status()
    # Retorna los datos si existen, de lo contrario, retorna un error 404
    # Returns the data if it exists, otherwise, returns a 404 error
    return data if data else HTTPException(
        status_code=404, detail="No se encontraron registros")


@app.get("/api/last_ups_data", tags=["UPS"], responses={
    200: {
        "description": "Response",
        "content": {
            "application/json": {
                "example": {
                    "timestamp": "2024-08-15 19:10:50",
                    "battery_charge": 100.0,
                    "battery_voltage": 13.6,
                    "input_voltage": 235.2,
                    "output_voltage": 235.2,
                    "ups_load": 27.0,
                    "ups_status": "OL"
                }
            }
        }
    },
    404: {
        "description": "No se encontraron registros",
        "content": {
            "application/json": {
                "example": {"detail": "No se encontraron registros"}
            }
        }
    }
})
def last_ups_data():
    # Obtiene el último registro
    # Get the last record
    data = last()
    # Retorna los datos si existen, de lo contrario, retorna un error 404
    # Returns the data if it exists, otherwise, returns a 404 error
    return data if data else HTTPException(
        status_code=404, detail="No se encontraron registros")


@app.get("/gauge", response_class=HTMLResponse, tags=["Gauges"])
async def create_gauge():
    # Obtiene el último registro / Get the last record
    data = last()

    gauges = []

    # Crea el indicador para la carga de la UPS / Create the indicator for the UPS load
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data["ups_load"],
        title={'text': 'UPS Load', 'font': {'color': 'white'}},
        gauge={'axis': {'range': [None, 100], 'tickcolor': 'white'},
               'bar': {'color': '#4a4a48'},
               'bgcolor': 'black',
               'borderwidth': 2,
               'bordercolor': 'gray',
               'steps': [
            {'range': [0, 60], 'color': '#4CAF50'},
            {'range': [60, 80], 'color': '#FFBF00'},
            {'range': [80, 100], 'color': '#FF4C4C'}]
        }
    ))

    fig1.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=50)
    )

    gauges.append(fig1.to_html(full_html=False, config={"responsive": True}))

    # Crea el indicador para la carga de la batería / Create the indicator for the battery charge
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data["battery_charge"],
        title={'text': 'Battery Charge', 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': 'white'},
            'bar': {'color': '#4a4a48'},
            'bgcolor': 'black',
            'borderwidth': 2,
            'bordercolor': 'gray',
            'steps': [
                {'range': [0, 20], 'color': '#FF4C4C'},
                {'range': [20, 50], 'color': '#FFBF00'},
                {'range': [50, 100], 'color': '#4CAF50'}
            ]
        }
    ))

    fig2.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=50)
    )
    gauges.append(fig2.to_html(full_html=False, config={"responsive": True}))

    # Crea el indicador para el voltaje de entrada / Create the indicator for the input voltage
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data["input_voltage"],
        title={'text': 'Input Voltage', 'font': {'color': 'white'}},
        gauge={'axis': {'range': [170, 270], 'tickcolor': 'white'},
               'bar': {'color': '#4a4a48'},
               'bgcolor': 'black',
               'borderwidth': 2,
               'bordercolor': 'gray',
               'steps': [
            {'range': [170, 190], 'color': '#FF4C4C'},
            {'range': [190, 200], 'color': '#FFBF00'},
            {'range': [200, 240], 'color': '#4CAF50'},
            {'range': [240, 250], 'color': '#FFBF00'},
            {'range': [250, 270], 'color': '#FF4C4C'}]
        }
    ))

    fig3.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        autosize=True,
        margin=dict(l=20, r=20, t=50, b=50)
    )

    gauges.append(fig3.to_html(full_html=False, config={"responsive": True}))

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gauges</title>
        <style>
            body {{
                background-color: black;
                color: white;
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
            .gauge-container {{
                display: flex;
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: center;
                align-items: center;
                gap: 20px;
            }}
            .gauge {{
                width: 100%;
                max-width: 300px;
                box-sizing: border-box;
            }}
            @media (max-width: 768px) {{
                .gauge-container {{
                    flex-direction: column;
                    align-items: center;
                }}
                .gauge {{
                    width: 80%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="gauge-container">
            <div class="gauge">{gauges[0]}</div>
            <div class="gauge">{gauges[1]}</div>
            <div class="gauge">{gauges[2]}</div>
        </div>
        
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


def main():
    uvicorn.run(app, host="0.0.0.0", port=5005)


if __name__ == "__main__":
    main()
