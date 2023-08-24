from fastapi import FastAPI

from .routers import health, root

app = FastAPI()
app.include_router(health.router)
app.include_router(root.router)
