import can
import time
import random

bus = can.interface.Bus(channel='test', interface='virtual')

# UDS Service IDs
SERVICES = {
    0x10: "DiagnosticSessionControl",
    0x11: "ECUReset",
    0x14: "ClearDiagnosticInfo",
    0x19: "ReadDTCInfo",
    0x22: "ReadDataByID",
    0x27: "SecurityAccess",
    0x28: "CommunicationControl",
    0x2E: "WriteDataByID",
    0x31: "RoutineControl",
    0x34: "RequestDownload",
    0x36: "TransferData",
    0x37: "RequestTransferExit",
    0x3E: "TesterPresent",
}

# Common ECU addresses in a real car
ECU_ADDRESSES = {
    0x7E0: "Engine ECU",
    0x7E1: "Transmission ECU",
    0x7E2: "ABS/Brake ECU",
    0x7E3: "Airbag ECU",
    0x7E4: "Body Control Module",
    0x7E5: "Battery Management System",
    0x7E6: "Motor Controller",
    0x7E7: "Charging ECU",
    0x7E8: "Instrument Cluster",
    0x7E9: "HVAC ECU",
}

# Common Data Identifiers
DIDS = {
    0xF190: "VIN Number",
    0xF18C: "ECU Serial Number",
    0xF187: "Part Number",
    0xF189: "Software Version",
    0xF197: "System Name",
    0xF1A0: "Calibration ID",
}

def simulate_ecu_response(address, service):
    """Simulate ECU responding - some services randomly supported"""
    if random.random() > 0.3:  # 70% chance ECU responds
        return True
    return False

def simulate_did_response(did):
    """Simulate reading a data identifier"""
    responses = {
        0xF190: "1HGBH41JXMN109186",  # Fake VIN
        0xF18C: f"ECU-{random.randint(10000,99999)}",
        0xF187: f"P/N-{random.randint(1000,9999)}-{random.randint(100,999)}",
        0xF189: f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,99)}",
        0xF197: "EV-CTRL-SYSTEM",
        0xF1A0: f"CAL-{random.randint(1000,9999)}",
    }
    return responses.get(did, "N/A")

print("=" * 60)
print("         UDS ECU NETWORK SCANNER")
print("=" * 60)
print("\n[*] Scanning ECU addresses on CAN network...\n")
time.sleep(1)

live_ecus = []

# Phase 1: ECU Discovery
print("─" * 60)
print("PHASE 1: ECU DISCOVERY")
print("─" * 60)
for address, name in ECU_ADDRESSES.items():
    time.sleep(0.3)
    responding = simulate_ecu_response(address, 0x10)
    status = "✓ ALIVE" if responding else "✗ no response"
    print(f"  {hex(address)}  {name:<25} {status}")
    if responding:
        live_ecus.append((address, name))

print(f"\n[+] Found {len(live_ecus)} live ECUs\n")
time.sleep(1)

# Phase 2: Service Enumeration
print("─" * 60)
print("PHASE 2: SERVICE ENUMERATION")
print("─" * 60)
for address, name in live_ecus:
    print(f"\n  Probing {name} ({hex(address)}):")
    supported = []
    for sid, sname in SERVICES.items():
        time.sleep(0.1)
        if simulate_ecu_response(address, sid):
            print(f"    [+] 0x{sid:02X} {sname}")
            supported.append(sid)
    if not supported:
        print(f"    [-] No services responded")

time.sleep(1)

# Phase 3: Data Extraction
print(f"\n{'─' * 60}")
print("PHASE 3: DATA EXTRACTION (ReadDataByID)")
print("─" * 60)
for address, name in live_ecus[:3]:  # First 3 ECUs
    print(f"\n  Reading DIDs from {name} ({hex(address)}):")
    for did, did_name in DIDS.items():
        time.sleep(0.2)
        value = simulate_did_response(did)
        print(f"    0x{did:04X}  {did_name:<20} = {value}")

# Phase 4: Security Access Check
print(f"\n{'─' * 60}")
print("PHASE 4: SECURITY ACCESS PROBE (0x27)")
print("─" * 60)
print("\n  [*] Requesting seed from each ECU...\n")
for address, name in live_ecus:
    time.sleep(0.3)
    seed = random.randint(0x1000, 0xFFFF)
    print(f"  {name:<25} Seed: 0x{seed:04X}  <- Send key to unlock")

print(f"\n{'=' * 60}")
print("  SCAN COMPLETE")
print(f"{'=' * 60}")
print(f"  Live ECUs found:     {len(live_ecus)}")
print(f"  Services probed:     {len(SERVICES)}")
print(f"  DIDs extracted:      {len(DIDS)}")
print(f"\n  [!] SecurityAccess seeds captured - see Phase 6 to crack them")
print(f"{'=' * 60}\n")

bus.shutdown()
