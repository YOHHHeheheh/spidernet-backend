from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            # Added max_connection_lifetime to prevent idle connections from being killed by AuraDB
            self.__driver = GraphDatabase.driver(
                self.__uri, 
                auth=(self.__user, self.__pwd),
                max_connection_lifetime=30 * 60,
                keep_alive=True
            )
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
            
    def get_session(self):
        return self.__driver.session()
        
db_conn = Neo4jConnection(settings.NEO4J_URI, settings.NEO4J_USER, settings.NEO4J_PASSWORD)
