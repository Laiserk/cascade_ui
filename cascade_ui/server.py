"""
Copyright 2023-2024 Oleg Sevostyanov, Ilia Moiseev

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


import glob
import logging
import os
from argparse import ArgumentParser
from typing import Any, Dict, List, Union

import pydantic
import uvicorn
from cascade import models as cdm
from cascade.base import MetaHandler, supported_meta_formats
from fastapi import FastAPI
from fastapi.responses import JSONResponse

SCRIPT_DIR = os.path.dirname(__file__)


class Container(pydantic.BaseModel):
    name: str
    len: int


class Repo(pydantic.BaseModel):
    name: str


class ModelPathSpec(pydantic.BaseModel):
    repo: str
    line: str
    num: int


class Model(pydantic.BaseModel):
    path: str
    slug: str
    description: Union[str, None]
    tags: Union[str, List[str]]
    created_at: str
    saved_at: str
    metrics: Dict[str, Any]
    params: Dict[str, Any]
    comments: List[Dict[Any, Any]]
    meta: List[Dict[str, Any]]
    artifacts: List[str]
    files: List[str]


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

    async def repos(self) -> List[Container]:
        repo_names = self._ws.get_repo_names()
        repo_lengths = [len(self._ws[name]) for name in repo_names]

        return [
                Container(name=name, len=length)
                for name, length in zip(repo_names, repo_lengths)
            ]

    async def lines(self, repo: Repo) -> List[Container]:
        repo = self._ws[repo.name]
        line_names = repo.get_line_names()
        line_lengths = [len(repo[line]) for line in line_names]

        return [
                Container(name=name, len=length)
                for name, length in zip(line_names, line_lengths)
            ]

    async def model(self, ps: ModelPathSpec) -> Model:
        line = self._ws[ps.repo][ps.line]
        meta = line.load_model_meta(ps.num)
        files = line.load_artifact_paths(ps.num)

        return Model(
            path=meta[0]["path"],
            slug=meta[0]["slug"],
            description=meta[0]["description"],
            tags=meta[0]["tags"],
            created_at=meta[0]["created_at"],
            saved_at=meta[0]["saved_at"],
            metrics=meta[0]["metrics"],
            params=meta[0]["params"],
            comments=meta[0]["comments"],
            meta=meta,
            artifacts=files["artifacts"],
            files=files["files"],
        )


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

    app = FastAPI(title="CascadeUI Backend")
    app.add_api_route("/v1/repos", server.repos, methods=["post"])
    app.add_api_route("/v1/lines", server.lines, methods=["post"])
    app.add_api_route("/v1/model", server.model, methods=["post"])

    uvicorn.run(app)
