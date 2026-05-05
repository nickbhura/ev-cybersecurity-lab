import random
import time
import json
from datetime import datetime
from collections import defaultdict

print("=" * 60)
print("     EV INTRUSION DETECTION SYSTEM v1.0")
print("=" * 60)
print("\n[*] Initializing IDS engine...")
time.sleep(1)

# Known legitimate CAN IDs and their normal frequency (msgs/sec)
BASELINE = {
    0x0CF: {"name": "Battery Voltage",   "freq": 10, "dlc": 8, "range": (0, 100)},
    0x1F4: {"name": "Motor RPM",         "freq": 20, "dlc": 8, "range": (0, 8000)},
    0x2A0: {"name": "Vehicle Speed",     "freq": 20, "dlc": 8, "range": (0, 200)},
    0x305: {"name": "State of Charge",   "freq": 1,  "dlc": 8, "range": (0, 100)},
    0x42F: {"name": "Door Status",       "freq": 1,  "dlc": 1, "range": (0, 15)},
    0x380: {"name": "Brake Pressure",    "freq": 50, "dlc": 8, "range": (0, 255)},
    0x4B0: {"name": "Steering Angle",    "freq": 50, "dlc": 8, "range": (0, 255)},
}

# Alert levels
ALERT_LEVELS = {
    "INFO":     "ℹ",
    "LOW":      "⚠",
    "MEDIUM":   "🔶",
    "HIGH":     "🔴",
    "CRITICAL": "💀"
}

alerts = []
stats = {"total": 0, "normal": 0, "suspicious": 0, "blocked": 0}
id_frequency = defaultdict(list)

def generate_alert(level, rule, can_id, details):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    alert = {
        "time": timestamp,
        "level": level,
        "rule": rule,
        "can_id": hex(can_id),
        "details": details
    }
    alerts.append(alert)
    icon = ALERT_LEVELS[level]
    print(f"  {icon} [{level:<8}] {timestamp} | {rule}")
    print(f"           CAN ID: {hex(can_id)} | {details}")

def analyze_frame(can_id, data, dlc, timestamp):
    stats["total"] += 1
    suspicious = False

    # Rule 1: Unknown CAN ID
    if can_id not in BASELINE:
        if random.random() > 0.7:  # Not every unknown is malicious
            generate_alert("MEDIUM", "UNKNOWN_CAN_ID",
                can_id, f"CAN ID {hex(can_id)} not in baseline - possible injection")
            suspicious = True

    else:
        baseline = BASELINE[can_id]

        # Rule 2: Wrong DLC
        if dlc != baseline["dlc"]:
            generate_alert("HIGH", "DLC_MISMATCH",
                can_id, f"Expected DLC={baseline['dlc']} got DLC={dlc} - possible fuzzing")
            suspicious = True

        # Rule 3: Frequency anomaly
        now = time.time()
        id_frequency[can_id].append(now)
        id_frequency[can_id] = [t for t in id_frequency[can_id] if now - t < 1.0]
        actual_freq = len(id_frequency[can_id])
        expected_freq = baseline["freq"]

        if actual_freq > expected_freq * 3:
            generate_alert("HIGH", "FREQUENCY_ANOMALY",
                can_id, f"Frequency {actual_freq}/s vs baseline {expected_freq}/s - possible DoS")
            suspicious = True

        # Rule 4: Value out of range
        if data and len(data) > 0:
            value = data[0]
            min_val, max_val = baseline["range"]
            if value < min_val or value > max_val:
                generate_alert("MEDIUM", "VALUE_OUT_OF_RANGE",
                    can_id, f"Value {value} outside normal range [{min_val}-{max_val}]")
                suspicious = True

    # Rule 5: Replay detection - same exact frame seen before
    frame_hash = hash((can_id, tuple(data)))
    if hasattr(analyze_frame, 'seen_frames'):
        if frame_hash in analyze_frame.seen_frames:
            analyze_frame.seen_frames[frame_hash] += 1
            if analyze_frame.seen_frames[frame_hash] > 3:
                generate_alert("CRITICAL", "REPLAY_ATTACK",
                    can_id, f"Identical frame seen {analyze_frame.seen_frames[frame_hash]}x - replay attack detected!")
                suspicious = True
        else:
            analyze_frame.seen_frames[frame_hash] = 1
    else:
        analyze_frame.seen_frames = {frame_hash: 1}

    if suspicious:
        stats["suspicious"] += 1
    else:
        stats["normal"] += 1

    return not suspicious

# Generate traffic scenarios
def generate_normal_traffic():
    can_id = random.choice(list(BASELINE.keys()))
    dlc = BASELINE[can_id]["dlc"]
    data = [random.randint(0, 50) for _ in range(dlc)]
    return can_id, data, dlc

def generate_fuzzing_attack():
    can_id = random.randint(0x000, 0x7FF)
    dlc = random.randint(1, 8)
    data = [random.randint(0, 255) for _ in range(dlc)]
    return can_id, data, dlc

def generate_replay_attack():
    can_id = 0x42F  # Door status
    data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    dlc = 8
    return can_id, data, dlc

def generate_injection_attack():
    can_id = random.choice(list(BASELINE.keys()))
    dlc = BASELINE[can_id]["dlc"]
    data = [random.randint(200, 255) for _ in range(dlc)]  # Out of range
    return can_id, data, dlc

def generate_dos_attack():
    can_id = 0x380  # Brake pressure - flood this
    dlc = 8
    data = [random.randint(0, 50) for _ in range(dlc)]
    return can_id, data, dlc

# Run scenarios
scenarios = [
    ("Normal driving traffic",    generate_normal_traffic,   15, False),
    ("Fuzzing attack",            generate_fuzzing_attack,   10, True),
    ("Normal traffic resumes",    generate_normal_traffic,   10, False),
    ("CAN injection attack",      generate_injection_attack, 8,  True),
    ("Replay attack",             generate_replay_attack,    6,  True),
    ("DoS flood on brake ECU",    generate_dos_attack,       15, True),
    ("Normal traffic resumes",    generate_normal_traffic,   10, False),
]

print("[*] Starting traffic analysis...\n")

for scenario_name, generator, count, is_attack in scenarios:
    print(f"\n{'─' * 60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'─' * 60}")
    time.sleep(0.3)

    for i in range(count):
        can_id, data, dlc = generator()
        analyze_frame(can_id, data, dlc, time.time())
        if is_attack:
            time.sleep(0.05)
        else:
            time.sleep(0.1)

# Final report
print(f"\n{'=' * 60}")
print(f"  IDS SESSION REPORT")
print(f"{'=' * 60}")
print(f"""
  Frames analyzed:  {stats['total']}
  Normal:           {stats['normal']}
  Suspicious:       {stats['suspicious']}
  Detection rate:   {stats['suspicious']/max(stats['total'],1)*100:.1f}%

  Alerts by severity:
""")

severity_counts = defaultdict(int)
for alert in alerts:
    severity_counts[alert['level']] += 1

for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
    count = severity_counts[level]
    bar = "█" * count
    print(f"  {level:<10} {bar} ({count})")

print(f"""
  Rules triggered:
""")
rule_counts = defaultdict(int)
for alert in alerts:
    rule_counts[alert['rule']] += 1
for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
    print(f"  {rule:<30} {count} alerts")

print(f"\n{'=' * 60}")
print(f"  [*] IDS running - protecting your EV network")
print(f"{'=' * 60}\n")
