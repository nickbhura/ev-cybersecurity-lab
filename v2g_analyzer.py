import json
import time
import random
import hashlib
from datetime import datetime

print("=" * 60)
print("     V2G / ISO 15118 PROTOCOL ANALYZER")
print("=" * 60)
print("\n[*] Simulating V2G handshake between EV and Charger\n")
print("    EV (EVCC)  <------>  Charger (SECC)")
print("    Electric            Supply Equipment")
print("    Vehicle             Communication")
print("    Comm Controller     Controller\n")
time.sleep(1)

V2G_MESSAGES = [
    {
        "step": 1, "from": "EV", "to": "CHARGER",
        "msg": "SupportedAppProtocolReq",
        "desc": "EV announces supported protocols",
        "payload": {"AppProtocol": [{"ProtocolNamespace": "ISO 15118-2", "Priority": 1}]},
        "vuln": None
    },
    {
        "step": 2, "from": "CHARGER", "to": "EV",
        "msg": "SupportedAppProtocolRes",
        "desc": "Charger selects protocol",
        "payload": {"SchemaID": 1, "ResponseCode": "OK_SuccessfulNegotiation"},
        "vuln": None
    },
    {
        "step": 3, "from": "EV", "to": "CHARGER",
        "msg": "SessionSetupReq",
        "desc": "EV sends its ID to start session",
        "payload": {"EVCCID": "00:1A:2B:3C:4D:5E"},
        "vuln": "EVCC ID sent before TLS - vehicle trackable without consent"
    },
    {
        "step": 4, "from": "CHARGER", "to": "EV",
        "msg": "SessionSetupRes",
        "desc": "Charger assigns session ID",
        "payload": {"ResponseCode": "OK_NewSessionEstablished",
                    "SessionID": hashlib.md5(str(random.random()).encode()).hexdigest()[:16].upper()},
        "vuln": None
    },
    {
        "step": 5, "from": "EV", "to": "CHARGER",
        "msg": "ServiceDiscoveryReq",
        "desc": "EV asks what services charger offers",
        "payload": {"ServiceCategory": "EVCharging"},
        "vuln": None
    },
    {
        "step": 6, "from": "CHARGER", "to": "EV",
        "msg": "ServiceDiscoveryRes",
        "desc": "Charger lists services",
        "payload": {"FreeService": False, "ServiceID": 1},
        "vuln": "FreeService=False not cryptographically enforced"
    },
    {
        "step": 7, "from": "EV", "to": "CHARGER",
        "msg": "ContractAuthenticationReq",
        "desc": "EV presents Plug and Charge certificate",
        "payload": {"GenChallenge": hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]},
        "vuln": "Certificate chain validation often misconfigured in real EVs"
    },
    {
        "step": 8, "from": "CHARGER", "to": "EV",
        "msg": "ContractAuthenticationRes",
        "desc": "Charger validates contract",
        "payload": {"ResponseCode": "OK", "EVSEProcessing": "Finished"},
        "vuln": None
    },
    {
        "step": 9, "from": "EV", "to": "CHARGER",
        "msg": "ChargeParameterDiscoveryReq",
        "desc": "EV self-reports its charging requirements",
        "payload": {"EVMaxVoltage": 400, "EVMaxCurrent": 32},
        "vuln": "CRITICAL: EV self-reports max current - charger trusts without verification"
    },
    {
        "step": 10, "from": "CHARGER", "to": "EV",
        "msg": "PowerDeliveryReq",
        "desc": "Power delivery starts",
        "payload": {"ChargeProgress": "Start", "MaxPower": 22000},
        "vuln": "ChargingProfile not signed - modifiable in transit via MitM"
    },
    {
        "step": 11, "from": "EV", "to": "CHARGER",
        "msg": "MeteringReceiptReq",
        "desc": "EV acknowledges metering data",
        "payload": {"MeterReading": random.randint(10000, 50000),
                    "SigMeterReading": "UNSIGNED"},
        "vuln": "CRITICAL: Meter signature optional - billing fraud possible"
    },
    {
        "step": 12, "from": "EV", "to": "CHARGER",
        "msg": "SessionStopReq",
        "desc": "Session terminated",
        "payload": {"ChargingSession": "Terminate"},
        "vuln": None
    },
]

vulnerabilities = []

for msg in V2G_MESSAGES:
    arrow = ">>>>>>" if msg["from"] == "EV" else "<<<<<<"
    prefix = "EV     " if msg["from"] == "EV" else "CHARGER"
    print(f"[Step {msg['step']:02d}] {prefix} {arrow} {msg['msg']}")
    print(f"         {msg['desc']}")
    if msg["vuln"]:
        print(f"         [!] {msg['vuln']}")
        vulnerabilities.append((msg['step'], msg['msg'], msg['vuln']))
    print()
    time.sleep(0.3)

print("=" * 60)
print("  VULNERABILITY REPORT")
print("=" * 60)
print(f"\n  Messages analyzed:     {len(V2G_MESSAGES)}")
print(f"  Vulnerabilities found: {len(vulnerabilities)}\n")
for step, msg, vuln in vulnerabilities:
    print(f"  [Step {step:02d}] {msg}")
    print(f"           {vuln}\n")
print("=" * 60)
