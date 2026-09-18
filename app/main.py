from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.rate_limit import limiter
from app.routers import auth as auth_router, widgets as widgets_router, delivery as delivery_router, submissions as submissions_router

app = FastAPI(title="Widget Platform")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(widgets_router.router)
app.include_router(delivery_router.router)
app.include_router(submissions_router.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/health")
def health():
    return {"status": "ok"}