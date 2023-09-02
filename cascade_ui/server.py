from argparse import ArgumentParser
import glob
import logging
from typing import List
import os

from cascade.base import MetaHandler, supported_meta_formats
from cascade import models as cdm
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn


SCRIPT_DIR = os.path.dirname(__file__)


class Server:
    def __init__(self, path: str) -> None:
        meta_paths = glob.glob(os.path.join(path, "meta.*"))
        meta_paths = [
            path
            for path in meta_paths
            if os.path.splitext(path)[-1] in supported_meta_formats
        ]

        if len(meta_paths) != 1:
            raise ValueError(f"There are {len(meta_paths)} meta objects in {path}")
        else:
            meta = MetaHandler.read(meta_paths[0])

        if not isinstance(meta, list):
            raise ValueError(f"Metadata in {path} is not a list")

        meta_type = meta[0].get("type")
        if not meta_type:
            raise ValueError(f"No type key in meta in {path}")

        if meta_type != "workspace":
            raise ValueError(f"Cannot start UI in {type}, workspace only")

        self._ws_meta = meta
        self._ws = cdm.Workspace(path)

    async def root_page(self) -> HTMLResponse:
        root = os.path.join(os.path.dirname(SCRIPT_DIR), "web", "index.html")
        with open(root, "r") as f:
            html = f.read()
        return HTMLResponse(content=html)

    async def repos_page(self):
        return HTMLResponse()

    def _repo_lengths(self) -> List[int]:
        return [len(self._ws[name]) for name in self._ws.get_repo_names()]

    async def repos(self):
        self._ws.reload()
        return JSONResponse({
            "repos": [
                {
                    "name": name,
                    "len": length
                }
                for name, length in zip(
                    self._ws.get_repo_names(),
                    self._repo_lengths()
                )
            ]
        })


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    logger = logging.getLogger(__file__)

    parser = ArgumentParser()
    parser.add_argument(
        "--path", type=str, help="Path of the workspace where to start UI", default="."
    )
    args = parser.parse_args()

    cwd = os.path.abspath(args.path)
    logger.info(f"Starting in {cwd}")

    server = Server(cwd)

    app = FastAPI()
    app.add_api_route("/", server.root_page, methods=["get"])
    app.add_api_route("/repos", server.repos_page, methods=["get"])
    app.add_api_route("/v1/repos", server.repos, methods=["post", "get"])

    uvicorn.run(app)
