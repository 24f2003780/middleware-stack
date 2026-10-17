
import time
import uuid
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

EMAIL = "24f2003780@ds.study.iitm.ac.in"

ALLOWED_ORIGINS = [
    "https://app-n6bf67.example.com",
    "https://exam.sanand.workers.dev",
]

requests_by_client = defaultdict(deque)


@app.middleware("http")
async def middleware_stack(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.scope["request_id"] = request_id

    if request.url.path == "/ping" and request.method == "GET":
        client_id = request.headers.get("X-Client-Id", "anonymous")
        now = time.monotonic()
        bucket = requests_by_client[client_id]

        while bucket and now - bucket[0] >= 10:
            bucket.popleft()

        if len(bucket) >= 10:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"X-Request-ID": request_id},
            )

        bucket.append(now)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["X-Request-ID", "X-Client-Id"],
)


@app.get("/")
async def home():
    return {"status": "ok", "email": EMAIL}


@app.get("/ping")
async def ping(request: Request):
    return {
        "email": EMAIL,
        "request_id": request.scope["request_id"],
    }


@app.get("/q13")
async def q13():
    return {
        "A": {
            "text": "Report job-907ecd7b: café\nReady ✓",
            "complete": True,
            "error": None,
        },
        "B": {
            "text": "Partial job-907ecd7b",
            "complete": False,
            "error": None,
        },
        "C": {
            "text": "Draft job-907ecd7b",
            "complete": False,
            "error": "model unloaded",
        },
    }


@app.get("/q14")
async def q14():
    return {
        "A": {"steps": ["L3", "L4", "L5"], "seconds": 43},
        "B": {"steps": ["L1", "L2", "L3", "L4", "L5"], "seconds": 93},
        "C": {"steps": [], "seconds": 0},
        "D": {"steps": [], "seconds": 0},
        "E": {"steps": ["L4", "L5"], "seconds": 43},
    }
