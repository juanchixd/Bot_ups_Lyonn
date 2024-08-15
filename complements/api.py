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
from fastapi import FastAPI, HTTPException

tags_metadata = [
    {
        "name": "Hello World",
        "description": "Saludar al mundo",
    },
    {
        "name": "UPS",
        "description": "Obtener el estado de la UPS",
    },
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


def main():
    uvicorn.run(app, host="0.0.0.0", port=5005)


if __name__ == "__main__":
    main()
