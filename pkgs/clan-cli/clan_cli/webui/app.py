from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
import logging

from .. import custom_logger 
from .assets import asset_path
from .routers import flake, health, machines, root, vms

origins = [
    "http://localhost:3000",
]


def setup_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(flake.router)
    app.include_router(health.router)
    app.include_router(machines.router)
    app.include_router(root.router)
    app.include_router(vms.router)
    app.add_exception_handler(vms.NixBuildException, vms.nix_build_exception_handler)

    app.mount("/static", StaticFiles(directory=asset_path()), name="static")

    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'
    return app


custom_logger.register(logging.getLogger('uvicorn').level)
app = setup_app()

