from fastapi import FastAPI
from app.database import Base, engine
from app.routers import trees, monitoring, risk, audit

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TreePassport Technology Enhancement API")

app.include_router(trees.router)
app.include_router(monitoring.router)
app.include_router(risk.router)
app.include_router(audit.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "treepassport-enhancement-api"}
