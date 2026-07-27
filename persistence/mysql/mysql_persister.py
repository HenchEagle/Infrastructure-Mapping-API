from persistence.persister import Persister
from persistence.mysql.scan_repository import ScanRepository
from persistence.mysql.graph_repository import GraphRepository
from dotenv import load_dotenv
from datetime import datetime
import mysql.connector
import os

class MySQLPersister(Persister):
    def __init__(self):
        self.connection = self.get_connection()
        self.scan_repository = ScanRepository(self.connection)
        self.graph_repository = GraphRepository(self.connection)

    def get_connection(self):
        load_dotenv()

        DB_HOST = os.getenv("DB_HOST")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWD = os.getenv("DB_PASSWD")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWD,
            port=DB_PORT,
            database=DB_NAME
        )

    # Scan Repository
    def create_scan_record(self, domain):
        self.scan_repository.create_scan_record(domain)

    def update_scan_status(self, scan_id, status):
        self.scan_repository.update_scan_status(scan_id, status)

    def get_scan_queue(self):
        return self.scan_repository.get_scan_queue()

    def get_last_scan(self, domain):
        return self.scan_repository.get_last_scan(domain)

    # Graph Repository
    def write_edges(self, graph):
        return self.graph_repository.write_edges(graph)

    def write_nodes(self, graph):
        self.graph_repository.write_nodes(graph)

    def write_scan_relationships(self, graph, relationship_ids, scan_id):
        self.graph_repository.write_scan_relationships(graph, relationship_ids, scan_id)

    def get_full_graph(self, domain):
        return self.graph_repository.get_full_graph(domain)