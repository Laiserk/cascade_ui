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
from typing import Any, Dict, List, Optional, Union

import pydantic
import uvicorn
from cascade.base import MetaHandler, supported_meta_formats
from cascade.lines import DataLine, ModelLine
from cascade.workspaces import Workspace
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

SCRIPT_DIR = os.path.dirname(__file__)

CLS2TYPE = {DataLine: "data_line", ModelLine: "model_line"}


class Container(pydantic.BaseModel):
    name: str
    type: str
    len: int


class Repo(pydantic.BaseModel):
    name: str


class ModelPathSpec(pydantic.BaseModel):
    repo: str
    line: str
    num: int


class Model(pydantic.BaseModel):
    slug: str
    path: str
    created_at: str
    saved_at: str
    user: str
    host: str
    python_version: str
    description: Union[str, None]
    comments: List[Dict[Any, Any]]
    tags: Union[str, List[str]]
    params: Dict[str, Any]
    metrics: List[Dict[str, Any]]
    artifacts: List[str]
    files: List[str]
    git_commit: Optional[str] = None
    git_uncommitted_changes: Optional[List[str]] = None


class Server:
    def __init__(self, path: str) -> None:
        meta_paths = glob.glob(os.path.join(path, "meta.*"))
        meta_paths = [
            path for path in meta_paths if os.path.splitext(path)[-1] in supported_meta_formats
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
            raise ValueError(f"Cannot start UI in {type}, workspaces only")

        self._ws_meta = meta
        self._ws = Workspace(path)

    def repos(self) -> List[Container]:
        repo_names = self._ws.get_repo_names()
        repo_lengths = [len(self._ws[name]) for name in repo_names]

        return [
            Container(name=name, type="repo", len=length)
            for name, length in zip(repo_names, repo_lengths)
        ]

    def lines(self, repo: Repo) -> List[Container]:
        repo = self._ws[repo.name]
        names = repo.get_line_names()
        lines = [repo[line] for line in names]
        types = [CLS2TYPE[type(line)] for line in lines]
        lens = [len(line) for line in lines]

        return [
            Container(name=name, type=type_, len=length)
            for name, type_, length in zip(names, types, lens)
        ]

    def model(self, ps: ModelPathSpec) -> Model:
        line = self._ws[ps.repo][ps.line]
        meta = line.load_model_meta(ps.num)
        files = line.load_artifact_paths(ps.num)

        return Model(
            slug=meta[0]["slug"],
            path=meta[0]["path"],
            created_at=meta[0]["created_at"],
            saved_at=meta[0]["saved_at"],
            user=meta[0]["user"],
            host=meta[0]["host"],
            python_version=meta[0]["python_version"],
            description=meta[0]["description"],
            comments=meta[0]["comments"],
            tags=meta[0]["tags"],
            params=meta[0]["params"],
            metrics=meta[0]["metrics"],
            artifacts=files["artifacts"],
            files=files["files"],
            git_commit=meta[0]["git_commit"] if "git_commit" in meta[0] else None,
            git_uncommitted_changes=(
                meta[0]["git_uncommitted_changes"] if "git_uncommitted_changes" in meta[0] else None
            ),
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

    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = FastAPI(title="CascadeUI Backend")
    app.mount(
        "/ui",
        StaticFiles(directory=os.path.join(module_dir, "UI", "dist"), html=True),
        name="static",
    )
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(module_dir, "UI", "dist", "assets"), html=True),
        name="static",
    )
    app.add_api_route("/v1/repos", server.repos, methods=["post"])
    app.add_api_route("/v1/lines", server.lines, methods=["post"])
    app.add_api_route("/v1/model", server.model, methods=["post"])

    uvicorn.run(app)
