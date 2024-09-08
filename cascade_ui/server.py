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
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles

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


class ModelRow(pydantic.BaseModel):
    name: str
    slug: str
    created_at: str
    saved_at: str


class LineResponse(Container):
    models: List[ModelRow]


class ModelPathSpec(pydantic.BaseModel):
    repo: str
    line: str
    num: int


# TODO: add cwd too
class ModelResponse(pydantic.BaseModel):
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
    python_version: str
    description: Union[str, None]
    comments: List[Dict[Any, Any]]
    tags: Union[str, List[str]]
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

        models = []
        model_names = line.get_model_names()
        for i, name in enumerate(model_names):
            meta = line.load_model_meta(i)
            model = ModelRow(
                name=name,
                slug=meta[0]["slug"],
                created_at=meta[0]["created_at"],
                saved_at=meta[0]["saved_at"],
            )
            models.append(model)
        return LineResponse(name=path.line, len=len(line), models=models)

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
            python_version=meta[0]["python_version"],
            description=meta[0]["description"],
            comments=meta[0]["comments"],
            tags=meta[0]["tags"],
            git_commit=meta[0]["git_commit"],
            git_uncommitted_changes=meta[0]["git_uncommitted_changes"],
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
    app.add_api_route("/v1/workspace", server.workspace, methods=["post"])
    app.add_api_route("/v1/repo", server.repo, methods=["post"])
    app.add_api_route("/v1/line", server.line, methods=["post"])
    app.add_api_route("/v1/model", server.model, methods=["post"])
    app.add_api_route("/v1/dataset", server.dataset, methods=["post"])
    app.mount(
        "/",
        StaticFiles(
            directory=os.path.join(module_dir, "UI", "dist"),
            html=True,
            check_dir=True,
        ),
        name="static",
    )
    uvicorn.run(app)
