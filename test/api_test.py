import sqlite3
import uvicorn
from fastapi import FastAPI, HTTPException
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/last_ups_data")
def last_ups_data():
    conn = sqlite3.connect('ups_data.db')
    cursor = conn.cursor()

    # Consulta el último registro
    cursor.execute(
        '''SELECT * FROM ups_status ORDER BY timestamp DESC LIMIT 1''')
    row = cursor.fetchone()
    conn.close()

    if row:
        # Crea un diccionario con los datos
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
    else:
        raise HTTPException(
            status_code=404, detail="No se encontraron registros")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
