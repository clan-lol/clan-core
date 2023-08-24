from fastapi import FastAPI

from .routers import health, machines, root

app = FastAPI()
app.include_router(health.router)
app.include_router(machines.router)
app.include_router(root.router)
