from persistence.db.connection import get_connection

def read_full_graph(apex_domain):
    connection = get_connection()

    cursor = connection.cursor()

    sql = """
    SELECT n_source.data, n_source.type, n_target.data, n_target.type, r.relationship_type, s.finished_at
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

    results = [x for x in cursor]

    return results