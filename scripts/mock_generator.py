import json
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid

fake = Faker('en_IN')

# Entities lists
persons = []
phones = []
bank_accounts = []
upi_ids = []
emails = []
devices = []

# Relationships lists
called_edges = []
transferred_edges = []
upi_edges = []
uses_number_edges = []
holds_account_edges = []
operates_upi_edges = []
associated_email_edges = []
logged_device_edges = []

def generate_phone():
    return f"9{random.randint(100000000, 999999999)}"

def generate_cctns():
    return f"FIR-2025-{random.randint(100, 999)}"

def generate_bank_acc():
    return f"SBIN{random.randint(1000000, 9999999)}"

def generate_upi():
    return f"{fake.user_name()}@okicici"

# 1 Kingpin
kingpin = {
    "cctns_id": generate_cctns(),
    "name": "Vikram Singh (Kingpin)",
    "risk_level": "CRITICAL",
    "nationality": "Indian"
}
persons.append(kingpin)
kp_phone = {"number": generate_phone(), "telecom_circle": "Delhi-NCR", "imsi": str(uuid.uuid4())[:15], "is_burner": True}
phones.append(kp_phone)
uses_number_edges.append({"cctns_id": kingpin["cctns_id"], "number": kp_phone["number"]})

# 3 Sub-handlers
sub_handlers = []
for i in range(3):
    sh = {
        "cctns_id": generate_cctns(),
        "name": fake.name(),
        "risk_level": "HIGH",
        "nationality": "Indian"
    }
    persons.append(sh)
    sub_handlers.append(sh)
    sh_phone = {"number": generate_phone(), "telecom_circle": "Mumbai", "imsi": str(uuid.uuid4())[:15], "is_burner": True}
    phones.append(sh_phone)
    uses_number_edges.append({"cctns_id": sh["cctns_id"], "number": sh_phone["number"]})

# 10 Layering Accounts (Entities + Bank Accounts)
layering_nodes = []
for i in range(10):
    p = {
        "cctns_id": generate_cctns(),
        "name": fake.name(),
        "risk_level": "MEDIUM",
        "nationality": "Indian"
    }
    persons.append(p)
    b_acc = {"account_number": generate_bank_acc(), "ifsc": "SBIN0000123", "bank_name": "SBI", "branch": "Main", "freeze_status": False}
    bank_accounts.append(b_acc)
    holds_account_edges.append({"cctns_id": p["cctns_id"], "account_number": b_acc["account_number"]})
    layering_nodes.append((p, b_acc))

# 50 Mule Accounts
mules = []
for i in range(50):
    p = {
        "cctns_id": generate_cctns(),
        "name": fake.name(),
        "risk_level": "NORMAL",
        "nationality": "Indian"
    }
    persons.append(p)
    b_acc = {"account_number": generate_bank_acc(), "ifsc": "HDFC0000123", "bank_name": "HDFC", "branch": "Local", "freeze_status": False}
    bank_accounts.append(b_acc)
    holds_account_edges.append({"cctns_id": p["cctns_id"], "account_number": b_acc["account_number"]})
    mules.append((p, b_acc))

# Generating 1,000 CDRs (CALLED)
start_date = datetime(2025, 1, 1)
for _ in range(1000):
    # Kingpin occasionally calls subhandlers
    # Subhandlers call each other and layering accounts
    r = random.random()
    if r < 0.1:
        caller = kp_phone
        receiver = phones[random.randint(1, 3)]
    elif r < 0.5:
        caller = phones[random.randint(1, 3)]
        receiver = phones[random.randint(1, 3)]
    else:
        caller = phones[random.randint(1, 3)]
        receiver = {"number": generate_phone(), "telecom_circle": "Other", "imsi": str(uuid.uuid4())[:15], "is_burner": False}
        if receiver not in phones:
            phones.append(receiver)
            
    call_time = start_date + timedelta(minutes=random.randint(1, 40000))
    called_edges.append({
        "caller": caller["number"],
        "receiver": receiver["number"],
        "timestamp": call_time.isoformat(),
        "duration_sec": random.randint(10, 300),
        "cell_tower": f"Tower_{random.randint(1, 100)}"
    })

# Generating 500 Financial Transactions (TRANSFERRED_FUNDS) - layering structure
for _ in range(500):
    r = random.random()
    if r < 0.2:
        # Layering to Layering
        src = random.choice(layering_nodes)[1]
        tgt = random.choice(layering_nodes)[1]
        amt = random.randint(50000, 500000)
    elif r < 0.8:
        # Layering to Mule (shattering)
        src = random.choice(layering_nodes)[1]
        tgt = random.choice(mules)[1]
        amt = random.randint(5000, 25000)
    else:
        # Mule to out (external)
        src = random.choice(mules)[1]
        tgt = {"account_number": generate_bank_acc(), "ifsc": "ICIC0000123", "bank_name": "ICICI", "branch": "Out", "freeze_status": False}
        if tgt not in bank_accounts:
            bank_accounts.append(tgt)
        amt = random.randint(1000, 25000)
        
    txn_time = start_date + timedelta(minutes=random.randint(1, 40000))
    transferred_edges.append({
        "src_account": src["account_number"],
        "tgt_account": tgt["account_number"],
        "amount": amt,
        "timestamp": txn_time.isoformat(),
        "channel": random.choice(['IMPS', 'NEFT', 'RTGS']),
        "utr": f"UTR{random.randint(10000000, 99999999)}"
    })

data = {
    "persons": persons,
    "phones": phones,
    "bank_accounts": bank_accounts,
    "upi_ids": upi_ids,
    "emails": emails,
    "devices": devices,
    "called_edges": called_edges,
    "transferred_edges": transferred_edges,
    "uses_number_edges": uses_number_edges,
    "holds_account_edges": holds_account_edges
}

with open("synthetic_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Generated synthetic data (synthetic_data.json)")
