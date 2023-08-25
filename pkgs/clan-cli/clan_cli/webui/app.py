from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from .assets import asset_path
from .config import settings
from .routers import health, machines, root


def setup_app() -> FastAPI:
    app = FastAPI()
    app.include_router(health.router)
    app.include_router(machines.router)
    app.include_router(root.router)

    if settings.env.is_development():
        # TODO make this configurable
        app.add_middleware(
            CORSMiddleware,
            allow_origins="http://${settings.dev_host}:${settings.dev_port}",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.mount("/static", StaticFiles(directory=asset_path()), name="static")

    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'
    return app


app = setup_app()
