# demo_app.py - safe version of app.py for GitHub (no live control)

from flask import Flask, render_template, request, jsonify
import threading
import time
from datetime import datetime


app = Flask(__name__)

# Demo state variables
PUMP_PINS = [17, 18, 27, 22, 23, 24]
pump_states = {pin: "off" for pin in PUMP_PINS}
stirrer_state = "off"
mg_test_running = False
alk_test_running = False
latest_alk = "--"
latest_b = "--"
test_history = []
emergency_stop = False

# DEMO_MODE flag
DEMO_MODE = True

@app.route('/')
def index():
    return render_template('dashboard.html', pumps=PUMP_PINS, states=pump_states, stirrer_state=stirrer_state)

@app.route('/toggle_pump/<int:pump_id>', methods=['POST'])
def toggle_pump(pump_id):
    if DEMO_MODE:
        print(f"Demo mode: toggle_pump({pump_id}) - no action taken")
        return jsonify({"status": "off"})
    return jsonify({"error": "Demo mode only"}), 400

@app.route('/toggle_stirrer', methods=['POST'])
def toggle_stirrer():
    if DEMO_MODE:
        print("Demo mode: toggle_stirrer() - no action taken")
        return jsonify({"status": "off"})
    return jsonify({"error": "Demo mode only"}), 400

@app.route('/mg_test', methods=['POST'])
def mg_test():
    global mg_test_running
    if DEMO_MODE:
        print("Demo mode: mg_test() - no action taken")
        mg_test_running = True
        def fake_mg_test():
            global mg_test_running
            time.sleep(3)  # Simulate test delay
            mg_test_running = False
        threading.Thread(target=fake_mg_test).start()
        return jsonify({"status": "Demo mode - Mg test simulated"})
    return jsonify({"error": "Demo mode only"}), 400

@app.route('/alk_test', methods=['POST'])
def alk_test():
    global alk_test_running, latest_alk, latest_b, test_history
    if DEMO_MODE:
        print("Demo mode: alk_test() - simulating test")
        alk_test_running = True
        def fake_alk_test():
            global alk_test_running, latest_alk, latest_b, test_history
            time.sleep(3)  # Simulate test delay
            latest_alk = 7.5  # Fixed demo value
            latest_b = 137    # Example blue value (arbitrary)
            print(f"Demo mode: returning dKH={latest_alk}, B={latest_b}")

            test_history.insert(0, {
                "timestamp": datetime.now().isoformat(),
                "alk": latest_alk,
                "blue": latest_b
            })
            test_history = test_history[:50]  # Keep last 50 results
            alk_test_running = False

        threading.Thread(target=fake_alk_test).start()
        return jsonify({"status": "Demo mode - Alk test simulated"})
    return jsonify({"error": "Demo mode only"}), 400

@app.route('/emergency_stop', methods=['POST'])
def stop_all():
    global emergency_stop, mg_test_running, alk_test_running
    if DEMO_MODE:
        print("Demo mode: emergency_stop() - no action taken")
        emergency_stop = True
        mg_test_running = False
        alk_test_running = False
        time.sleep(0.5)
        emergency_stop = False
        return jsonify({"status": "Demo mode - Emergency stop simulated"})
    return jsonify({"error": "Demo mode only"}), 400

@app.route('/clean_vial', methods=['POST'])
def clean_vial_endpoint():
    if DEMO_MODE:
        print("Demo mode: clean_vial() - no action taken")
        return jsonify({"status": "Demo mode - Cleaning simulated"})
    return jsonify({"error": "Demo mode only"}), 400

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

# IMPORTANT: no /go and no /ngrok_url.txt in demo_app.py

if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:5055/")  # open GUI locally on Pi browser
    app.run(host='0.0.0.0', port=5055, debug=False)




