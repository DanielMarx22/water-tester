import lgpio
import time

chip = lgpio.gpiochip_open(0)
pin = 17

# Set relay OFF initially (HIGH for active-low)
lgpio.gpio_claim_output(chip, pin, 1)

try:
    while True:
        lgpio.gpio_write(chip, pin, 0)  # ON
        print("Relay ON")
        time.sleep(1)

        lgpio.gpio_write(chip, pin, 1)  # OFF
        print("Relay OFF")
        time.sleep(1)

except KeyboardInterrupt:
    lgpio.gpio_write(chip, pin, 1)
    lgpio.gpiochip_close(chip)
    print("Exiting...")
