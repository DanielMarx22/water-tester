import lgpio

# Try to free any stuck pins
PINS_TO_FREE = [17, 18, 27, 22, 23, 24, 5]

h = lgpio.gpiochip_open(0)

for pin in PINS_TO_FREE:
    try:
        lgpio.gpio_free(h, pin)
        print(f"Freed GPIO {pin}")
    except Exception as e:
        print(f"GPIO {pin} not allocated, skipping.")

lgpio.gpiochip_close(h)
