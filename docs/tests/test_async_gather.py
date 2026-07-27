import asyncio

import dns.asyncresolver
import asyncio

async def fetch_origin_asn(ip: str) -> dns.resolver.Answer | None:
    resolver = dns.asyncresolver.Resolver()

    print(f"[⋆] QUERY ASN ORIGIN | {ip}")
    try:
        reversed_ip = ".".join(reversed(ip.split(".")))
        query = f"{reversed_ip}.origin.asn.cymru.com"

        result = await(resolver.resolve(query, "TXT"))
        return result
                
    except(
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.Timeout,
        dns.resolver.NoNameservers,
    ):
        return None
    

async def fetch_asn_metadata(asn: str) -> dns.resolver.Answer | None:
    resolver = dns.asyncresolver.Resolver()

    print(f"[⋆] QUERY ASN ORGANISATION | {asn}")
    try:
        query = f"AS{asn}.asn.cymru.com"

        result = await(resolver.resolve(query, "TXT"))
        return result

    except(
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.Timeout,
        dns.resolver.NoNameservers,
    ):
        return None


def process_cymru_origin(x, y, z):
    print("origin")
    print(x, y, z)

def process_cymru_metadata(x, y, z):
    print("metadata")
    print(x, y, z)

async def cymru_pipeline(graph="hello") -> None:
    ips = ["8.8.8.8", "0.0.0.0", "1.1.1.1"]

    origin_results = await asyncio.gather(
        *(fetch_origin_asn(ip) for ip in ips)
    )

    for ip, data in zip(ips, origin_results):
        process_cymru_origin(data, ip, graph)

    asns = [asn.data for asn in graph.asns.values()]

    asn_results = await asyncio.gather(
        *(fetch_asn_metadata(asn) for asn in asns)
    )

    for asn, data in zip(asns, asn_results):
        if data:
            process_cymru_metadata(data, asn, graph)

asyncio.run(cymru_pipeline())