from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to {URI} with user {USER}")

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
    print("CONNECTION SUCCESSFUL!")
    driver.close()
except Exception as e:
    print("CONNECTION FAILED:")
    import traceback
    traceback.print_exc()
