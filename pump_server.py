from flask import Flask, request
import lgpio
import time

app = Flask(__name__)

PUMP_PIN = 17
h = lgpio.gpiochip_open(0)  # Open gpiochip0 (default)

# Set PUMP_PIN as output and initialize it to HIGH (OFF for active-low pump)
try:
    lgpio.gpio_free(h, PUMP_PIN)
except:
    pass  # No error if already free

lgpio.gpio_claim_output(h, PUMP_PIN, 1)  # 1 = OFF for active-low relay


@app.route('/pump', methods=['POST'])
def control_pump():
    data = request.get_json()
    action = data.get('action')
    duration = data.get('duration')

    print(f"Received action: {action}, duration: {duration}")

    if action == "on":
        print("Turning pump ON")
        lgpio.gpio_write(h, PUMP_PIN, 0)  # Active-low ON
        if duration and duration > 0:
            time.sleep(duration)
            print("Turning pump OFF after duration")
            lgpio.gpio_write(h, PUMP_PIN, 1)
    elif action == "off":
        print("Turning pump OFF")
        lgpio.gpio_write(h, PUMP_PIN, 1)

    return {'status': 'success'}

app.run(host='0.0.0.0', port=5000)
