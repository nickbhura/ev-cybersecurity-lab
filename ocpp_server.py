import asyncio
import websockets
import json
from datetime import datetime

connected_chargers = {}

async def handle_charger(websocket):
    try:
        path = websocket.request.path
    except:
        path = "/unknown"
    
    charger_id = path.strip("/") or "unknown"
    connected_chargers[charger_id] = websocket
    print(f"\n[+] Charger connected: {charger_id}")
    print(f"[*] Total chargers online: {len(connected_chargers)}")

    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data[0]
            msg_id = data[1]
            action = data[2] if len(data) > 2 else ""
            payload = data[3] if len(data) > 3 else {}

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] {charger_id} >> {action}")
            print(f"  Payload: {json.dumps(payload, indent=2)}")

            if action == "BootNotification":
                response = [3, msg_id, {
                    "status": "Accepted",
                    "currentTime": datetime.utcnow().isoformat(),
                    "interval": 30
                }]
                print(f"  >> Responding: Accepted")

            elif action == "Heartbeat":
                response = [3, msg_id, {
                    "currentTime": datetime.utcnow().isoformat()
                }]

            elif action == "Authorize":
                id_tag = payload.get("idTag", "")
                response = [3, msg_id, {
                    "idTagInfo": {"status": "Accepted"}
                }]
                print(f"  >> [!] Card '{id_tag}' ACCEPTED - no validation!")

            elif action == "StartTransaction":
                response = [3, msg_id, {
                    "transactionId": 1337,
                    "idTagInfo": {"status": "Accepted"}
                }]
                print(f"  >> Transaction started!")

            elif action == "StopTransaction":
                response = [3, msg_id, {"idTagInfo": {"status": "Accepted"}}]
                print(f"  >> Transaction stopped!")

            elif action == "MeterValues":
                response = [3, msg_id, {}]
                print(f"  >> Meter values logged")

            elif action == "StatusNotification":
                response = [3, msg_id, {}]

            else:
                response = [3, msg_id, {}]

            await websocket.send(json.dumps(response))

    except websockets.exceptions.ConnectionClosed:
        print(f"\n[-] Charger disconnected: {charger_id}")
        connected_chargers.pop(charger_id, None)

async def main():
    print("=" * 55)
    print("     OCPP CHARGING STATION MANAGEMENT SERVER")
    print("=" * 55)
    print("\n[*] Starting server on ws://localhost:9000")
    print("[!] VULNERABILITY: No authentication enabled\n")

    async with websockets.serve(handle_charger, "0.0.0.0", 9000):
        await asyncio.Future()

asyncio.run(main())
