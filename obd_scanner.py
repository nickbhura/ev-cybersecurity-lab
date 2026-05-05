import can
import time
import random

bus = can.interface.Bus(channel='test', interface='virtual')

PIDS = {
    0x04: ("Engine Load",        "%",    lambda v: v[0] / 2.55),
    0x05: ("Coolant Temp",       "°C",   lambda v: v[0] - 40),
    0x0C: ("Engine RPM",         "RPM",  lambda v: ((v[0] * 256) + v[1]) / 4),
    0x0D: ("Vehicle Speed",      "km/h", lambda v: v[0]),
    0x0F: ("Intake Air Temp",    "°C",   lambda v: v[0] - 40),
    0x11: ("Throttle Position",  "%",    lambda v: v[0] / 2.55),
    0x2F: ("Fuel Level",         "%",    lambda v: v[0] / 2.55),
    0x5C: ("Oil Temperature",    "°C",   lambda v: v[0] - 40),
}

EV_PIDS = {
    0xE1: ("Battery Voltage",    "V",    lambda v: ((v[0] * 256) + v[1]) / 10),
    0xE2: ("State of Charge",    "%",    lambda v: v[0] / 2.55),
    0xE3: ("Motor Temp",         "°C",   lambda v: v[0] - 40),
    0xE4: ("Regen Brake Power",  "kW",   lambda v: v[0] / 2),
}

def simulate_response(pid):
    return [random.randint(0, 255) for _ in range(4)]

print("=" * 50)
print("      EV OBD-II DIAGNOSTIC SCANNER")
print("=" * 50)
print(f"\n{'PID':<8} {'Parameter':<22} {'Value':<12} {'Unit'}")
print("-" * 50)

all_pids = {**PIDS, **EV_PIDS}

try:
    while True:
        for pid, (name, unit, formula) in all_pids.items():
            response = simulate_response(pid)
            try:
                value = formula(response)
                print(f"0x{pid:02X}     {name:<22} {value:<12.1f} {unit}")
            except:
                pass
            time.sleep(0.3)
        print("-" * 50)
        print("[ Scan complete - rescanning in 3s... ]")
        print("-" * 50)
        time.sleep(3)
except KeyboardInterrupt:
    print("\nScanner stopped.")
    bus.shutdown()
