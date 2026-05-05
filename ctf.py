import hashlib
import random
import time
import base64
import json

print("=" * 60)
print("   DEF CON CAR HACKING VILLAGE - CTF SIMULATOR")
print("=" * 60)
print("\n[*] Welcome to the EV Security CTF")
print("[*] Find the flags hidden in each challenge")
print("[*] Format: FLAG{...}\n")
time.sleep(1)

score = 0
solved = []

def check_flag(challenge, user_input, correct_flag, points):
    global score
    if user_input.strip() == correct_flag:
        print(f"\n  ✓ CORRECT! +{points} points")
        score += points
        solved.append(challenge)
        return True
    else:
        print(f"\n  ✗ Wrong flag. Try again.")
        return False

def banner(title, points, difficulty):
    print(f"\n{'═' * 60}")
    print(f"  CHALLENGE: {title}")
    print(f"  Points:    {points}  |  Difficulty: {difficulty}")
    print(f"{'═' * 60}\n")

# ─────────────────────────────────────────────
# CHALLENGE 1: CAN Bus Basics
# ─────────────────────────────────────────────
banner("CAN Bus Decoded", 100, "EASY")
print("""
  You captured this CAN frame from a vehicle:

  ID: 0x042F  DLC: 8  Data: 46 4C 41 47 7B 43 41 4E 7D

  The door status ECU sends ASCII encoded messages
  when a security researcher is nearby.

  Decode the data bytes from hex to ASCII to get the flag.

  Hint: Each byte is a character. 0x46 = 'F'
""")

while True:
    answer = input("  Enter flag: ").strip()
    # 46 4C 41 47 7B 43 41 4E 7D = FLAG{CAN}
    if check_flag("CAN Bus Decoded", answer, "FLAG{CAN}", 100):
        break
    retry = input("  Try again? (y/n): ")
    if retry.lower() != 'y':
        print("  Skipping... FLAG{CAN}")
        break

# ─────────────────────────────────────────────
# CHALLENGE 2: OBD-II PID Analysis
# ─────────────────────────────────────────────
banner("OBD-II Speed Trap", 150, "EASY")
print("""
  A vehicle responded to PID 0x0D (Vehicle Speed) with:

  Response bytes: [0x00, 0x00, 0x00, 0x5A]

  OBD-II formula for Vehicle Speed PID 0x0D:
  Speed (km/h) = byte[3]

  What is the vehicle speed in km/h?
  Format your answer as: FLAG{speed_kmh}
  Example: if speed is 42 km/h, answer is FLAG{42}
""")

while True:
    answer = input("  Enter flag: ").strip()
    # 0x5A = 90
    if check_flag("OBD-II Speed Trap", answer, "FLAG{90}", 150):
        break
    retry = input("  Try again? (y/n): ")
    if retry.lower() != 'y':
        print("  Skipping... FLAG{90}")
        break

# ─────────────────────────────────────────────
# CHALLENGE 3: UDS Security Access
# ─────────────────────────────────────────────
banner("ECU Lockpick", 250, "MEDIUM")
print("""
  You sent a UDS SecurityAccess request (0x27)
  to the Battery Management System and got this seed:

  Seed: 0x1337

  You reverse engineered the ECU firmware and found
  the key algorithm:

  key = (seed XOR 0xFF00) + 0x42

  Calculate the key and submit as: FLAG{0xKEY}
  Use uppercase hex. Example: FLAG{0x1234}
""")

while True:
    answer = input("  Enter flag: ").strip()
    # (0x1337 XOR 0xFF00) + 0x42 = 0xEC37 + 0x42 = 0xEC79
    seed = 0x1337
    key = (seed ^ 0xFF00) + 0x42
    correct = f"FLAG{{{hex(key).upper().replace('X','x')}}}"
    if check_flag("ECU Lockpick", answer, correct, 250):
        break
    retry = input("  Try again? (y/n): ")
    if retry.lower() != 'y':
        print(f"  Skipping... {correct}")
        break

