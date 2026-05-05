import json
import time
import random
import hashlib
from datetime import datetime

print("=" * 60)
print("     EV CLOUD API SECURITY RECON TOOL")
print("=" * 60)
print("\n[*] Target: Generic EV Manufacturer API")
print("[*] Based on real vulnerabilities found in:")
print("    - Nissan Leaf (2016 - no auth on API)")
print("    - Tesla API (various endpoint issues)")
print("    - Honda Connect (hardcoded credentials)")
print()
time.sleep(1)

# Simulated API endpoints discovered through recon
API_ENDPOINTS = [
    {
        "method": "POST",
        "path": "/oauth/token",
        "auth": False,
        "desc": "Authentication endpoint",
        "params": {"username": "user@example.com", "password": "****"},
        "vuln": None,
        "severity": None
    },
    {
        "method": "GET",
        "path": "/v1/vehicles",
        "auth": True,
        "desc": "List all vehicles for account",
        "params": {},
        "vuln": None,
        "severity": None
    },
    {
        "method": "GET",
        "path": "/v1/vehicles/{vin}/location",
        "auth": True,
        "desc": "Get real-time GPS location",
        "params": {"vin": "1HGBH41JXMN109186"},
        "vuln": "IDOR: Change VIN to access other users vehicles",
        "severity": "CRITICAL"
    },
    {
        "method": "GET",
        "path": "/v1/vehicles/{vin}/battery",
        "auth": True,
        "desc": "Get battery status and range",
        "params": {"vin": "1HGBH41JXMN109186"},
        "vuln": "IDOR: VIN enumerable - sequential patterns found",
        "severity": "HIGH"
    },
    {
        "method": "POST",
        "path": "/v1/vehicles/{vin}/command/unlock",
        "auth": True,
        "desc": "Remote unlock doors",
        "params": {"vin": "1HGBH41JXMN109186"},
        "vuln": "No rate limiting - brute force VIN possible",
        "severity": "CRITICAL"
    },
    {
        "method": "POST",
        "path": "/v1/vehicles/{vin}/command/horn",
        "auth": True,
        "desc": "Remote horn trigger",
        "params": {"vin": "1HGBH41JXMN109186"},
        "vuln": "No rate limiting - DoS/harassment possible",
        "severity": "MEDIUM"
    },
    {
        "method": "POST",
        "path": "/v1/vehicles/{vin}/command/climate",
        "auth": True,
        "desc": "Remote climate control",
        "params": {"vin": "1HGBH41JXMN109186", "temp": 22},
        "vuln": "Input not sanitized - negative temps accepted",
        "severity": "LOW"
    },
    {
        "method": "GET",
        "path": "/v1/vehicles/{vin}/trips",
        "auth": True,
        "desc": "Full trip history with GPS routes",
        "params": {"vin": "1HGBH41JXMN109186"},
        "vuln": "Returns complete location history - no pagination limit",
        "severity": "HIGH"
    },
    {
        "method": "GET",
        "path": "/v1/admin/users",
        "auth": False,
        "desc": "Admin user listing",
        "params": {},
        "vuln": "CRITICAL: Admin endpoint exposed with no auth required",
        "severity": "CRITICAL"
    },
    {
        "method": "GET",
        "path": "/v1/vehicles/{vin}/diagnostics",
        "auth": True,
        "desc": "Full vehicle diagnostic data",
        "params": {"vin": "1HGBH41JXMN109186"},
        "vuln": "Returns VIN, ECU versions, fault codes - excessive data exposure",
        "severity": "MEDIUM"
    },
    {
        "method": "POST",
        "path": "/v1/vehicles/{vin}/firmware/update",
        "auth": True,
        "desc": "Trigger OTA firmware update",
        "params": {"vin": "1HGBH41JXMN109186", "version": "2.1.0"},
        "vuln": "No signature verification on firmware URL parameter",
        "severity": "CRITICAL"
    },
    {
        "method": "GET",
        "path": "/api/debug/config",
        "auth": False,
        "desc": "Debug configuration endpoint",
        "params": {},
        "vuln": "Left exposed in production - leaks API keys and DB config",
        "severity": "CRITICAL"
    },
]

# Phase 1: Endpoint discovery
print("─" * 60)
print("PHASE 1: ENDPOINT DISCOVERY")
print("─" * 60)
print("\n[*] Scanning for API endpoints...\n")
time.sleep(0.5)

for ep in API_ENDPOINTS:
    time.sleep(0.2)
    auth_str = "🔒 Auth" if ep["auth"] else "🔓 Open"
    print(f"  {ep['method']:<6} {ep['path']:<45} {auth_str}")

time.sleep(1)

# Phase 2: Authentication testing
print(f"\n{'─' * 60}")
print("PHASE 2: AUTHENTICATION TESTING")
print("─" * 60)

