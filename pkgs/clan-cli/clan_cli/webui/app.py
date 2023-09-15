from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from .assets import asset_path
from .routers import health, machines, root, vms


def setup_app() -> FastAPI:
    app = FastAPI()
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


app = setup_app()
