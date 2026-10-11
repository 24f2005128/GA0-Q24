from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

DATA = [
    {"region":"apac","latency_ms":127.11,"uptime_pct":97.412},
    {"region":"apac","latency_ms":168.5,"uptime_pct":99.402},
    {"region":"apac","latency_ms":140.45,"uptime_pct":98.279},
    {"region":"apac","latency_ms":148.07,"uptime_pct":98.422},
    {"region":"apac","latency_ms":134.55,"uptime_pct":98.407},
    {"region":"apac","latency_ms":217.76,"uptime_pct":98.342},
    {"region":"apac","latency_ms":191.89,"uptime_pct":99.375},
    {"region":"apac","latency_ms":179.96,"uptime_pct":97.713},
    {"region":"apac","latency_ms":125.26,"uptime_pct":98.134},
    {"region":"apac","latency_ms":112.71,"uptime_pct":98.837},
    {"region":"apac","latency_ms":200.05,"uptime_pct":98.452},
    {"region":"apac","latency_ms":161.98,"uptime_pct":97.149},

    {"region":"emea","latency_ms":165.38,"uptime_pct":97.902},
    {"region":"emea","latency_ms":117.27,"uptime_pct":97.444},
    {"region":"emea","latency_ms":220.52,"uptime_pct":98.49},
    {"region":"emea","latency_ms":114.72,"uptime_pct":97.691},
    {"region":"emea","latency_ms":133.03,"uptime_pct":97.196},
    {"region":"emea","latency_ms":196.83,"uptime_pct":98.4},
    {"region":"emea","latency_ms":182.39,"uptime_pct":98.112},
    {"region":"emea","latency_ms":111.77,"uptime_pct":98.892},
    {"region":"emea","latency_ms":128.36,"uptime_pct":98.486},
    {"region":"emea","latency_ms":109.99,"uptime_pct":99.403},
    {"region":"emea","latency_ms":148.88,"uptime_pct":99.301},
    {"region":"emea","latency_ms":203.1,"uptime_pct":98.884},

    {"region":"amer","latency_ms":155.21,"uptime_pct":98.058},
    {"region":"amer","latency_ms":193.03,"uptime_pct":98.329},
    {"region":"amer","latency_ms":119.41,"uptime_pct":98.655},
    {"region":"amer","latency_ms":197.76,"uptime_pct":97.764},
    {"region":"amer","latency_ms":124.07,"uptime_pct":98.505},
    {"region":"amer","latency_ms":140.53,"uptime_pct":99.482},
    {"region":"amer","latency_ms":159.86,"uptime_pct":98.53},
    {"region":"amer","latency_ms":118.09,"uptime_pct":99.259},
    {"region":"amer","latency_ms":219.91,"uptime_pct":99.032},
    {"region":"amer","latency_ms":163.06,"uptime_pct":97.35},
    {"region":"amer","latency_ms":181.36,"uptime_pct":99.429},
    {"region":"amer","latency_ms":228.82,"uptime_pct":98.323},
]

class RequestData(BaseModel):
    regions: list[str]
    threshold_ms: float

def percentile(values, p):
    values = sorted(values)
    k = (len(values) - 1) * p
    f = int(k)
    c = k - f
    if f + 1 < len(values):
        return values[f] + (values[f + 1] - values[f]) * c
    return values[f]

@app.post("/")
def calculate(req: RequestData):
    result = {}

    for region in req.regions:
        rows = [r for r in DATA if r["region"] == region]
        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": percentile(latencies, 0.95),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(
                r["latency_ms"] > req.threshold_ms
                for r in rows
            ),
        }

    return result
