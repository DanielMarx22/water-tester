Water Tester Project
This is a custom-built, automated aquarium water testing system powered by a Raspberry Pi and inspired by the Neptune Systems Trident. The goal of this project is to create an open, affordable, and fully customizable platform for performing automated water tests (such as alkalinity, calcium, and magnesium) in a saltwater aquarium.

The system consists of a Python Flask web application that provides a responsive dashboard for controlling the testing process and viewing results. The Raspberry Pi interfaces with peristaltic pumps, a magnetic stirrer, and a PiCamera to automate the full testing workflow.




Current Features:

1. Responsive web-based dashboard with manual pump and stirrer controls

2. Automated alkalinity test (Alk Test)

3. Pumps tank water into the test vial

4. Adds reagent while stirring

5. Captures image with PiCamera

6. Analyzes color to determine alkalinity (dKH) using a calibration curve

7. Logs and displays recent test results

8. Magnesium test sequence partially implemented (no color analysis yet)

9. Vial cleaning cycle with programmable rinse and drain steps

10. Emergency stop feature to halt all hardware operations instantly

11. Test history display in the dashboard



Repository Structure:

This GitHub repository contains a safe demonstration version of the project:

1. demo_app.py: a demo-only version of the Flask app. This version is safe to run on any machine and does not control any physical hardware. It simulates the GUI experience and always returns a demo alkalinity value (7.5 dKH) for demonstration purposes.

2. dashboard.html: the main GUI dashboard used by both the live and demo applications.

3. README.md: this document.

4. .gitignore: configuration for files and folders excluded from version control.



The live version of the Flask app (app.py), which controls physical hardware on the Raspberry Pi, is not included in this public repository for security and safety reasons.

How to Use the Demo:
Anyone cloning this repository can run the demo safely on their local machine.

Prerequisites:
Python 3.x
Flask


Installation Steps:
1. Clone this repository
2. Open a terminal and run "cd water-tester" to get to project folder
3. Make sure python is installed and run "python -m pip install flask" to install flask
4. Then run "python3 demo_app.py"


Then open your browser and navigate to:
http://127.0.0.1:5055/

The dashboard will load, and you can interact with it as if it were connected to hardware. Running an Alk Test will always display a simulated result of 7.5 dKH.



Live Deployment (Private)
The full live version of this project runs on a Raspberry Pi and interfaces with:
6 peristaltic pumps, 
A magnetic stirrer, 
A PiCamera for automated color detection, 
Flask web server, 
and an Ngrok tunnel for secure remote access via phone



The live version is not included in this public repository to prevent unintended remote control of the hardware.
 

Planned Future Enhancements:  
1. Full implementation of Calcium and Magnesium tests
2. Improved GUI with live test progress indicators and trends
3. Integration with a smart power strip (similar to Neptune EB832) for controlling power to additional equipment
4. Scheduled automatic testing (daily, weekly, etc.)
5. Remote alerts and notifications


6. Modular refactoring to allow easy integration of additional tests or sensors


Project Goals: 
This project aims to provide a fully open and customizable alternative to commercial aquarium water testers. By using affordable components and open-source software, this system allows full control over the testing process, reagent usage, and data handling.



Disclaimer
This is a personal project and is not affiliated with or endorsed by Neptune Systems or any other commercial vendor. Use of this project and any connected hardware is at your own risk.