import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

cypher = """
// 1. Create the Cold Case Criminal from 2007
CREATE (old_criminal:Person {
    name: "Ramesh 'The Ghost' Kumar",
    cctns_id: "CCTNS-2007-00142",
    risk_level: "HIGH"
})

// 2. Create his phone number
CREATE (old_phone:PhoneNumber {
    number: "9998887776",
    risk_level: "CRITICAL",
    carrier: "BSNL",
    last_active: "2026-09-12T10:14:00Z"
})

// 3. Create the 2007 FIR/Case File
CREATE (cold_case:FIR {
    id: "FIR-2007-DEL-89",
    date: "2007-11-14",
    status: "ARCHIVED",
    charge: "Narcotics Smuggling",
    jurisdiction: "Delhi Police Special Cell"
})

// 4. Create the relationships
CREATE (old_criminal)-[:OWNS]->(old_phone)
CREATE (old_criminal)-[:ARRESTED_IN]->(cold_case)

// 5. Link to the current Kingpin
WITH old_phone
MATCH (kingpin:PhoneNumber {number: "9313090380"})
CREATE (old_phone)-[:CALLED {
    timestamp: "2026-09-12T10:15:22Z",
    duration_sec: 412,
    type: "VOICE",
    cell_tower_start: "CELL-TWR-88"
}]->(kingpin)

RETURN old_phone.number AS injected_number
"""

try:
    with driver.session() as session:
        result = session.run(cypher)
        record = result.single()
        print(f"SUCCESS: Injected Cold Case! Search for {record['injected_number']}")
finally:
    driver.close()
