import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

from .assets import asset_path
from .error_handlers import clan_error_handler
from .routers import clan_modules, flake, health, machines, root
from .settings import settings
from .tags import tags_metadata

# Logging setup
log = logging.getLogger(__name__)


def setup_app() -> FastAPI:
    app = FastAPI()

    if settings.env.is_development():
        # Allow CORS in development mode for nextjs dev server
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(clan_modules.router)
    app.include_router(flake.router)
    app.include_router(health.router)
    app.include_router(machines.router)

    # Needs to be last in register. Because of wildcard route
    app.include_router(root.router)

    app.add_exception_handler(Exception, clan_error_handler)

    app.mount("/static", StaticFiles(directory=asset_path()), name="static")

    # Add tag descriptions to the OpenAPI schema
    app.openapi_tags = tags_metadata

    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'
        log.debug(f"Registered route: {route}")

    for i in app.exception_handlers.items():
        log.debug(f"Registered exception handler: {i}")

    return app


app = setup_app()
