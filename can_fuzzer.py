import can
import time
import random

bus = can.interface.Bus(channel='test', interface='virtual')

print("=== EV CAN Bus Fuzzer ===")
print("Sending random frames across all CAN IDs...\n")
print(f"{'ID':<10} {'Data':<20} {'Attempt'}")
print("-" * 45)

attempt = 0

try:
    while True:
        can_id = random.randint(0x000, 0x7FF)
        dlc = random.randint(1, 8)
        data = [random.randint(0, 255) for _ in range(dlc)]
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        bus.send(msg)
        attempt += 1
        print(f"0x{can_id:03X}      {bytes(data).hex():<20} #{attempt}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print(f"\nFuzzing stopped. Total frames sent: {attempt}")
    bus.shutdown()
