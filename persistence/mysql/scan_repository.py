from core.extract_apex import extract_apex
from datetime import datetime
import mysql.connector

class ScanRepository():
    def __init__(self, connection):
        self.connection = connection

    def get_scan_queue(self):
        cursor = self.connection.cursor()

        try:
            query = """
            SELECT scan_id, query_domain FROM scans
            WHERE status = 'QUEUED'
            ORDER BY scan_id ASC
            LIMIT 1;
            """

            cursor.execute(query)

            return cursor.fetchone()

        finally:
            cursor.close()
            self.connection.rollback()

    def get_last_scan(self, domain):
        cursor = self.connection.cursor()

        sql = """
        SELECT finished_at FROM scans
        WHERE apex_domain = %s
        ORDER BY finished_at DESC
        LIMIT 1
        """

        cursor.execute(sql, (domain,))

        try:
            current_date = datetime.now().replace(microsecond=0)
            last_scan = cursor.fetchone()[0]

            time_difference = current_date - last_scan

            cursor.close()

            return int(time_difference.total_seconds() // 3600)

        except:
            cursor.close()
                    
            return None

    def create_scan_record(self, domain):
        cursor = self.connection.cursor()

        apex_domain = extract_apex(domain)

        try:
            # INSERT SCAN INTO THE DATABASE
            scans_query = """
            INSERT IGNORE INTO scans (apex_domain, status, query_domain)
            VALUES (%s, %s, %s)
            """

            cursor.execute(scans_query, (apex_domain, "QUEUED", domain))

            self.connection.commit()

            return cursor.lastrowid
        
        finally:
            cursor.close()

    def update_scan_status(self, scan_id, status):
        cursor = self.connection.cursor()

        if status == "pending":
            query = """
            UPDATE scans
            SET status = "PROCESSING",
            started_at = NOW()
            WHERE scan_id = %s
            """

            cursor.execute(query, (scan_id,))

            self.connection.commit()

        elif status == "complete":
            query = """
            UPDATE scans
            SET status = "COMPLETE",
            finished_at = NOW()
            WHERE scan_id = %s
            """

            cursor.execute(query, (scan_id,))

            self.connection.commit()

        elif status == "failed":    
            query = """
            UPDATE scans
            SET status = "FAILED",
            finished_at = NOW()
            WHERE scan_id = %s
            """

            cursor.execute(query, (scan_id,))

            self.connection.commit()

        cursor.close()

