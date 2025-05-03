from flask import Flask, render_template, request, jsonify, redirect
import lgpio
import threading
import time

app = Flask(__name__)

# GPIO pins
PUMP_PINS = [17, 18, 27, 22, 23, 24]  # 6 pumps
STIRRER_PIN = 5  # GPIO 5 for stirrer motor
h = lgpio.gpiochip_open(0)

# States
pump_states = {}
stirrer_state = "off"
mg_test_running = False

# Safe GPIO reset
for pin in PUMP_PINS + [STIRRER_PIN]:
    try:
        lgpio.gpio_free(h, pin)
    except Exception as e:
        print(f"Warning: gpio_free error on pin {pin}: {e}")
    try:
        lgpio.gpio_claim_output(h, pin, 1)
        if pin != STIRRER_PIN:
            pump_states[pin] = "off"
    except Exception as e:
        print(f"Error: gpio_claim_output failed for pin {pin}: {e}")


# Set pin ON or OFF
def set_pin(pin, state, duration=None, is_stirrer=False):
    global stirrer_state
    if state == "on":
        lgpio.gpio_write(h, pin, 0)  # ON = 0
        if is_stirrer:
            stirrer_state = "on"
        else:
            pump_states[pin] = "on"
        if duration:
            def turn_off_later(p, delay):
                time.sleep(delay)
                lgpio.gpio_write(h, p, 1)
                if is_stirrer:
                    stirrer_state = "off"
                else:
                    pump_states[p] = "off"
            threading.Thread(target=turn_off_later, args=(pin, duration)).start()
    else:
        lgpio.gpio_write(h, pin, 1)
        if is_stirrer:
            stirrer_state = "off"
        else:
            pump_states[pin] = "off"

@app.route('/')
def index():
    return render_template('dashboard.html', pumps=PUMP_PINS, states=pump_states, stirrer_state=stirrer_state)

@app.route('/toggle_pump/<int:pump_id>', methods=['POST'])
def toggle_pump(pump_id):
    if 0 <= pump_id < len(PUMP_PINS):
        pin = PUMP_PINS[pump_id]
        data = request.get_json()
        duration = data.get("time")
        try:
            duration = int(duration)
        except:
            duration = None
        new_state = "on" if pump_states[pin] == "off" else "off"
        set_pin(pin, new_state, duration)
        return jsonify({"status": pump_states[pin]})
    return jsonify({"error": "Invalid pump ID"}), 400

@app.route('/toggle_stirrer', methods=['POST'])
def toggle_stirrer():
    new_state = "on" if stirrer_state == "off" else "off"
    set_pin(STIRRER_PIN, new_state, is_stirrer=True)
    return jsonify({"status": stirrer_state})

@app.route('/mg_test', methods=['POST'])
def mg_test():
    global mg_test_running

    water_pump_index = 0  # Pump 1
    reagent_pump_index = 1  # Pump 2
    water_duration = 5  # seconds
    reagent_duration = int(water_duration * (9/10) * (10/9))  # Adjust for slower reagent pump

    def sequence():
        global mg_test_running
        mg_test_running = True

        # Pump water
        set_pin(PUMP_PINS[water_pump_index], "on", water_duration)
        time.sleep(water_duration + 1)

        # Pump reagent
        set_pin(PUMP_PINS[reagent_pump_index], "on", reagent_duration)
        time.sleep(reagent_duration + 1)

        # Stir
        set_pin(STIRRER_PIN, "on", 5, is_stirrer=True)
        time.sleep(5 + 1)

        mg_test_running = False

    threading.Thread(target=sequence).start()

    return jsonify({"status": "Mg test started"})

@app.route("/status")
def status():
    return jsonify([pump_states[pin] for pin in PUMP_PINS] + [stirrer_state, "running" if mg_test_running else "off"])

@app.route("/ngrok_url.txt")
def ngrok_url():
    try:
        with open("/home/danielmarx/Desktop/CodeStuff/ngrok_url.txt") as f:
            return f.read()
    except:
        return "URL not ready yet", 503

@app.route("/go")
def go():
    try:
        with open("/home/danielmarx/Desktop/CodeStuff/ngrok_url.txt") as f:
            url = f.read().strip()
            return redirect(url, code=302)
    except:
        return "ngrok URL not available yet", 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=False)

