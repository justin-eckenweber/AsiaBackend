import bme680
import uvicorn
from fastapi import FastAPI
import RPi.GPIO as GPIO
import time
import threading

sensor_pin = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN)

state = 0
motion_detected = False  # Shared state

temperature = 0
humidity = 0
pressure = 0
gas_resistance = 0

def proxmity_loop():
    global state, motion_detected
    try:
        while True:
            val = GPIO.input(sensor_pin)
            if val == 1:
                if state == 0:
                    print("Motion detected!")
                    motion_detected = True
                    state = 1
            else:
                if state == 1:
                    print("Motion stopped!")
                    motion_detected = False
                    state = 0
            time.sleep(0.1)
    except Exception as e:
        print(f"Sensor error: {e}")
    finally:
        GPIO.cleanup()


def sensor_loop():
    global temperature, humidity, pressure, gas_resistance
    bme680sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

    bme680sensor.set_humidity_oversample(bme680.OS_2X)
    bme680sensor.set_pressure_oversample(bme680.OS_4X)
    bme680sensor.set_temperature_oversample(bme680.OS_8X)
    bme680sensor.set_filter(bme680.FILTER_SIZE_3)
    bme680sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

    bme680sensor.set_gas_heater_temperature(320)
    bme680sensor.set_gas_heater_duration(150)
    bme680sensor.select_gas_heater_profile(0)

    while True:
        if bme680sensor.get_sensor_data():
            temperature = bme680sensor.data.temperature
            pressure = bme680sensor.data.pressure
            humidity = bme680sensor.data.humidity
            gas_resistance = bme680sensor.data.gas_resistance

        time.sleep(1)


app = FastAPI()

@app.on_event("startup")
def startup_event():
    sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
    sensor_thread.start()

    proxmity_thread = threading.Thread(target=proxmity_loop, daemon=True)
    proxmity_thread.start()
    print("Sensor thread started")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/sensor")
async def sensor():
    return {
        "motion": motion_detected,
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "gas_resistance": gas_resistance
    }



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)