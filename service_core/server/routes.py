import logging
from typing import Callable
import re
from uuid import uuid4

from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from service_core.server.security import verify


class LogAPIRoute(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request_id = str(uuid4())

            req_log_str = "Request - "
            req_log_str += f"Path: {request.scope['path']}, "
            req_log_str += f"Method: {request.method}, "
            req_log_str += f"Headers: {request.headers}, "
            req_log_str += f"PathParams: {request.path_params}, "
            req_log_str += f"QueryParams: {request.query_params}, "
            body = (await request.body()).decode('utf-8')
            body = body.replace("\n","").replace("\r", "")
            body = re.sub(r" +", " ", body, 0, re.MULTILINE)
            req_log_str += f"Body: {body}"
            logging.debug(req_log_str)

            response: Response = await original_route_handler(request)
            response.headers["RequestId"] = request_id

            res_log_str = "Response - "
            res_log_str += f"StatusCode: {response.status_code}, "
            res_log_str += f"Headers: {response.headers}, "
            res_log_str += f"Body: {response.body.decode('utf-8')}"
            logging.debug(res_log_str)
            return response
        return custom_route_handler


class ApiKeyLogAPIRoute(LogAPIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            apikey = request.app.apikey
            if "x-api-key" in request.headers and verify(apikey, request.headers["x-api-key"]):
                response: Response = await original_route_handler(request)
                return response
            else:
                raise HTTPException(status_code=403)

        return custom_route_handler


def create_api_route(path, handler, response_model=None, methods=["POST"],
                     tags=[], include_in_schema=True):
    return LogAPIRoute(path, handler, tags=tags,
                       response_model=response_model, methods=methods,
                       include_in_schema=include_in_schema)

def load_routes():
    routes = []
    return routes