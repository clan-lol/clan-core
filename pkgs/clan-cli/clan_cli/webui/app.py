import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from .. import custom_logger
from .assets import asset_path
from .routers import flake, health, machines, root, vms

origins = [
    "http://localhost:3000",
]
# Logging setup
log = logging.getLogger(__name__)


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
    app.include_router(vms.router)

    # Needs to be last in register. Because of wildcard route
    app.include_router(root.router)

    app.add_exception_handler(vms.NixBuildException, vms.nix_build_exception_handler)

    app.mount("/static", StaticFiles(directory=asset_path()), name="static")

    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'
        log.debug(f"Registered route: {route}")
    return app


# TODO: How do I get the log level from the command line in here?
custom_logger.register(logging.DEBUG)
app = setup_app()

for i in app.exception_handlers.items():
    log.info(f"Registered exception handler: {i}")

log.warn("log warn")
log.debug("log debug")
