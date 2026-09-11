"""
seed.py — Populate the database with demo CDN providers, resources,
policy rules, peering requests, and arrangements.
Run once:  python seed.py
"""

from app import create_app
from models import (
    db,
    CDNProvider,
    Resource,
    PolicyRule,
    PeeringRequest,
    PeeringArrangement,
    NegotiationLog,
)

app = create_app()

PROVIDERS = [
    {"name": "Cloudflare Edge",      "asn": "ASN 13335"},
    {"name": "Fastly POP",           "asn": "ASN 54113"},
    {"name": "Akamai Intelligent",   "asn": "ASN 20940"},
    {"name": "AWS CloudFront",       "asn": "ASN 16509"},
    {"name": "Lumen Fabric",         "asn": "ASN 3356"},
    {"name": "Verizon Digital",      "asn": "ASN 15133"},
    {"name": "Equinix Fabric",       "asn": "ASN 24115"},
    {"name": "Limelight Networks",   "asn": "ASN 22822"},
]

RESOURCES = [
    # Cloudflare
    {"provider": "Cloudflare Edge",    "rid": "RES-1001", "cpu": 1024, "storage": 120000, "up": 38, "down": 38.4},
    {"provider": "Cloudflare Edge",    "rid": "RES-1002", "cpu": 512,  "storage": 60000,  "up": 20, "down": 20.0},
    # Fastly
    {"provider": "Fastly POP",         "rid": "RES-1003", "cpu": 512,  "storage": 64000,  "up": 24, "down": 24.1},
    {"provider": "Fastly POP",         "rid": "RES-1004", "cpu": 256,  "storage": 32000,  "up": 12, "down": 12.5},
    # Akamai
    {"provider": "Akamai Intelligent", "rid": "RES-1005", "cpu": 2048, "storage": 240000, "up": 62, "down": 62.8},
    {"provider": "Akamai Intelligent", "rid": "RES-1006", "cpu": 1024, "storage": 120000, "up": 30, "down": 30.0},
    # AWS
    {"provider": "AWS CloudFront",     "rid": "RES-1007", "cpu": 1536, "storage": 96000,  "up": 51, "down": 51.2},
    # Lumen
    {"provider": "Lumen Fabric",       "rid": "RES-1008", "cpu": 768,  "storage": 48000,  "up": 18, "down": 18.9},
    # Verizon
    {"provider": "Verizon Digital",    "rid": "RES-1009", "cpu": 640,  "storage": 40000,  "up": 15, "down": 16.0},
    # Equinix
    {"provider": "Equinix Fabric",     "rid": "RES-1010", "cpu": 512,  "storage": 36000,  "up": 14, "down": 14.2},
    # Limelight
    {"provider": "Limelight Networks", "rid": "RES-1011", "cpu": 256,  "storage": 20000,  "up": 8,  "down": 0.0, "status": "standby"},
]

POLICIES = [
    {"provider": "Cloudflare Edge",    "min_cpu": 64,  "max_pct": 30, "max_rate": 15000},
    {"provider": "Fastly POP",         "min_cpu": 32,  "max_pct": 25, "max_rate": 12000},
    {"provider": "Akamai Intelligent", "min_cpu": 128, "max_pct": 20, "max_rate": 18000},
    {"provider": "AWS CloudFront",     "min_cpu": 96,  "max_pct": 35, "max_rate": 15000},
    {"provider": "Lumen Fabric",       "min_cpu": 48,  "max_pct": 25, "max_rate": 10000},
]


