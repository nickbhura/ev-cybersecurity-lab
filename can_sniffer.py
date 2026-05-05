import can
import time

# Virtual bus - simulates a CAN network in pure Python
bus = can.interface.Bus(channel='test', interface='virtual')

print("=== EV CAN Bus Sniffer ===")
print("Listening for messages... (Ctrl+C to stop)\n")

try:
    while True:
        msg = bus.recv(timeout=1.0)
        if msg:
            print(f"ID: {hex(msg.arbitration_id):<8} "
                  f"DLC: {msg.dlc}  "
                  f"Data: {msg.data.hex()}")
except KeyboardInterrupt:
    print("\nSniffer stopped.")
    bus.shutdown()
