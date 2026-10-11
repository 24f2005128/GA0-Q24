from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import statistics
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float

with open("q-vercel-latency.json", "r") as f:
    DATA = json.load(f)

def p95(values):
    values = sorted(values)
    r = (len(values) - 1) * 0.95
    n = int(r)
    fraction = r - n

    if n + 1 < len(values):
        return values[n] + fraction * (values[n + 1] - values[n])

    return values[n]

@app.options("/")
async def options():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

@app.post("/")
async def calculate(req: RequestBody):
    result = {}

    for region in req.regions:
        rows = [
            r for r in DATA
            if r["region"] == region
        ]

        latencies = [
            r["latency_ms"]
            for r in rows
        ]

        uptimes = [
            r["uptime_pct"]
            for r in rows
        ]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(
                r["latency_ms"] > req.threshold_ms
                for r in rows
            ),
        }

    return JSONResponse(
        content=result,
        headers={
            "Access-Control-Allow-Origin": "*",
        },
    )
