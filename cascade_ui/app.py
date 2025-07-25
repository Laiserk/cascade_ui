"""
Copyright 2023-2025 Oleg Sevostyanov, Ilia Moiseev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from . import __version__
from .server import Server


def run(path: str, host: str, port: int):
    logging.basicConfig(level="INFO")
    logger = logging.getLogger(__file__)

    cwd = os.path.abspath(path)
    logger.info(f"Starting in {cwd}")

    server = Server(cwd)

    package_dir = os.path.dirname(os.path.abspath(__file__))

    app = FastAPI(title="CascadeUI Backend", version=__version__)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_api_route("/v1/workspace", server.workspace, methods=["post"])
    app.add_api_route("/v1/repo", server.repo, methods=["post"])
    app.add_api_route("/v1/line", server.line, methods=["post"])
    app.add_api_route("/v1/model", server.model, methods=["post"])
    app.add_api_route("/v1/run_log", server.run_log, methods=["post"])
    app.add_api_route("/v1/run_config", server.run_config, methods=["post"])
    app.add_api_route("/v1/dataset", server.dataset, methods=["post"])
    app.add_api_route("/v1/version", server.version, methods=["get"])
    app.add_api_route("/v1/line_item_table", server.line_item_table, methods=["post"])
    app.add_api_route("/v1/add_comment", server.add_comment, methods=["post"])
    app.add_api_route(
        "/v1/search/item/suggestions", server.item_search_suggestions, methods=["post"]
    )

    app.mount(
        "/assets",
        StaticFiles(
            directory=os.path.join(package_dir, "web", "dist", "assets"),
            html=False,
            check_dir=True,
        ),
        name="assets",
    )

    app.mount(
        "/logo.svg",
        StaticFiles(
            directory=os.path.join(package_dir, "web", "dist"),
            html=False,
            check_dir=True,
        ),
        name="favicon",
    )

    @app.get("/{full_path:path}")
    async def fallback(full_path: str, request: Request):
        if (
            request.method == "GET"
            and not full_path.startswith("v1/")
            and not full_path.startswith("assets/")
            and full_path != "favicon.ico"
        ):
            index_path = os.path.join(package_dir, "web", "dist", "index.html")
            return FileResponse(index_path)
        return Response(status_code=404)

    uvicorn.run(app, host=host, port=port)
