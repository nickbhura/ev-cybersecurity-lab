import random
import time
from collections import defaultdict
from datetime import datetime

print("=" * 60)
print("     EV INTRUSION DETECTION SYSTEM v2.0")
print("      NOW WITH BEHAVIORAL ANALYSIS")
print("=" * 60)

BASELINE = {
    0x0CF: {"name": "Battery Voltage",   "freq": 10, "dlc": 8, "range": (0, 100)},
    0x1F4: {"name": "Motor RPM",         "freq": 20, "dlc": 8, "range": (0, 8000)},
    0x2A0: {"name": "Vehicle Speed",     "freq": 20, "dlc": 8, "range": (0, 200)},
    0x305: {"name": "State of Charge",   "freq": 1,  "dlc": 8, "range": (0, 100)},
    0x42F: {"name": "Door Status",       "freq": 1,  "dlc": 1, "range": (0, 15)},
    0x380: {"name": "Brake Pressure",    "freq": 50, "dlc": 8, "range": (0, 255)},
    0x4B0: {"name": "Steering Angle",    "freq": 50, "dlc": 8, "range": (0, 255)},
}

# NEW: UDS service IDs to watch for
UDS_SERVICES = {
    0x10: "DiagnosticSessionControl",
    0x11: "ECUReset",
    0x22: "ReadDataByID",
    0x27: "SecurityAccess",
    0x2E: "WriteDataByID",
    0x34: "RequestDownload",
    0x36: "TransferData",
}

alerts = []
stats = {"total": 0, "normal": 0, "suspicious": 0}
id_frequency = defaultdict(list)
id_sequence = []  # NEW: track sequence of IDs
uds_sessions = defaultdict(list)  # NEW: track UDS activity per address
seen_frames = defaultdict(int)  # NEW: replay detection

def generate_alert(level, rule, details):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    icons = {"CRITICAL": "💀", "HIGH": "🔴", "MEDIUM": "🔶", "LOW": "⚠"}
    icon = icons.get(level, "ℹ")
    alerts.append({"level": level, "rule": rule})
    print(f"  {icon} [{level:<8}] {rule}")
    print(f"           {details}")

def analyze_frame(can_id, data, dlc):
    stats["total"] += 1
    suspicious = False
    now = time.time()

    # Track sequence
    id_sequence.append(can_id)
    if len(id_sequence) > 100:
        id_sequence.pop(0)

    # Rule 1: Unknown CAN ID
    if can_id not in BASELINE:
        # NEW: Check if it looks like a UDS request
        if dlc >= 2 and len(data) >= 2:
            service = data[1] if len(data) > 1 else 0
            if service in UDS_SERVICES:
                generate_alert("CRITICAL", "UDS_PROBE_DETECTED",
                    f"UDS service 0x{service:02X} ({UDS_SERVICES[service]}) sent to ECU 0x{can_id:03X}")
                suspicious = True
                uds_sessions[can_id].append(service)
            else:
                if random.random() > 0.6:
                    generate_alert("MEDIUM", "UNKNOWN_CAN_ID",
                        f"Unknown ID 0x{can_id:03X} - possible injection or scan")
                    suspicious = True
    else:
        baseline = BASELINE[can_id]

        # Rule 2: DLC mismatch
        if dlc != baseline["dlc"]:
            generate_alert("HIGH", "DLC_MISMATCH",
                f"ID 0x{can_id:03X} expected DLC={baseline['dlc']} got DLC={dlc}")
            suspicious = True

        # Rule 3: Frequency anomaly
        id_frequency[can_id].append(now)
        id_frequency[can_id] = [t for t in id_frequency[can_id] if now - t < 1.0]
        actual_freq = len(id_frequency[can_id])
        if actual_freq > baseline["freq"] * 3:
            generate_alert("HIGH", "FREQUENCY_ANOMALY",
                f"ID 0x{can_id:03X} at {actual_freq}/s vs baseline {baseline['freq']}/s")
            suspicious = True

        # Rule 4: Value out of range
        if data and len(data) > 0:
            value = data[0]
            min_val, max_val = baseline["range"]
            if value < min_val or value > max_val:
                generate_alert("MEDIUM", "VALUE_OUT_OF_RANGE",
                    f"ID 0x{can_id:03X} value {value} outside [{min_val}-{max_val}]")
                suspicious = True

    # Rule 5: Replay detection
    frame_hash = (can_id, tuple(data))
    seen_frames[frame_hash] += 1
    if seen_frames[frame_hash] > 3:
        generate_alert("CRITICAL", "REPLAY_ATTACK",
            f"ID 0x{can_id:03X} identical frame seen {seen_frames[frame_hash]}x")
        suspicious = True

    # NEW Rule 6: UDS enumeration pattern
    if len(id_sequence) >= 20:
        unique_ids = len(set(id_sequence[-20:]))
        if unique_ids > 12:
            generate_alert("HIGH", "ECU_ENUMERATION",
                f"High ID diversity detected: {unique_ids} unique IDs in last 20 frames - possible scan")
            suspicious = True

    # NEW Rule 7: SecurityAccess sequence
    for addr, services in uds_sessions.items():
        if 0x27 in services and len(services) >= 3:
            generate_alert("CRITICAL", "SECURITY_ACCESS_ATTEMPT",
                f"ECU 0x{addr:03X} received SecurityAccess after {len(services)} UDS probes - attack in progress!")
            uds_sessions[addr] = []  # Reset to avoid repeat alerts
            suspicious = True

    # NEW Rule 8: Scan pattern - sequential IDs
    if len(id_sequence) >= 10:
        recent = id_sequence[-10:]
        diffs = [abs(recent[i+1] - recent[i]) for i in range(len(recent)-1)]
        if all(d <= 2 for d in diffs) and len(set(recent)) > 5:
            generate_alert("HIGH", "SEQUENTIAL_SCAN",
                f"Sequential CAN ID scanning detected - possible fuzzer/scanner")
            suspicious = True

    if suspicious:
        stats["suspicious"] += 1
    else:
        stats["normal"] += 1

