from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from dependency_injector.wiring import inject, Provide
from typing import Any

from fastapi.routing import APIRoute
from uvicorn import Config, Server
from starlette.responses import RedirectResponse

from service_core.server.routes import create_api_route, ApiKeyLogAPIRoute, LogAPIRoute, load_routes
from service_core.containers.containers import Application
from service_core.server.exception_handlers import validation_exception_handler
from service_core.config.log_configuration import setup_logging
import logging

def get_route_class(enable_logs, enable_apikey_check):
    route_class = APIRoute
    if enable_apikey_check:
        route_class = ApiKeyLogAPIRoute
    elif enable_logs:
        route_class = LogAPIRoute
    return route_class


class RestServer(FastAPI):
    def __init__(self,name: str,version: str = "1.0",description: str = "",
                prefix: str = Provide[Application.config.core.server.prefix],
                apikey: str = Provide[Application.config.core.auth.xapikey],
                app_insight_conn_str: str = Provide[
                Application.config.services.azure.app_insights.connection_string],
                 **extra: Any):
            super().__init__(title=name,version=version,
                             description=description,
                             # root_path="/sd-edi",
                             openapi_url=prefix + "/openapi.json",
                             docs_url=prefix + "/docs",
                             redoc_url=prefix + "/redoc",
                             **extra)
            self.prefix = prefix
            self.apikey = apikey
            self._configure()

            default_routes = [
                create_api_route('/ping', self._ping, methods=['GET']),
                create_api_route(prefix + '/openapi.json', self._openapi, methods=['GET']),
                create_api_route(prefix, self._redirect, methods=['GET'],
                                 include_in_schema=False)
            ]
            self.add_router(routes=default_routes, tags=["default"],
                            enable_apikey_check=False, enable_logs=False,
                            no_root_prefix=True)

            #self.on_event('startup')(lambda: setup_azure_logging(app_insight_conn_str, prefix))


    def _ping(self):
        return "Alive"


    def _openapi(self):
        return self.openapi()


    def _redirect(self):
        return RedirectResponse(self.prefix + "/docs")


    def _configure(self):
        self.add_exception_handler(RequestValidationError, validation_exception_handler)


    def add_router(self, routes, prefix="", tags=[],
                   enable_apikey_check=True,
                   enable_logs=True,
                   no_root_prefix=False):
        router = APIRouter(
            prefix=prefix if no_root_prefix else self.prefix + prefix,
            route_class=get_route_class(enable_logs, enable_apikey_check)
        )

        route_tags = tags
        for route in routes:
            router.add_api_route(route.path, route.endpoint,
                                 methods=route.methods,
                                 response_model=route.response_model,
                                 include_in_schema=route.include_in_schema)
            route_tags += route.tags
        router.tags = route_tags
        self.include_router(router)


    def log_routes(self):
        for route in self.routes:
            logging.debug(
                f"Configuring Route - Path: {route.path}, Methods: {route.methods}")


    def run(self,
            host: str = "0.0.0.0",
            port: int = 5000,
            workers: int = 1,
            log_level: str = Provide[Application.config.core.log_level]):
            server = Server(
                Config(
                    app=self,
                    host=host,
                    port=port,
                    workers=workers,
                    lifespan="on",
                    reload=True
                ),
            )

            # setup logging last, to make sure no library overwrites it
            # (they shouldn't, but it happens)
            setup_logging(log_level)

            self.log_routes()
            server.run()