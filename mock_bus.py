# mock_bus.py
from fastapi import FastAPI
from typing import List, Dict, Any
import uvicorn
 
app = FastAPI(title="Mock Service Bus")

# List of available services
@app.get("/bus/services")
def bus_services() -> List[Dict[str, str]]:
    return [{"id": "svc-a"}, {"id": "svc-b"}]

# Capabilities per service
@app.get("/services/svc-a/capabilities")
def caps_a() -> Dict[str, Any]:
    return {"endpoints": [{"rel": "telemetry", "href": "/services/svc-a/telemetry"}]}

@app.get("/services/svc-b/capabilities")
def caps_b() -> Dict[str, Any]:
    return {"endpoints": [{"rel": "alerts", "href": "/services/svc-b/alerts"}]}

# Endpoint that the consumer will poll
@app.get("/services/svc-a/telemetry")
def telem_a():
    return [{"timestamp": "2025-08-18T10:00:00Z", "value": 42}]

@app.get("/services/svc-b/alerts")
def alerts_b():
    return {"timestamp": "2025-08-18T10:00:10Z", "value": "HIGH"}

if __name__ == "__main__":
    uvicorn.run("mock_bus:app", host="127.0.0.1", port=8001, reload=True)
