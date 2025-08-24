# main.py
import asyncio
from typing import Any, List, Optional
from fastapi import FastAPI, Query
import httpx

# The address where the service bus API is accessible
BUS_BASE = "http://127.0.0.1:8001"
# How often to poll the bus (in seconds)
POLL_INTERVAL_SEC = 5
# Timeout for HTTP requests (in seconds)
HTTP_TIMEOUT = 5.0

# Minimal in-memory storage for received data
# Each item is a dictionary: {service_id, kind, t, v}
_DB: List[dict] = []

# Create FastAPI app instance with a custom title
app = FastAPI(title="vCare Consumer")


# Function to normalize any response into a common schema
# - service_id: ID of the service
# - rel: relationship/type of data
# - payload: the actual data received (can be list or dict)
def normalize(service_id: str, rel: str, payload: Any) -> List[dict]:
    """Maps any response into a minimal common schema."""
    # Ensure we always work with a list
    items = payload if isinstance(payload, list) else [payload]
    out = []
    for it in items:
        # If item is a dictionary, extract fields
        if isinstance(it, dict):
            out.append(
                {
                    "service_id": service_id,
                    "kind": rel,
                    "t": str(it.get("timestamp")),
                    "v": it.get("value", it),
                }
            )
        # If item is not a dictionary, store as-is
        else:
            out.append({"service_id": service_id, "kind": rel, "t": None, "v": it})
    return out


# Asynchronous function to fetch JSON data from a URL using httpx
async def fetch_json(client: httpx.AsyncClient, url: str):
    # Make GET request with timeout
    r = await client.get(url, timeout=HTTP_TIMEOUT)
    # Raise error if response is not 2xx
    r.raise_for_status()
    # Return parsed JSON data
    return r.json()


# Poll the service bus once: get services, then get capabilities and data for each
async def poll_once():
    async with httpx.AsyncClient() as c:
        # Get the list of available services from the bus
        # Example response: [{"id":"svc-a"}, ...]
        services = await fetch_json(c, f"{BUS_BASE}/bus/services")
        # For each service, get its capabilities (endpoints)
        for s in services:
            # Service ID
            sid = s["id"]
            # Get capabilities
            caps = await fetch_json(c, f"{BUS_BASE}/services/{sid}/capabilities")
            # For each endpoint in capabilities
            for ep in caps.get("endpoints", []):
                # Endpoint path
                href = ep["href"]
                # Build full URL
                url = BUS_BASE + href if href.startswith("/") else href
                # Fetch data from endpoint
                data = await fetch_json(c, url)
                # Store normalized data in DB
                _DB.extend(normalize(sid, ep["rel"], data))


# Loop that continuously polls the bus at regular intervals
async def polling_loop():
    while True:
        try:
            # Poll once
            await poll_once()
        except Exception as e:
            # Do not stop the application if a request fails
            print("[poll] error:", e)
        # Wait before next poll
        await asyncio.sleep(POLL_INTERVAL_SEC)


# FastAPI event: runs when the app starts
@app.on_event("startup")
async def _startup():
    # Start polling loop as a background task
    asyncio.create_task(polling_loop())


# Health check endpoint: returns status OK
@app.get("/health")
def health():
    return {"status": "ok"}


# Endpoint to get all data, or filter by kind
@app.get("/data")
def get_data(kind: Optional[str] = Query(default=None)):
    # Return only items of given kind if specified
    if kind:
        return [r for r in _DB if r["kind"] == kind]
    # Return all items
    return _DB


# Endpoint to clear the in-memory database
@app.post("/admin/clear")
def clear():
    # Remove all items from DB
    _DB.clear()
    return {"cleared": True}