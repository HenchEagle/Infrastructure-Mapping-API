from persistence.mysql.mysql_persister import MySQLPersister
from worker.worker import WorkerManager
from dotenv import load_dotenv
import asyncio
import os

ENABLE_CRT_SH = os.getenv("ENABLE_CRT_SH").lower() in ["true", "yes", "1"]
ENABLE_VIRUSTOTAL = os.getenv("ENABLE_VIRUSTOTAL").lower() in ["true", "yes", "1"]
ENABLE_CERTSPOTTER = os.getenv("ENABLE_CERTSPOTTER").lower() in ["true", "yes", "1"]

async def main():
    config = {
        "crtsh": ENABLE_CRT_SH,
        "virustotal": ENABLE_VIRUSTOTAL,
        "certspotter": ENABLE_CERTSPOTTER
    }

    if os.getenv("DB_TYPE") == "mysql":
        persister = MySQLPersister
    
    worker_manager = WorkerManager(persister=persister, config=config)

    await worker_manager.run()

if __name__ == "__main__":
    load_dotenv()

    asyncio.run(main())