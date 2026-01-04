import logfire
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


logfire_token = os.getenv("LOGFIRE_TOKEN")
if not logfire_token:
    raise RuntimeError("LOGFIRE_TOKEN is required to start the API")
logfire.configure(token=logfire_token)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logfire.instrument_fastapi(app)

@app.get("/health")
async def health():
    return {"status": "ok"}