def seed():
    with app.app_context():
        # Skip if data already exists
        if CDNProvider.query.first():
            print("[SEED] Data already exists — skipping. Drop tables first to re-seed.")
            return

        # --- Providers ---
        provider_map = {}
        for p in PROVIDERS:
            obj = CDNProvider(name=p["name"], asn=p["asn"])
            db.session.add(obj)
            db.session.flush()
            provider_map[p["name"]] = obj
            print(f"  + Provider: {p['name']} ({p['asn']})")

        # --- Resources ---
        for r in RESOURCES:
            obj = Resource(
                resource_id=r["rid"],
                provider_id=provider_map[r["provider"]].id,
                cpu=r["cpu"],
                storage_gb=r["storage"],
                upload_rate=r["up"],
                download_rate=r["down"],
                status=r.get("status", "active"),
            )
            db.session.add(obj)
            print(f"  + Resource: {r['rid']} -> {r['provider']}")

        # --- Policy Rules ---
        for p in POLICIES:
            obj = PolicyRule(
                provider_id=provider_map[p["provider"]].id,
                min_cpu_available=p["min_cpu"],
                max_delegated_pct=p["max_pct"],
                max_request_rate=p["max_rate"],
            )
            db.session.add(obj)
            print(f"  + Policy: {p['provider']} (min_cpu={p['min_cpu']}, max_pct={p['max_pct']}%)")

        # --- Sample Peering Requests ---
        cf = provider_map["Cloudflare Edge"]
        ak = provider_map["Akamai Intelligent"]
        fs = provider_map["Fastly POP"]
        lm = provider_map["Lumen Fabric"]
        aws = provider_map["AWS CloudFront"]
        eq = provider_map["Equinix Fabric"]
        vz = provider_map["Verizon Digital"]

        # Accepted request → creates arrangement
        pr1 = PeeringRequest(provider_id=ak.id, target_provider_id=cf.id, load_pct=87, request_rate=11200, status="accepted")
        db.session.add(pr1)
        db.session.flush()

        arr1 = PeeringArrangement(primary_provider_id=ak.id, peer_provider_id=cf.id, request_id=pr1.id, status="active", accounting_units=28350, max_accounting_units=50000)
        db.session.add(arr1)
        db.session.flush()

        db.session.add(NegotiationLog(request_id=pr1.id, arrangement_id=arr1.id, action="accepted", message="[ACCEPTED] Policy SLA matched — Akamai Intelligent → Cloudflare Edge (Load: 87%)"))

        # Second accepted
        pr2 = PeeringRequest(provider_id=fs.id, target_provider_id=lm.id, load_pct=78, request_rate=9800, status="accepted")
        db.session.add(pr2)
        db.session.flush()

        arr2 = PeeringArrangement(primary_provider_id=fs.id, peer_provider_id=lm.id, request_id=pr2.id, status="active", accounting_units=14250, max_accounting_units=30000)
        db.session.add(arr2)
        db.session.flush()

        db.session.add(NegotiationLog(request_id=pr2.id, arrangement_id=arr2.id, action="accepted", message="[ACCEPTED] Policy SLA matched — Fastly POP → Lumen Fabric (Load: 78%)"))

        # Disbanded arrangement
        pr3 = PeeringRequest(provider_id=aws.id, target_provider_id=eq.id, load_pct=65, request_rate=7500, status="accepted")
        db.session.add(pr3)
        db.session.flush()

        arr3 = PeeringArrangement(primary_provider_id=aws.id, peer_provider_id=eq.id, request_id=pr3.id, status="disbanded", accounting_units=4120, max_accounting_units=40000)
        db.session.add(arr3)
        db.session.flush()

        db.session.add(NegotiationLog(request_id=pr3.id, arrangement_id=arr3.id, action="disbanded", message="Arrangement disbanded — AWS CloudFront ↔ Equinix Fabric"))

        # Rearranged arrangement
        pr4 = PeeringRequest(provider_id=vz.id, target_provider_id=lm.id, load_pct=82, request_rate=10500, status="accepted")
        db.session.add(pr4)
        db.session.flush()

        arr4 = PeeringArrangement(primary_provider_id=vz.id, peer_provider_id=lm.id, request_id=pr4.id, status="rearranged", accounting_units=19800, max_accounting_units=25000)
        db.session.add(arr4)
        db.session.flush()

        db.session.add(NegotiationLog(request_id=pr4.id, arrangement_id=arr4.id, action="rearranged", message="Rearranged from Arelion Carrier → Lumen Fabric"))

        # Rejected request (malicious)
        pr5 = PeeringRequest(provider_id=cf.id, target_provider_id=ak.id, load_pct=92, request_rate=18000, status="rejected", reject_reason="Rate exceeded ceiling (>15000/s) during ingress storm")
        db.session.add(pr5)
        db.session.flush()
        db.session.add(NegotiationLog(request_id=pr5.id, action="rejected", message="[MALICIOUS] Rate exceeded ceiling (>15000/s) — Cloudflare Edge → Akamai Intelligent"))

        # Pending request
        pr6 = PeeringRequest(provider_id=lm.id, target_provider_id=aws.id, load_pct=74, request_rate=8900, status="pending")
        db.session.add(pr6)
        db.session.flush()
        db.session.add(NegotiationLog(request_id=pr6.id, action="info", message="Port Rebalance — Lumen Fabric → AWS CloudFront (awaiting arbitration)"))

        db.session.commit()
        print("\n[SEED] Database seeded successfully with demo data!")
        print(f"  Providers:    {len(PROVIDERS)}")
        print(f"  Resources:    {len(RESOURCES)}")
        print(f"  Policies:     {len(POLICIES)}")
        print(f"  Requests:     6")
        print(f"  Arrangements: 4")


if __name__ == "__main__":
    seed()
