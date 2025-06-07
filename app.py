from flask import Flask, render_template, request, jsonify, redirect
import lgpio
import threading
import time
import os
from datetime import datetime
from picamera2 import Picamera2
from PIL import Image
from contextlib import contextmanager

app = Flask(__name__)

PUMP_PINS = [17, 18, 27, 22, 23, 24]
STIRRER_PIN = 5
h = lgpio.gpiochip_open(0)

pump_states = {}
stirrer_state = "off"
mg_test_running = False
alk_test_running = False
latest_alk = "--"
latest_b = "--"
test_history = []
emergency_stop = False

calibration = [
    (8, 5), (14, 6), (27, 7), (95, 8), (137, 9),
    (159, 10), (164, 11), (168, 12), (171, 13), (173, 14)
]

# Setup GPIO
for pin in PUMP_PINS + [STIRRER_PIN]:
    try:
        lgpio.gpio_free(h, pin)
    except:
        pass
    try:
        lgpio.gpio_claim_output(h, pin, 1)
        if pin != STIRRER_PIN:
            pump_states[pin] = "off"
    except Exception as e:
        print(f"Error claiming pin {pin}: {e}")

def set_pin(pin, state, duration=None, is_stirrer=False):
    global stirrer_state
    if emergency_stop:
        return
        
    if state == "on":
        lgpio.gpio_write(h, pin, 0)
        if is_stirrer:
            stirrer_state = "on"
        else:
            pump_states[pin] = "on"
        if duration:
            def turn_off_later(p, delay):
                start_time = time.time()
                while time.time() - start_time < delay and not emergency_stop:
                    time.sleep(0.1)
                if not emergency_stop:
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

def emergency_shutdown():
    """Turn off all pumps and stirrer immediately but allow new operations"""
    global emergency_stop, stirrer_state, pump_states, mg_test_running, alk_test_running
    
    # Set emergency stop flag to abort current operations
    emergency_stop = True
    
    # Turn off all hardware immediately
    stirrer_state = "off"
    for pin in PUMP_PINS + [STIRRER_PIN]:
        lgpio.gpio_write(h, pin, 1)
        if pin != STIRRER_PIN:
            pump_states[pin] = "off"
    
    # Reset test flags
    mg_test_running = False
    alk_test_running = False
    
    # Immediately allow new operations
    emergency_stop = False

def clean_vial(cycles=1):
    """General vial cleaning sequence with proper draining"""
    global emergency_stop
    drain_pump = 4    # Pump 5 (GPIO 23)
    fresh_water_pump = 5  # Pump 6 (GPIO 24)
    
    rinse_durations = {
        'drain': 30,    # Complete drain first
        'fill': 20,     # Fresh water fill
        'stir': 15      # Mixing
    }
    
    for _ in range(cycles):
        if emergency_stop: 
            return False  # Indicate cleaning was aborted
        
        # Drain first to ensure vial is empty
        set_pin(PUMP_PINS[drain_pump], "on", rinse_durations['drain'])
        time.sleep(rinse_durations['drain'] + 1)
        if emergency_stop: 
            return False
        
        # Fill with fresh water
        set_pin(PUMP_PINS[fresh_water_pump], "on", rinse_durations['fill'])
        time.sleep(rinse_durations['fill'] + 1)
        if emergency_stop: 
            return False
        
        # Stir to rinse
        set_pin(STIRRER_PIN, "on", rinse_durations['stir'], is_stirrer=True)
        time.sleep(rinse_durations['stir'] + 1)
        if emergency_stop: 
            return False
        
        # Drain again
        set_pin(PUMP_PINS[drain_pump], "on", rinse_durations['drain'])
        time.sleep(rinse_durations['drain'] + 1)
    
    return True  # Cleaning completed successfully

@contextmanager
def camera_session():
    picam2 = None
    try:
        picam2 = Picamera2()
        config = picam2.create_still_configuration(main={"size": (3280, 2464)})
        picam2.configure(config)
        picam2.start()
        time.sleep(2)
        yield picam2
    finally:
        if picam2 is not None:
            picam2.stop()
            picam2.close()

@app.route('/')
def index():
    return render_template('dashboard.html', pumps=PUMP_PINS, states=pump_states, stirrer_state=stirrer_state)

@app.route('/toggle_pump/<int:pump_id>', methods=['POST'])
def toggle_pump(pump_id):
    if emergency_stop:
        return jsonify({"error": "System in emergency stop"}), 400
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
    if emergency_stop:
        return jsonify({"error": "System in emergency stop"}), 400
    new_state = "on" if stirrer_state == "off" else "off"
    set_pin(STIRRER_PIN, new_state, is_stirrer=True)
    return jsonify({"status": stirrer_state})

