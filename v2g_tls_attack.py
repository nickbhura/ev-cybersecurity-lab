import ssl
import socket
import hashlib
import random
import time
import threading
from datetime import datetime, timedelta

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import ipaddress
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

print("=" * 60)
print("     V2G TLS CERTIFICATE ATTACK LAB")
print("=" * 60)
print()

# Phase 1: Generate rogue CA and certificates
print("─" * 60)
print("PHASE 1: GENERATING ROGUE PKI INFRASTRUCTURE")
print("─" * 60)

if CRYPTO_OK:
    print("\n[*] Generating rogue Root CA...")
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "V2G-Root-CA"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Rogue Charging Authority"),
        x509.NameAttribute(NameOID.COUNTRY_NAME, "XX"),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    print(f"  [+] Rogue CA generated")
    print(f"      Subject: {ca_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
    print(f"      Valid:   {ca_cert.not_valid_before_utc} to {ca_cert.not_valid_after_utc}")

    print("\n[*] Generating rogue SECC (charger) certificate...")
    secc_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    secc_cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "SECC-ROGUE-001"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Evil Charging Co"),
        ]))
        .issuer_name(ca_name)
        .public_key(secc_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.IPv4Address('127.0.0.1')),
        ]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    print(f"  [+] Rogue SECC cert generated")
    print(f"      Subject: {secc_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
    print(f"      Signed by: Rogue CA (not trusted V2G Root)")

    # Save certs
    with open("/tmp/rogue_ca.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
    with open("/tmp/rogue_secc.pem", "wb") as f:
        f.write(secc_cert.public_bytes(serialization.Encoding.PEM))
    with open("/tmp/rogue_secc.key", "wb") as f:
        f.write(secc_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))
    print(f"\n  [+] Certificates saved to /tmp/")
else:
    print("  [!] Cryptography library issue - showing simulation")

time.sleep(1)

# Phase 2: Simulate EVCC validation scenarios
print(f"\n{'─' * 60}")
print("PHASE 2: TESTING EVCC CERTIFICATE VALIDATION")
print("─" * 60)
print("\n[*] Simulating different EV implementations...\n")

evcc_implementations = [
    {
        "name": "Tesla Model 3 (simulated)",
        "checks_chain": True,
        "checks_expiry": True,
        "checks_revocation": False,
        "checks_hostname": True,
    },
    {
        "name": "Nissan Leaf (simulated)",
        "checks_chain": False,
        "checks_expiry": True,
        "checks_revocation": False,
        "checks_hostname": False,
    },
    {
        "name": "Generic OEM Stack (simulated)",
        "checks_chain": False,
        "checks_expiry": False,
        "checks_revocation": False,
        "checks_hostname": False,
    },
    {
        "name": "Reference Implementation (simulated)",
        "checks_chain": True,
        "checks_expiry": True,
        "checks_revocation": True,
        "checks_hostname": True,
    },
]

for ev in evcc_implementations:
    print(f"  Target: {ev['name']}")
    vulnerable = False

    checks = [
        ("Certificate chain validation", ev["checks_chain"]),
        ("Certificate expiry check",     ev["checks_expiry"]),
        ("Revocation check (OCSP/CRL)",  ev["checks_revocation"]),
        ("Hostname/IP verification",     ev["checks_hostname"]),
    ]

    for check_name, passes in checks:
        status = "✓ passes" if passes else "✗ SKIPS  <- vulnerable"
        if not passes:
            vulnerable = True
        print(f"    {check_name:<35} {status}")

    if vulnerable:
        print(f"    >> RESULT: MitM POSSIBLE with rogue certificate")
    else:
        print(f"    >> RESULT: Secure - rogue cert rejected")
    print()
    time.sleep(0.5)

# Phase 3: MitM simulation
print(f"{'─' * 60}")
print("PHASE 3: MAN-IN-THE-MIDDLE ATTACK SIMULATION")
print("─" * 60)
print("""
  Normal V2G flow:
  EV ----[TLS]----- Charger

  MitM attack:
  EV ----[TLS]---- ATTACKER ----[TLS]---- Charger
                   (rogue cert)  (real cert)

  Attacker can see and modify:
  - Contract certificate (Plug & Charge identity)
  - Charging parameters (power levels)
  - Meter values (billing data)
  - Payment information
""")

time.sleep(1)
print("[*] Simulating MitM interception...\n")

mitm_intercepts = [
    ("ContractAuthenticationReq", "Contract cert extracted", "CRITICAL - identity theft"),
    ("ChargeParameterDiscoveryReq", "Modified EVMaxCurrent 32A -> 200A", "CRITICAL - hardware damage"),
    ("MeteringReceiptReq", "Modified MeterReading 50000 -> 5000 Wh", "HIGH - billing fraud"),
    ("PowerDeliveryReq", "Modified MaxPower 7kW -> 22kW", "HIGH - overload attack"),
]

for msg, intercept, severity in mitm_intercepts:
    time.sleep(0.5)
    print(f"  [{severity}]")
    print(f"  Message:   {msg}")
    print(f"  Modified:  {intercept}")
    print()

# Phase 4: Defense recommendations
print(f"{'─' * 60}")
print("PHASE 4: DEFENSES")
print("─" * 60)
print("""
  [1] Mutual TLS (mTLS)
      Both EV and charger must present valid certificates
      Certificates signed by trusted V2G Root CA only

  [2] Certificate Pinning
      EV hardcodes expected charger cert fingerprint
      Rejects any cert not matching - even valid ones

  [3] OCSP Stapling
      Real-time certificate revocation checking
      Compromised certs blocked immediately

  [4] Message Signing (ISO 15118-20)
      Every V2G message signed with private key
      Tampering detected even if TLS is broken

  [5] Secure Element
      Store private keys in hardware (TPM/HSM)
      Keys never exposed even if software is compromised
""")

print("=" * 60)
print("  P-011 COMPLETE - V2G TLS ATTACK LAB")
print("=" * 60)
print(f"""
  What you built:
  [+] Rogue V2G Certificate Authority
  [+] Rogue SECC (charger) certificate
  [+] EVCC validation weakness analysis
  [+] MitM attack simulation
  [+] Defense recommendations

  Real world impact:
  A vulnerable EV accepting our rogue cert would expose:
  - Driver identity and payment credentials
  - Vehicle location and charging patterns
  - Ability to manipulate power delivery
""")
