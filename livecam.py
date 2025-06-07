from picamera2 import Picamera2
import cv2
import time

# Initialize camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

picam2.start()
time.sleep(1)

# Loop to show frames
while True:
    frame = picam2.capture_array()
    cv2.imshow("Live Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

# Cleanup
cv2.destroyAllWindows()
picam2.close()
