import asyncio
import websockets
import json
import random
import time
from datetime import datetime

CHARGER_ID = "EV-CHARGER-001"
SERVER = f"ws://localhost:9000/{CHARGER_ID}"

async def run_charger():
    print("=" * 55)
    print("     OCPP CHARGE POINT SIMULATOR")
    print("=" * 55)
    print(f"\n[*] Charger ID: {CHARGER_ID}")
    print(f"[*] Connecting to {SERVER}\n")

    async with websockets.connect(SERVER) as ws:
        print("[+] Connected to CSMS!\n")

        async def send(action, payload):
            msg_id = str(random.randint(1000, 9999))
            message = [2, msg_id, action, payload]
            await ws.send(json.dumps(message))
            response = json.loads(await ws.recv())
            print(f"  << Server response: {json.dumps(response[2], indent=2)}")
            return response[2]

        # Step 1: Boot notification
        print("[1] Sending BootNotification...")
        await send("BootNotification", {
            "chargePointModel": "EV-HACKLAB-3000",
            "chargePointVendor": "HackLab Industries",
            "firmwareVersion": "v1.3.3.7"
        })
        await asyncio.sleep(1)

        # Step 2: Authorize a card
        print("\n[2] Authorizing RFID card...")
        card = f"CARD-{random.randint(1000,9999)}"
        print(f"  Using card ID: {card}")
        await send("Authorize", {"idTag": card})
        await asyncio.sleep(1)

        # Step 3: Start charging
        print("\n[3] Starting charging session...")
        meter_start = random.randint(1000, 5000)
        await send("StartTransaction", {
            "connectorId": 1,
            "idTag": card,
            "meterStart": meter_start,
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(1)

        # Step 4: Send meter values
        print("\n[4] Sending meter values (simulating charging)...")
        for i in range(3):
            meter_start += random.randint(500, 1500)
            await send("MeterValues", {
                "connectorId": 1,
                "transactionId": 1337,
                "meterValue": [{
                    "timestamp": datetime.utcnow().isoformat(),
                    "sampledValue": [{"value": str(meter_start), "unit": "Wh"}]
                }]
            })
            await asyncio.sleep(1)

        # Step 5: Stop charging
        print("\n[5] Stopping charging session...")
        await send("StopTransaction", {
            "transactionId": 1337,
            "meterStop": meter_start,
            "meterStart": meter_start - 3000,
            "timestamp": datetime.utcnow().isoformat()
        })

        print("\n[+] Charging session complete!")

asyncio.run(run_charger())