auth_tests = [
    ("Valid credentials",           True,  "200 OK - Token received"),
    ("Empty password",              False, "200 OK - ACCEPTED! No password required"),
    ("SQL injection in username",   False, "500 Internal Server Error - DB error exposed"),
    ("Expired token reuse",         False, "200 OK - ACCEPTED! Tokens never expire"),
    ("Token from other user",       False, "200 OK - ACCEPTED! No token binding"),
    ("No auth header at all",       False, "403 Forbidden - correctly rejected"),
]

print("\n[*] Testing authentication edge cases...\n")
for test, expected_secure, result in auth_tests:
    time.sleep(0.3)
    status = "✓ SECURE" if expected_secure else "✗ VULNERABLE"
    print(f"  {status}  {test}")
    print(f"           Response: {result}")

time.sleep(1)

# Phase 3: IDOR testing
print(f"\n{'─' * 60}")
print("PHASE 3: IDOR VULNERABILITY TESTING")
print("─" * 60)
print("\n[*] Testing Insecure Direct Object Reference...")
print("[*] Can we access OTHER users vehicles?\n")

my_vin = "1HGBH41JXMN109186"
target_vins = [
    "1HGBH41JXMN109187",
    "1HGBH41JXMN109188",
    "1HGBH41JXMN109189",
]

print(f"  My VIN:     {my_vin}")
print(f"  Testing sequential VINs...\n")

for vin in target_vins:
    time.sleep(0.3)
    # Simulate - real research would make actual HTTP requests
    accessible = random.random() > 0.3
    if accessible:
        lat = round(random.uniform(25, 48), 6)
        lon = round(random.uniform(-120, -70), 6)
        print(f"  GET /v1/vehicles/{vin}/location")
        print(f"  Response: 200 OK")
        print(f"  {{\"lat\": {lat}, \"lon\": {lon}, \"speed\": {random.randint(0,80)}mph}}")
        print(f"  [!] IDOR CONFIRMED - accessed another user's vehicle!\n")
    else:
        print(f"  GET /v1/vehicles/{vin}/location -> 403 Forbidden\n")

time.sleep(1)

# Phase 4: Sensitive data exposure
print(f"{'─' * 60}")
print("PHASE 4: SENSITIVE DATA EXPOSURE")
print("─" * 60)
print("\n[*] Checking debug/config endpoints...\n")

time.sleep(0.5)
fake_config = {
    "database": {
        "host": "prod-db.internal.evcompany.com",
        "port": 5432,
        "username": "ev_api_user",
        "password": "Sup3rS3cr3t!2024"
    },
    "aws": {
        "access_key": "AKIAIOSFODNN7EXAMPLE",
        "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
        "s3_bucket": "ev-firmware-updates-prod"
    },
    "jwt_secret": "mysupersecretjwtkey123",
    "admin_api_key": "sk-admin-8f7d3a2b1c9e4f6a"
}

print(f"  GET /api/debug/config")
print(f"  Response: 200 OK")
print(f"  {json.dumps(fake_config, indent=4)}")
print(f"\n  [!] CRITICAL: Production secrets exposed!")
print(f"  [!] AWS keys allow access to firmware S3 bucket")
print(f"  [!] DB password allows direct database access")
print(f"  [!] JWT secret allows forging any user token")

time.sleep(1)

# Phase 5: Generate report
print(f"\n{'=' * 60}")
print("  SECURITY ASSESSMENT REPORT")
print(f"{'=' * 60}")

findings = [(ep['severity'], ep['path'], ep['vuln'])
            for ep in API_ENDPOINTS if ep['vuln']]

severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
findings.sort(key=lambda x: severity_order.get(x[0], 4))

counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
for sev, _, _ in findings:
    counts[sev] += 1

print(f"""
  Target:    Generic EV Manufacturer API
  Date:      {datetime.now().strftime('%Y-%m-%d')}
  Tester:    bhurasingh

  SUMMARY:
  Critical:  {counts['CRITICAL']} findings
  High:      {counts['HIGH']} findings
  Medium:    {counts['MEDIUM']} findings
  Low:       {counts['LOW']} findings
""")

for sev, path, vuln in findings:
    print(f"  [{sev}] {path}")
    print(f"         {vuln}")
    print()

print(f"{'=' * 60}")
print(f"  OWASP API TOP 10 VIOLATIONS FOUND:")
print(f"{'=' * 60}")
print("""
  API1  Broken Object Level Auth    -> IDOR on VIN endpoints
  API2  Broken Authentication       -> Expired tokens accepted
  API3  Broken Object Property Auth -> Debug config exposed
  API5  Broken Function Level Auth  -> Admin endpoint open
  API6  Unrestricted Resource Use   -> No rate limiting
  API8  Security Misconfiguration   -> Debug endpoint in prod
""")
