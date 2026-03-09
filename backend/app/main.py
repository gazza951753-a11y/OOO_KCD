from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audit, auth, documents, reports, timekeeping, users

app = FastAPI(
    title="ООО КЦД — Кадровая система",
    description="HR-система с модулями табельного учёта, документооборота, отчётности и аудита",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(timekeeping.router, prefix=API_PREFIX)
app.include_router(documents.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(audit.router, prefix=API_PREFIX)


@app.get("/api/health")
def health():
    return {"status": "ok"}