# ─────────────────────────────────────────────
# CHALLENGE 4: OCPP Auth Bypass
# ─────────────────────────────────────────────
banner("Free Juice", 300, "MEDIUM")
print("""
  You intercepted this OCPP Authorize request:

  ["Authorize", {"idTag": "CARD-9999"}]

  The server responded:
  {"idTagInfo": {"status": "Accepted"}}

  You noticed the server accepts ANY idTag without
  checking against a whitelist.

  The hidden flag is encoded in the server's
  response headers:

  X-Debug-Flag: RkxBR3tGUkVFX0NIQVJHSU5HfQ==

  Decode the base64 string to get the flag.
""")

while True:
    answer = input("  Enter flag: ").strip()
    # base64 decode of RkxBR3tGUkVFX0NIQVJHSU5HfQ== = FLAG{FREE_CHARGING}
    if check_flag("Free Juice", answer, "FLAG{FREE_CHARGING}", 300):
        break
    retry = input("  Try again? (y/n): ")
    if retry.lower() != 'y':
        print("  Skipping... FLAG{FREE_CHARGING}")
        break

# ─────────────────────────────────────────────
# CHALLENGE 5: V2G Certificate
# ─────────────────────────────────────────────
banner("Rogue Charger", 400, "HARD")
print("""
  You captured a V2G TLS certificate from a
  suspicious charging station.

  Certificate details:
  Subject:    CN=SECC-EVIL-001
  Issuer:     CN=V2G-Root-CA
  Serial:     0xDEADBEEF
  Not After:  2099-12-31

  The certificate's SHA256 fingerprint is:
  de:ad:be:ef:ca:fe:ba:be:00:11:22:33:44:55:66:77

  A legitimate charger's serial number is NEVER
  above 0xCAFE0000.

  This serial is suspicious. Convert 0xDEADBEEF
  to decimal and submit as: FLAG{decimal_value}
""")

while True:
    answer = input("  Enter flag: ").strip()
    # 0xDEADBEEF = 3735928559
    if check_flag("Rogue Charger", answer, "FLAG{3735928559}", 400):
        break
    retry = input("  Try again? (y/n): ")
    if retry.lower() != 'y':
        print("  Skipping... FLAG{3735928559}")
        break

# ─────────────────────────────────────────────
# CHALLENGE 6: CAN Replay
# ─────────────────────────────────────────────
banner("Ghost Driver", 500, "HARD")
print("""
  You recorded this CAN sequence that unlocks
  all doors on a 2024 EV:

  Frame 1: ID=0x42F Data=AA BB CC DD 01 00 00 00
  Frame 2: ID=0x42F Data=AA BB CC DD 02 00 00 00
  Frame 3: ID=0x42F Data=AA BB CC DD 03 00 00 00

  The first 4 bytes (AA BB CC DD) are a rolling
  counter that increments each ignition cycle.

  Current counter value captured: 0xAABBCCDD

  If the counter increments by 0x11223344 each
  cycle, what is the NEXT counter value?

  Submit as: FLAG{0xNEXTVALUE} in uppercase hex.
""")

while True:
    answer = input("  Enter flag: ").strip()
    # 0xAABBCCDD + 0x11223344 = 0xBBDE0021
    result = (0xAABBCCDD + 0x11223344) & 0xFFFFFFFF
    correct = f"FLAG{{{hex(result).upper().replace('X','x')}}}"
    if check_flag("Ghost Driver", answer, correct, 500):
        break
    retry = input("  Try again? (y/n): ")
    if retry.lower() != 'y':
        print(f"  Skipping... {correct}")
        break

# ─────────────────────────────────────────────
# FINAL SCORE
# ─────────────────────────────────────────────
print(f"\n{'=' * 60}")
print(f"  CTF COMPLETE - FINAL RESULTS")
print(f"{'=' * 60}")
print(f"""
  Player:    bhurasingh
  Score:     {score} / 1700 points
  Solved:    {len(solved)} / 6 challenges
  Rank:      {'ELITE' if score >= 1500 else 'ADVANCED' if score >= 1000 else 'INTERMEDIATE' if score >= 500 else 'BEGINNER'}
""")

for ch in solved:
    print(f"  ✓ {ch}")

print(f"""
  Next step: Try real CTF challenges at
  - carhackingvillage.com
  - ctftime.org (search 'automotive')
  - DEF CON Car Hacking Village archives
""")
print(f"{'=' * 60}\n")
