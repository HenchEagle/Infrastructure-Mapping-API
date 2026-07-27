from core.engine import Engine
from core.configuration import create_config
from persistence.mysql.mysql_persister import MySQLPersister
from worker.worker import WorkerManager
import sys
import asyncio

class SQLitePersister():
    pass

class PostgreSQLPersister():
    pass

class StdoutPersister():
    pass

def main():
    config = create_config()

    if config["database"] == "STDOUT":
        persister = MySQLPersister()
    elif config["database"] == "SQLITE":
        persister = SQLitePersister()
    elif config["database"] == "POSTGRES":
        persister = PostgreSQLPersister()
    else:
        persister = MySQLPersister()

    worker = WorkerManager(persister, config)

    try:
        worker.start_worker_manager()
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit()

if __name__ == "__main__":
    main()