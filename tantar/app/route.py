from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import logfire


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
