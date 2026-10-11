from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = [
    # paste the telemetry records from q-vercel-latency.json here
]

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

def p95(values):
    values = sorted(values)
    k = (len(values) - 1) * 0.95
    f = int(k)
    c = min(f + 1, len(values) - 1)
    return values[f] + (values[c] - values[f]) * (k - f)

@app.post("/")
def calculate(req: RequestBody):
    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(
                r["latency_ms"] > req.threshold_ms for r in rows
            ),
        }

    return result
