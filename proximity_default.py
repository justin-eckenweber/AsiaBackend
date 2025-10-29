import RPi.GPIO as GPIO
import time

sensor_pin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor_pin, GPIO.IN)

state = 0

try:
    while True:
        val = GPIO.input(sensor_pin)
        if val == 1:
            #GPIO.output(led_pin, GPIO.HIGH)
            if state == 0:
                print("Motion detected!")
                state = 1
        else:
            #GPIO.output(led_pin, GPIO.LOW)
            if state == 1:
                print("Motion stopped!")
                state = 0
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
