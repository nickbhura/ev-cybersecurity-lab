import can
import time
import random

bus = can.interface.Bus(channel='test', interface='virtual')

print("=== CAN Bus Sender ===")
print("Sending fake vehicle data...\n")

# Simulated EV CAN IDs
can_ids = {
    0x0CF: "Battery Voltage",
    0x1F4: "Motor RPM",
    0x2A0: "Vehicle Speed",
    0x305: "State of Charge",
    0x42F: "Door Status",
}

try:
    while True:
        for can_id, label in can_ids.items():
            data = [random.randint(0, 255) for _ in range(8)]
            msg = can.Message(
                arbitration_id=can_id,
                data=data,
                is_extended_id=False
            )
            bus.send(msg)
            print(f"Sent [{label}] ID: {hex(can_id)} Data: {bytes(data).hex()}")
            time.sleep(0.5)
except KeyboardInterrupt:
    print("\nSender stopped.")
    bus.shutdown()
