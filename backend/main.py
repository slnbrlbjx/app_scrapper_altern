from fastapi import FastAPI

from api.routes.jobs import router as jobs_router

app = FastAPI()

app.include_router(jobs_router)


@app.get("/")
def root():
    return {
        "status": "running"
    }