@app.route('/mg_test', methods=['POST'])
def mg_test():
    global mg_test_running, emergency_stop
    if emergency_stop or mg_test_running:
        return jsonify({"error": "System in emergency stop or test already running"}), 400
        
    water_pump_index = 0
    reagent_pump_index = 1
    drain_pump = 4
    water_duration = 10
    reagent_duration = int(water_duration * 0.9)

    def sequence():
        global mg_test_running
        mg_test_running = True

        try:
            # Ensure vial is empty before starting
            if not emergency_stop:
                set_pin(PUMP_PINS[drain_pump], "on", 30)
                time.sleep(31)
            
            # Water fill
            if not emergency_stop:
                set_pin(PUMP_PINS[water_pump_index], "on", water_duration)
                time.sleep(water_duration + 1)
            
            # Reagent add
            if not emergency_stop:
                set_pin(PUMP_PINS[reagent_pump_index], "on", reagent_duration)
                time.sleep(reagent_duration + 1)
            
            # Stirring
            if not emergency_stop:
                set_pin(STIRRER_PIN, "on", 5, is_stirrer=True)
                time.sleep(6)
            
            # Cleaning
            if not emergency_stop:
                clean_vial(cycles=2)
                
        finally:
            mg_test_running = False

    threading.Thread(target=sequence).start()
    return jsonify({"status": "Mg test started"})

@app.route('/alk_test', methods=['POST'])
def alk_test():
    global alk_test_running, latest_alk, latest_b, test_history, emergency_stop
    if emergency_stop or alk_test_running:
        return jsonify({"error": "System in emergency stop or test already running"}), 400

    salt_water_pump = 0
    reagent_pump = 1
    drain_pump = 4
    water_duration = 10
    reagent_duration = water_duration * 0.90

    def sequence():
        global alk_test_running, latest_alk, latest_b, test_history
        alk_test_running = True

        try:
            # Ensure vial is empty before starting
            if not emergency_stop:
                set_pin(PUMP_PINS[drain_pump], "on", 30)
                time.sleep(31)
            
            # Water fill
            if not emergency_stop:
                set_pin(PUMP_PINS[salt_water_pump], "on", water_duration)
                time.sleep(water_duration + 1)
            
            # Reagent add and stirring
            if not emergency_stop:
                set_pin(STIRRER_PIN, "on", water_duration + 1, is_stirrer=True)
                set_pin(PUMP_PINS[reagent_pump], "on", reagent_duration)
                time.sleep(water_duration + 2)

            # Image capture and processing
            if not emergency_stop:
                try:
                    save_dir = "/home/danielmarx/Desktop/CodeStuff/captured_images"
                    os.makedirs(save_dir, exist_ok=True)
                    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                    filename = os.path.join(save_dir, f"image_{timestamp}.jpg")

                    with camera_session() as picam2:
                        picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})
                        image_data = picam2.capture_array("main")
                        
                        pil_image = Image.fromarray(image_data)
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        
                        pil_image.save(filename)
                        
                        r, g, b = pil_image.getpixel((1700, 1200))
                        latest_b = int(b)
                        b_val = latest_b

                        closest = min(calibration, key=lambda x: abs(x[0] - b_val))
                        if abs(closest[0] - b_val) <= 5:
                            latest_alk = closest[1]
                        else:
                            for i in range(len(calibration) - 1):
                                x1, y1 = calibration[i]
                                x2, y2 = calibration[i + 1]
                                if x1 <= b_val <= x2:
                                    latest_alk = round(y1 + (b_val - x1) * (y2 - y1) / (x2 - x1), 1)
                                    break
                            else:
                                latest_alk = "Out of range"

                        print(f"🟦 Blue value: {latest_b} | dKH: {latest_alk}")
                        with open("alk_log.txt", "a") as f:
                            f.write(f"{datetime.now().isoformat()} - dKH: {latest_alk}, B: {latest_b}\n")
                        
                        test_history.insert(0, {
                            "timestamp": datetime.now().isoformat(),
                            "alk": latest_alk,
                            "blue": latest_b
                        })
                        test_history = test_history[:50]

                except Exception as e:
                    print("❌ Error during test:", str(e))
                    latest_alk = "Error"
                    latest_b = "--"
                    import traceback
                    traceback.print_exc()

            # Cleaning - now with proper draining sequence
            if not emergency_stop:
                clean_vial(cycles=2)

        finally:
            alk_test_running = False

    threading.Thread(target=sequence).start()
    return jsonify({"status": "Alk test started"})

@app.route('/emergency_stop', methods=['POST'])
def stop_all():
    emergency_shutdown()
    return jsonify({"status": "Emergency stop activated - system ready for new commands"})

@app.route('/clean_vial', methods=['POST'])
def clean_vial_endpoint():
    if emergency_stop:
        return jsonify({"error": "System in emergency stop"}), 400
    
    def cleaning_thread():
        try:
            clean_vial(cycles=1)
        except Exception as e:
            print(f"Cleaning error: {e}")
    
    threading.Thread(target=cleaning_thread).start()
    return jsonify({"status": "Cleaning started"})

@app.route("/status")
def status():
    return jsonify(
        [pump_states[pin] for pin in PUMP_PINS] +
        [stirrer_state, 
         "running" if mg_test_running else "off", 
         "running" if alk_test_running else "off", 
         latest_alk, 
         latest_b,
         "stopped" if emergency_stop else "normal"]
    )

@app.route("/test_history")
def get_test_history():
    return jsonify(test_history)

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