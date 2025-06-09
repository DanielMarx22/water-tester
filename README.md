Water Tester Project
This is a custom-built, automated aquarium water testing system powered by a Raspberry Pi and inspired by the Neptune Systems Trident. The goal of this project is to create an open, affordable, and fully customizable platform for performing automated water tests (such as alkalinity, calcium, and magnesium) in a saltwater aquarium.

The system consists of a Python Flask web application that provides a responsive dashboard for controlling the testing process and viewing results. The Raspberry Pi interfaces with peristaltic pumps, a magnetic stirrer, and a PiCamera to automate the full testing workflow.

Current Features
Responsive web-based dashboard with manual pump and stirrer controls

Automated alkalinity test (Alk Test)

Pumps tank water into the test vial

Adds reagent while stirring

Captures image with PiCamera

Analyzes color to determine alkalinity (dKH) using a calibration curve

Logs and displays recent test results

Magnesium test sequence partially implemented (no color analysis yet)

Vial cleaning cycle with programmable rinse and drain steps

Emergency stop feature to halt all hardware operations instantly

Test history display in the dashboard

Repository Structure
This GitHub repository contains a safe demonstration version of the project:

demo_app.py: a demo-only version of the Flask app. This version is safe to run on any machine and does not control any physical hardware. It simulates the GUI experience and always returns a demo alkalinity value (7.5 dKH) for demonstration purposes.

dashboard.html: the main GUI dashboard used by both the live and demo applications.

README.md: this document.

.gitignore: configuration for files and folders excluded from version control.

The live version of the Flask app (app.py), which controls physical hardware on the Raspberry Pi, is not included in this public repository for security and safety reasons.

How to Use the Demo
Anyone cloning this repository can run the demo safely on their local machine.

Prerequisites
Python 3.x

Flask

Pillow (for image handling, though not required in demo mode)

Running the Demo
bash
Copy
Edit
pip install flask pillow
python3 demo_app.py
Then open your browser and navigate to:

cpp
Copy
Edit
http://127.0.0.1:5055/
The dashboard will load, and you can interact with it as if it were connected to hardware. Running an Alk Test will always display a simulated result of 7.5 dKH.

Live Deployment (Private)
The full live version of this project runs on a Raspberry Pi and interfaces with:

6 peristaltic pumps

A magnetic stirrer

A PiCamera for automated color detection

Flask web server

Ngrok tunnel for secure remote access via phone

The live version is not included in this public repository to prevent unintended remote control of the hardware.

Planned Future Enhancements
Full implementation of Calcium and Magnesium tests

Improved GUI with live test progress indicators and trends

Integration with a smart power strip (similar to Neptune EB832) for controlling power to additional equipment

Scheduled automatic testing (daily, weekly, etc.)

Remote alerts and notifications

Data export (CSV, JSON) for long-term analysis

Modular refactoring to allow easy integration of additional tests or sensors

Project Goals
This project aims to provide a fully open and customizable alternative to commercial aquarium water testers. By using affordable components and open-source software, this system allows full control over the testing process, reagent usage, and data handling.

It is also designed to be educational, helping others explore automation and data collection in the aquarium hobby.

Disclaimer
This is a personal project and is not affiliated with or endorsed by Neptune Systems or any other commercial vendor. Use of this project and any connected hardware is at your own risk.