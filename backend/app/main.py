from fastapi import FastAPI
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TreePassport Technology Enhancement API")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "treepassport-enhancement-api"}
