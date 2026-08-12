import time

def persistence_pipeline(graph, scan_id, persister):
    start_write_db = time.perf_counter()

    persister.write_nodes(graph)
    edge_ids = persister.write_edges(graph)

    persister.write_scan_relationships(graph, edge_ids, scan_id)

    persister.update_scan_status(scan_id, "complete")

    end_write_db = time.perf_counter()

    print(f"\nTotal Databse Write Time: {end_write_db - start_write_db:.2f} seconds")