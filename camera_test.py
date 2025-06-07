import os
import time
from datetime import datetime
import numpy as np
from picamera2 import Picamera2
from PIL import Image

save_dir = "/home/danielmarx/Desktop/CodeStuff/captured_images"
os.makedirs(save_dir, exist_ok=True)
filename = os.path.join(save_dir, f"image_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg")

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": (3280, 2464)})
picam2.configure(config)

picam2.start()
time.sleep(2)
picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})

image = picam2.capture_array()
image = np.ascontiguousarray(image)

Image.fromarray(image).save(filename)
print(f"✅ Saved: {filename}")
