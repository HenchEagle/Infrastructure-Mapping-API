from core.engine import Engine
import asyncio

class WorkerManager():
    def __init__(self, persister, config):
        self.persister = persister
        self.config = config
        self.worker_persister = self.persister()

    async def run(self):
        try:
            print("STARTING WORKERS")
            await self.manage_workers()
        except Exception as e:
            print("ERROR: ", end="")
            print(e)

    async def spawn_worker(self, scan_id, domain, sem):
        async with sem:
            try:
                engine = Engine(self.persister())

                result = await engine.run_scan(domain, self.config, scan_id)

                print(f"SCAN COMPLETED {domain}")

            except Exception as e:
                print(e)
                self.worker_persister.update_scan_status(scan_id, "failed")

    async def get_job(self):
        result = self.worker_persister.get_scan_queue()

        if result:
            scan_id, domain = result[0], result[1]

            self.worker_persister.update_scan_status(scan_id, "pending")
            return scan_id, domain
        
        await asyncio.sleep(15)
        return None, None

    async def manage_workers(self):
        sem = asyncio.Semaphore(3) # Max concurrent tasks - 3 workers.
        found_job = False
        tasks = set()

        while True:
            while found_job == False:
                if len(tasks) >= 3:
                    await asyncio.sleep(15)
                    continue

                scan_id, domain = await self.get_job()
                if scan_id:
                    found_job = True
            
            task = asyncio.create_task(self.spawn_worker(scan_id, domain, sem))

            print(f"CREATED WORKER FOR SCAN_ID {scan_id}")

            tasks.add(task)
            task.add_done_callback(tasks.discard)
            found_job = False