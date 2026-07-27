from pipelines.dns_pipeline import dns_pipeline
from pipelines.virustotal_pipeline import virustotal_pipeline
from pipelines.crtsh_pipeline import crtsh_pipeline
from pipelines.certspotter_pipeline import certspotter_pipeline
from pipelines.cymru_pipeline import cymru_pipeline
from pipelines.persistence_pipeline import persistence_pipeline
from core.graph import Graph
from core.models import *
from core.write_to_json import write_to_json
import sys
import asyncio
import time

class Engine():
    def __init__(self, persister):
        self.persister = persister
        self.graph = Graph()

    async def run_scan(self, domain, config, scan_id):
        try:
            self.graph.apex_domain = domain
            self.graph.add_node(FQDN(domain))

            start_scan = time.perf_counter()

            async with asyncio.TaskGroup() as tg:
                print("\n-- [+] BEGIN PASSIVE RECON --\n")
                if config["virustotal"]:
                    tg.create_task(virustotal_pipeline(self.graph))

                if config["crtsh"]:
                    while True:
                        try:
                            tg.create_task(crtsh_pipeline(self.graph))
                            break
                        except ValueError:
                            continue

                if config["certspotter"]:
                    tg.create_task(certspotter_pipeline(self.graph))

            print("\n-- [+] BEGIN DNS RECON --\n")
            await dns_pipeline(self.graph)

            print("\n-- [+] BEGIN BGP RECON --\n")
            await cymru_pipeline(self.graph)

            end_scan = time.perf_counter()

            if config["output"] != None:
                write_to_json(self.graph, config)

            print(f"\n\n\n\nTotal Scan Time: {end_scan - start_scan:.2f} seconds\n\n")

            persistence_pipeline(self.graph, scan_id, self.persister)

            return 1

        except asyncio.CancelledError:
            print("\nExiting.")
            return 0

        except KeyboardInterrupt:
            print("\nExiting.")
            return 0

        except Exception as e:
            print("ERROR:",end="")
            print(e)
            return 0