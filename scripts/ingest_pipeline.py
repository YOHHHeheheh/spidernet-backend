import json
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "LawEnforcementSecurePass#2026")

def create_constraints_and_indexes(tx):
    constraints = [
        "CREATE CONSTRAINT unique_person_cctns IF NOT EXISTS FOR (p:Person) REQUIRE p.cctns_id IS UNIQUE",
        "CREATE CONSTRAINT unique_phone_number IF NOT EXISTS FOR (ph:PhoneNumber) REQUIRE ph.number IS UNIQUE",
        "CREATE CONSTRAINT unique_bank_acc IF NOT EXISTS FOR (b:BankAccount) REQUIRE b.account_number IS UNIQUE",
        "CREATE CONSTRAINT unique_upi_vpa IF NOT EXISTS FOR (u:UpiID) REQUIRE u.vpa IS UNIQUE",
        "CREATE CONSTRAINT unique_email_addr IF NOT EXISTS FOR (e:Email) REQUIRE e.address IS UNIQUE",
        "CREATE CONSTRAINT unique_device_imei IF NOT EXISTS FOR (d:Device) REQUIRE d.imei IS UNIQUE",
        "CREATE INDEX idx_phone_search IF NOT EXISTS FOR (ph:PhoneNumber) ON (ph.number)",
        "CREATE INDEX idx_upi_search IF NOT EXISTS FOR (u:UpiID) ON (u.vpa)",
        "CREATE INDEX idx_email_search IF NOT EXISTS FOR (e:Email) ON (e.address)"
    ]
    for query in constraints:
        tx.run(query)

def ingest_data(tx, data):
    # Ingest Persons
    tx.run("""
    UNWIND $persons AS p
    MERGE (n:Person {cctns_id: p.cctns_id})
    SET n.name = p.name, n.risk_level = p.risk_level, n.nationality = p.nationality
    """, persons=data.get('persons', []))

    # Ingest Phones
    tx.run("""
    UNWIND $phones AS ph
    MERGE (n:PhoneNumber {number: ph.number})
    SET n.telecom_circle = ph.telecom_circle, n.imsi = ph.imsi, n.is_burner = ph.is_burner
    """, phones=data.get('phones', []))

    # Ingest Bank Accounts
    tx.run("""
    UNWIND $banks AS b
    MERGE (n:BankAccount {account_number: b.account_number})
    SET n.ifsc = b.ifsc, n.bank_name = b.bank_name, n.branch = b.branch, n.freeze_status = b.freeze_status
    """, banks=data.get('bank_accounts', []))

    # Ingest USES_NUMBER edges
    tx.run("""
    UNWIND $edges AS e
    MATCH (p:Person {cctns_id: e.cctns_id})
    MATCH (ph:PhoneNumber {number: e.number})
    MERGE (p)-[:USES_NUMBER]->(ph)
    """, edges=data.get('uses_number_edges', []))

    # Ingest HOLDS_ACCOUNT edges
    tx.run("""
    UNWIND $edges AS e
    MATCH (p:Person {cctns_id: e.cctns_id})
    MATCH (b:BankAccount {account_number: e.account_number})
    MERGE (p)-[:HOLDS_ACCOUNT]->(b)
    """, edges=data.get('holds_account_edges', []))

    # Ingest CALLED edges
    tx.run("""
    UNWIND $edges AS e
    MATCH (src:PhoneNumber {number: e.caller})
    MATCH (tgt:PhoneNumber {number: e.receiver})
    MERGE (src)-[r:CALLED {timestamp: e.timestamp}]->(tgt)
    SET r.duration_sec = e.duration_sec, r.cell_tower = e.cell_tower
    """, edges=data.get('called_edges', []))

    # Ingest TRANSFERRED_FUNDS edges
    tx.run("""
    UNWIND $edges AS e
    MATCH (src:BankAccount {account_number: e.src_account})
    MATCH (tgt:BankAccount {account_number: e.tgt_account})
    MERGE (src)-[r:TRANSFERRED_FUNDS {utr: e.utr}]->(tgt)
    SET r.amount = e.amount, r.timestamp = e.timestamp, r.channel = e.channel
    """, edges=data.get('transferred_edges', []))

def main():
    print("Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        with driver.session() as session:
            print("Applying constraints and indexes...")
            session.execute_write(create_constraints_and_indexes)
            
            print("Loading data from synthetic_data.json...")
            with open("synthetic_data.json", "r") as f:
                data = json.load(f)
                
            print("Ingesting data...")
            session.execute_write(ingest_data, data)
            print("Data ingestion complete!")
            
        driver.close()
    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    main()
