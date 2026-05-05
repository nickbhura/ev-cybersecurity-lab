import can
import json
import time
import threading

# Single bus instance
bus = can.interface.Bus(channel='test', interface='virtual')
recorded = []

def send_traffic():
    import random
    sender = can.interface.Bus(channel='test', interface='virtual')
    ids = [0x0CF, 0x1F4, 0x2A0, 0x305, 0x42F]
    for _ in range(20):
        msg = can.Message(
            arbitration_id=random.choice(ids),
            data=[random.randint(0,255) for _ in range(8)],
            is_extended_id=False
        )
        sender.send(msg)
        time.sleep(0.2)
    sender.shutdown()

print("=== CAN Replay Recorder ===")
print("Recording for 5 seconds...\n")

# Send and record at same time
t = threading.Thread(target=send_traffic)
t.start()

start = time.time()
while time.time() - start < 5:
    msg = bus.recv(timeout=0.5)
    if msg:
        recorded.append({
            'id': msg.arbitration_id,
            'data': list(msg.data),
        })
        print(f"Captured ID: {hex(msg.arbitration_id)} Data: {msg.data.hex()}")

t.join()
with open('capture.json', 'w') as f:
    json.dump(recorded, f)

print(f"\nRecorded {len(recorded)} frames to capture.json")
bus.shutdown()
