import time
import random

# Simulated seeds from our UDS scan
SEEDS = {
    "Engine ECU":                0xA469,
    "Transmission ECU":          0xBBEE,
    "ABS/Brake ECU":             0x7D90,
    "Airbag ECU":                0xB129,
    "Battery Management System": 0x93B3,
    "Motor Controller":          0xC0FE,
    "Charging ECU":              0x1533,
    "Instrument Cluster":        0xEBD1,
    "HVAC ECU":                  0xDC3E,
}

# Common weak seed->key algorithms found in real ECUs
def algo_xor(seed):
    """Simple XOR with fixed secret - very common"""
    SECRET = 0x5A5A
    return seed ^ SECRET

def algo_not(seed):
    """Bitwise NOT - seen in cheap ECUs"""
    return (~seed) & 0xFFFF

def algo_shift_xor(seed):
    """Shift then XOR - slightly harder"""
    return ((seed << 1) & 0xFFFF) ^ 0x1234

def algo_add(seed):
    """Add constant - also found in real cars"""
    return (seed + 0x4321) & 0xFFFF

def algo_multiply(seed):
    """Multiply - used in some BMW ECUs"""
    return (seed * 3) & 0xFFFF

ALGORITHMS = {
    "XOR 0x5A5A":       algo_xor,
    "Bitwise NOT":      algo_not,
    "Shift+XOR 0x1234": algo_shift_xor,
    "ADD 0x4321":       algo_add,
    "MULTIPLY x3":      algo_multiply,
}

def verify_key(ecu, seed, key, algo_name):
    """Simulate sending key to ECU and checking response"""
    # In real life: send 0x27 service with key, check for positive response
    # Here we simulate: engine ECU uses XOR, others use various algos
    real_algos = {
        "Engine ECU":                algo_xor,
        "Transmission ECU":          algo_not,
        "ABS/Brake ECU":             algo_shift_xor,
        "Airbag ECU":                algo_xor,
        "Battery Management System": algo_add,
        "Motor Controller":          algo_multiply,
        "Charging ECU":              algo_xor,
        "Instrument Cluster":        algo_not,
        "HVAC ECU":                  algo_shift_xor,
    }
    correct_key = real_algos[ecu](seed)
    return key == correct_key

print("=" * 60)
print("    SECURITY ACCESS BRUTE FORCE ANALYZER")
print("=" * 60)
print("\n[*] Testing known weak algorithms against captured seeds\n")
time.sleep(1)

cracked = []

for ecu, seed in SEEDS.items():
    print(f"─" * 60)
    print(f"TARGET: {ecu}")
    print(f"  Seed: 0x{seed:04X}")
    print(f"  Testing algorithms...")
    
    found = False
    for algo_name, algo_func in ALGORITHMS.items():
        time.sleep(0.3)
        candidate_key = algo_func(seed)
        success = verify_key(ecu, seed, candidate_key, algo_name)
        status = "✓ CRACKED!" if success else "✗ wrong"
        print(f"    [{algo_name:<20}] Key: 0x{candidate_key:04X}  {status}")
        
        if success:
            found = True
            cracked.append((ecu, seed, candidate_key, algo_name))
            break
    
    if not found:
        print(f"    [!] Algorithm unknown - need more seed/key pairs")
    time.sleep(0.2)

print(f"\n{'=' * 60}")
print(f"  RESULTS")
print(f"{'=' * 60}")
print(f"\n  Cracked: {len(cracked)}/{len(SEEDS)} ECUs\n")

for ecu, seed, key, algo in cracked:
    print(f"  ✓ {ecu}")
    print(f"    Seed: 0x{seed:04X}  Key: 0x{key:04X}  Algorithm: {algo}")
    print(f"    >> WRITE ACCESS UNLOCKED - can flash firmware\n")

print(f"{'=' * 60}")
print(f"  [!] IMPACT: Unlocked ECUs accept firmware updates,")
print(f"      parameter writes, and diagnostic commands")
print(f"      without any further authentication.")
print(f"{'=' * 60}\n")
