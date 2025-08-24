# main.py
import asyncio
from typing import Any, List, Optional
from fastapi import FastAPI, Query
import httpx

# address where the bus is accessible
BUS_BASE = "http://127.0.0.1:8001"  
POLL_INTERVAL_SEC = 5
HTTP_TIMEOUT = 5.0

# minimal in-memory storage
# each item: {service_id, kind, t, v}
_DB: List[dict] = []  

app = FastAPI(title="vCare Consumer")

def normalize(service_id: str, rel: str, payload: Any) -> List[dict]:
    """Maps any response into a minimal common schema."""
    items = payload if isinstance(payload, list) else [payload]
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append({
                "service_id": service_id,
                "kind": rel,
                "t": str(it.get("timestamp")),
                "v": it.get("value", it),
            })
        else:
            out.append({"service_id": service_id, "kind": rel, "t": None, "v": it})
    return out

async def fetch_json(client: httpx.AsyncClient, url: str):
    r = await client.get(url, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()

async def poll_once():
    async with httpx.AsyncClient() as c:
        # 1) get the list of services
        # [{"id":"svc-a"}, ...]
        services = await fetch_json(c, f"{BUS_BASE}/bus/services") 
        # 2) for each service -> get its capabilities
        for s in services:
            sid = s["id"]
            caps = await fetch_json(c, f"{BUS_BASE}/services/{sid}/capabilities")
            for ep in caps.get("endpoints", []):
                href = ep["href"]
                url = BUS_BASE + href if href.startswith("/") else href
                data = await fetch_json(c, url)
                _DB.extend(normalize(sid, ep["rel"], data))

async def polling_loop():
    while True:
        try:
            await poll_once()
        except Exception as e:
            # do not stop the application if a request fails
            print("[poll] error:", e)
        await asyncio.sleep(POLL_INTERVAL_SEC)

@app.on_event("startup")
async def _startup():
    asyncio.create_task(polling_loop())

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/data")
def get_data(kind: Optional[str] = Query(default=None)):
    if kind:
        return [r for r in _DB if r["kind"] == kind]
    return _DB

@app.post("/admin/clear")
def clear():
    _DB.clear()
    return {"cleared": True}