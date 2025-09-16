from fastapi import FastAPI
from .routers import text

app = FastAPI()

app.include_router(text.router)

@app.get("/")
def health():
    return {"status": "healthy"}

