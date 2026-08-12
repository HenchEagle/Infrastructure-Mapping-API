import dns.asyncresolver
import asyncio

async def resolve_dns_query(domain: str, rtype: str) -> dns.resolver.Answer | None:
    resolver = dns.asyncresolver.Resolver()

    print(f"[⋆] QUERY DNS - {rtype} | {domain}")
    try:
        result = await resolver.resolve(domain, rtype)
        return [str(r) for r in result]

    except(
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.Timeout,
        dns.resolver.NoNameservers,
    ):
        return None

DNS_RECORD_TYPES = (
    "A", 
    "AAAA", 
    "NS", 
    "MX", 
    "TXT", 
    "SOA", 
    "SRV",
    "CNAME"
)

"""
    queue = Queue(deque(graph.get_domains()), set())

    while len(queue.queue):
        domain = queue.next_item_in_queue()
"""
def process_dns(dns_records):
    print(dns_records)

from collections import defaultdict

async def dns_pipeline() -> None:
    queue = ("example.com", "www.example.com")
    tasks = {}
    dns_records = defaultdict(dict) # The missing value for any dictionary is a dictionary.

    for domain in queue:
        for rtype in DNS_RECORD_TYPES:
            task = asyncio.create_task(resolve_dns_query(domain, rtype))
            tasks[task] = (domain, rtype)

    while tasks:
        done, _ = await asyncio.wait(
            tasks.keys(),
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in done:
            domain, rtype = tasks.pop(task) # we pop the task, before we await it incase an exception is raised, and the task stays inside the dictionary.

            raw_data = await task

            if not raw_data:
                continue

            if rtype == "CNAME":
                for record in raw_data:
                    domain = record.removesuffix(".")

                    if domain.startswith("*"):
                        continue

                    task = asyncio.create_task(resolve_dns_query(domain, "CNAME"))
                    tasks[task] = (domain, "CNAME")

                    dns_records[domain][rtype] = raw_data

            else:
                dns_records[domain][rtype] = raw_data

    process_dns(dns_records)

asyncio.run(dns_pipeline())