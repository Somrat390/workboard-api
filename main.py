from fastapi import FastAPI

app = FastAPI(
    title="WorkBoard API",
    description="A project and task management REST API.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