# Simulate the same attack chain as before
scenarios = [
    ("Normal driving",         [(random.choice(list(BASELINE.keys())),
                                 [random.randint(0,50) for _ in range(8)], 8)
                                for _ in range(15)], False),
    ("UDS ECU scan",           [(0x7E0 + i//3, [0x02, 0x10, 0x01, 0,0,0,0,0], 8)
                                for i in range(12)], True),
    ("SecurityAccess probe",   [(0x7E0, [0x02, 0x27, 0x01, 0,0,0,0,0], 8)
                                for _ in range(5)], True),
    ("CAN fuzzing",            [(random.randint(0,0x7FF),
                                 [random.randint(0,255) for _ in range(random.randint(1,8))],
                                 random.randint(1,8))
                                for _ in range(15)], True),
    ("Replay attack",          [(0x42F, [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF], 8)
                                for _ in range(6)], True),
    ("Normal traffic resumes", [(random.choice(list(BASELINE.keys())),
                                 [random.randint(0,50) for _ in range(8)], 8)
                                for _ in range(10)], False),
]

for scenario_name, frames, is_attack in scenarios:
    print(f"\n{'─' * 60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'─' * 60}")
    for can_id, data, dlc in frames:
        analyze_frame(can_id, data, dlc)
        time.sleep(0.05)

# Results
from collections import defaultdict as dd
severity_counts = defaultdict(int)
rule_counts = defaultdict(int)
for a in alerts:
    severity_counts[a['level']] += 1
    rule_counts[a['rule']] += 1

print(f"\n{'=' * 60}")
print(f"  IDS v2.0 RESULTS")
print(f"{'=' * 60}")
print(f"""
  Frames analyzed:  {stats['total']}
  Normal:           {stats['normal']}
  Suspicious:       {stats['suspicious']}
  Detection rate:   {stats['suspicious']/max(stats['total'],1)*100:.1f}%
""")

for level in ["CRITICAL", "HIGH", "MEDIUM"]:
    count = severity_counts[level]
    bar = "█" * count
    print(f"  {level:<10} {bar} ({count})")

print(f"\n  Rules triggered:")
for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
    print(f"  {rule:<35} {count}")

print(f"\n  NEW rules that caught the attack:")
new_rules = ["UDS_PROBE_DETECTED", "ECU_ENUMERATION",
             "SECURITY_ACCESS_ATTEMPT", "SEQUENTIAL_SCAN"]
for rule in new_rules:
    count = rule_counts.get(rule, 0)
    print(f"  {'✓' if count > 0 else '✗'} {rule:<35} {count} alerts")

print(f"\n{'=' * 60}\n")
