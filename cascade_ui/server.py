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
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import pydantic
import uvicorn
from cascade import __version__ as cascade_version
from cascade.base import MetaHandler, supported_meta_formats
from cascade.lines import DataLine, ModelLine
from cascade.workspaces import Workspace
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from . import __version__

SCRIPT_DIR = os.path.dirname(__file__)

CLS2TYPE = {DataLine: "data_line", ModelLine: "model_line"}


class Container(pydantic.BaseModel):
    name: str
    len: int


class WorkspaceResponse(Container):
    repos: List[Container]


class RepoPathSpec(pydantic.BaseModel):
    repo: str


class LineRow(Container):
    type: str
    created_at: str
    updated_at: str


class RepoResponse(Container):
    lines: List[LineRow]


class LinePathSpec(pydantic.BaseModel):
    repo: str
    line: str


class Item(pydantic.BaseModel):
    name: str
    slug: Optional[str] = None
    created_at: Optional[str] = None
    saved_at: str


class LineResponse(Container):
    items: List[Item]


class ModelPathSpec(pydantic.BaseModel):
    repo: str
    line: str
    num: int


class Comment(pydantic.BaseModel):
    id: str
    user: str
    host: str
    timestamp: str
    message: str


class Metric(pydantic.BaseModel):
    name: str
    value: Optional[float] = None
    dataset: Optional[str] = None
    split: Optional[str] = None
    direction: Optional[Literal["up", "down"]] = None
    interval: Optional[Tuple[float, float]] = None
    extra: Optional[Dict[str, Any]] = None


class ModelResponse(pydantic.BaseModel):
    slug: str
    path: str
    created_at: str
    saved_at: str
    user: str
    host: str
    cwd: str
    python_version: str
    description: Union[str, None]
    comments: List[Comment]
    tags: List[str]
    params: Dict[str, Any]
    metrics: List[Metric]
    artifacts: List[str]
    files: List[str]
    git_commit: Optional[str] = None
    git_uncommitted_changes: Optional[List[str]] = None


class DatasetPathSpec(pydantic.BaseModel):
    repo: str
    line: str
    ver: str


class DatasetResponse(pydantic.BaseModel):
    name: str
    path: str
    saved_at: str
    user: str
    host: str
    cwd: str
    python_version: str
    description: Union[str, None]
    comments: List[Dict[Any, Any]]
    tags: Union[str, List[str]]
    git_commit: Optional[str] = None
    git_uncommitted_changes: Optional[List[str]] = None


class VersionResponse(pydantic.BaseModel):
    cascade_ml_version: str
    cascade_ui_version: str


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
        self._ws_name = self._ws.get_root()

    def workspace(self) -> WorkspaceResponse:
        repo_names = self._ws.get_repo_names()
        repo_lengths = [len(self._ws[name]) for name in repo_names]

        repos = [Container(name=name, len=length) for name, length in zip(repo_names, repo_lengths)]

        return WorkspaceResponse(name=self._ws_name, len=len(repos), repos=repos)

    def repo(self, path: RepoPathSpec) -> RepoResponse:
        r = self._ws[path.repo]
        names = r.get_line_names()
        lines = [r[line] for line in names]

        line_rows = []
        for name, line in zip(names, lines):
            t = CLS2TYPE[type(line)]
            meta = line.load_meta()
            row = LineRow(
                name=name,
                len=len(line),
                type=t,
                created_at=meta[0]["created_at"],
                updated_at=meta[0]["updated_at"],
            )
            line_rows.append(row)

        return RepoResponse(name=path.repo, len=len(lines), lines=line_rows)

    def line(self, path: LinePathSpec) -> LineResponse:
        line = self._ws[path.repo][path.line]

        items = []
        item_names = line.get_item_names()
        for i, name in enumerate(item_names):
            meta = line.load_obj_meta(i)
            item = Item(
                name=name,
                slug=meta[0].get("slug"),
                created_at=meta[0].get("created_at"),
                saved_at=meta[0]["saved_at"],
            )
            items.append(item)
        return LineResponse(name=path.line, len=len(line), items=items)

    def model(self, path: ModelPathSpec) -> ModelResponse:
        line = self._ws[path.repo][path.line]
        meta = line.load_model_meta(path.num)
        files = line.load_artifact_paths(path.num)

        return ModelResponse(
            slug=meta[0]["slug"],
            path=meta[0]["path"],
            created_at=meta[0]["created_at"],
            saved_at=meta[0]["saved_at"],
            user=meta[0]["user"],
            host=meta[0]["host"],
            cwd=meta[0]["cwd"],
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

    def dataset(self, path: DatasetPathSpec) -> DatasetResponse:
        line = self._ws[path.repo].add_line(path.line, line_type="data")
        meta = line.load_obj_meta(path.ver)

        return DatasetResponse(
            name=path.ver,
            path=meta[0]["path"],
            saved_at=meta[0]["saved_at"],
            user=meta[0]["user"],
            host=meta[0]["host"],
            cwd=meta[0]["cwd"],
            python_version=meta[0]["python_version"],
            description=meta[0]["description"],
            comments=meta[0]["comments"],
            tags=meta[0]["tags"],
            git_commit=meta[0]["git_commit"],
            git_uncommitted_changes=meta[0]["git_uncommitted_changes"],
        )

    def version(self):
        return VersionResponse(
            cascade_ml_version=cascade_version,
            cascade_ui_version=__version__,
        )


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
    app.add_api_route("/v1/dataset", server.dataset, methods=["post"])
    app.add_api_route("/v1/version", server.version, methods=["get"])

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
