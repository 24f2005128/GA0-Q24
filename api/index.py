from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: float

# Paste the telemetry records from the downloaded sample bundle here.
DATA = []

@app.post("/")
def metrics(req: RequestData):
    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]
        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": statistics.quantiles(latencies, n=100)[94],
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(x > req.threshold_ms for x in latencies),
        }

    return result
