from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Widget Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later — public config/submission endpoints need this open
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}