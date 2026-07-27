from persistence.mappers.edge_mapper import map_edges
from persistence.mappers.node_mapper import map_nodes
from core.extract_apex import extract_apex
from datetime import datetime
import mysql.connector
import json

class GraphRepository():
    def __init__(self, connection):
        self.connection = connection

    def get_full_graph(self, domain): 
        cursor = self.connection.cursor()

        apex_domain = extract_apex(domain)

        sql = """
        SELECT n_source.data, n_source.type, COALESCE(n_source.properties, '{}'), n_target.data, n_target.type, COALESCE(n_target.properties, '{}'), r.relationship_type, s.finished_at
        FROM scan_relationships sr

        JOIN scans s
        ON s.scan_id = sr.scan_id

        JOIN relationships r
        ON sr.relationship_id = r.relationship_id

        JOIN nodes n_source
        ON r.source_hash = n_source.node_hash

        JOIN nodes n_target
        ON r.target_hash = n_target.node_hash

        WHERE s.apex_domain = %s
        """

        cursor.execute(sql, (apex_domain,))

        results = {}
        row_number = 1

        for row in cursor:
            results[f"row_{row_number}"] = {
                "source": {
                    "data": row[0],
                    "type": row[1],
                    "properties": json.loads(row[2]) 
                },
                "target": {
                    "data": row[3],
                    "type": row[4],
                    "properties": json.loads(row[5]) 
                },
                "relationship": {
                    "type": str(row[6]),
                    "finished_at": str(row[7]),
                }
            }

            row_number += 1

        cursor.close()

        return results

    def write_edges(self, graph: Graph) -> list[int]:
        edges = map_edges(graph)

        try:
            cursor = self.connection.cursor()

            query = ("""
            INSERT INTO relationships(source_hash, target_hash, relationship_type, observed_at)
            VALUES(%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                relationship_id = LAST_INSERT_ID(relationship_id)
            """)

            relationship_ids = []

            # Itterate through our values
            for source, target, relationship_type, observed_at in edges:
                cursor.execute(query, (source, target, relationship_type, observed_at))

                relationship_ids.append(cursor.lastrowid) 

            self.connection.commit()

        except mysql.connector.Error as err:
            connection.rollback()
            print(err)
            print("TRANSACTION ABORTED & ROLLED BACK. DB NOT UPDATED WITH EDGES")
        finally:
            cursor.close()

        return relationship_ids

    def write_nodes(self, graph: Graph) -> None:
        cursor = self.connection.cursor()

        try:
            nodes = map_nodes(graph)

            sql = """
            INSERT IGNORE INTO nodes (node_hash, type, data, properties)
            VALUES (%s, %s, %s, %s)
            """

            cursor.executemany(sql, nodes)
            self.connection.commit()

        except mysql.connector.Error as err:
            self.connection.rollback()
            print(err)
            print("TRANSACTION ABORTED & ROLLED BACK. DB NOT UPDATED WITH NODES")

    def write_scan_relationships(self, graph: Graph, relationship_ids: list[int], scan_id) -> None:
        cursor = self.connection.cursor()
        # CREATE ITERABLE OF SCAN <> RELATIONSHIP IDS AND INSERT INTO DB.
        try:
            scan_to_relationship_query = """
            INSERT IGNORE INTO scan_relationships (scan_id, relationship_id)
            VALUES (%s, %s)
            """

            rows = [(scan_id, relationship_id) for relationship_id in relationship_ids]

            cursor.executemany(scan_to_relationship_query, (rows))

            self.connection.commit()
        
        # IN CASE OF AN ERROR DO NOT COMMIT TO PRESERVE INTEGRITY
        except mysql.connector.Error as err:
            self.connection.rollback()
            print(err)
            print("TRANSACTION ABORTED & ROLLED BACK. DB NOT UPDATED WITH SCANS_RELATIONSHIPS")
        finally:
            cursor.close()