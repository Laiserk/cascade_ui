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

import glob
import json
import os
import warnings
from typing import Any, Dict, List

from cascade import __version__ as cascade_version
from cascade.base import MetaHandler, ZeroMetaError, supported_meta_formats
from cascade.base.utils import flatten_dict
from cascade.lines import DataLine, ModelLine
from cascade.workspaces import Workspace

from . import __version__
from .models import (
    ConfigResponse,
    Container,
    DatasetPathSpec,
    DatasetResponse,
    Item,
    LinePathSpec,
    LineResponse,
    LineRow,
    LogResponse,
    ModelPathSpec,
    ModelResponse,
    RepoPathSpec,
    RepoResponse,
    VersionResponse,
    WorkspaceResponse,
)

SCRIPT_DIR = os.path.dirname(__file__)

CLS2TYPE = {DataLine: "data_line", ModelLine: "model_line"}


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
        self._ws = Workspace(self._ws_name)
        ws_meta = self._ws.get_meta()
        repo_names = self._ws.get_repo_names()
        repo_lengths = [len(self._ws[name]) for name in repo_names]

        repos = [Container(name=name, len=length) for name, length in zip(repo_names, repo_lengths)]

        return WorkspaceResponse(
            name=self._ws_name,
            len=len(repos),
            repos=repos,
            tags=ws_meta[0].get("tags"),
            comments=ws_meta[0].get("comments"),
        )

    def repo(self, path: RepoPathSpec) -> RepoResponse:
        r = self._ws[path.repo]
        repo_meta = r.get_meta()
        names = r.get_line_names()
        lines = [r[line] for line in names]

        line_rows = []
        for name, line in zip(names, lines):
            t = CLS2TYPE[type(line)]
            meta = line.load_meta()

            created_at = meta[0].get("created_at")
            updated_at = meta[0].get("updated_at")

            if not created_at or not updated_at:
                warnings.warn(f"No created_at or updated_at in line {name}")
                continue

            row = LineRow(
                name=name,
                len=len(line),
                type=t,
                created_at=created_at,
                updated_at=updated_at,
            )
            line_rows.append(row)

        return RepoResponse(
            name=path.repo,
            len=len(lines),
            lines=line_rows,
            tags=repo_meta[0].get("tags"),
            comments=repo_meta[0].get("comments"),
        )

    def _prepare_item_dict(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        meta = meta[0]
        flat = flatten_dict(meta, separator=".", root_keys_to_ignore=("tags", "metrics"))

        metrics = flat.pop("metrics", [])
        for metric in metrics:
            name = metric["name"]
            for key in ["dataset", "split"]:
                part = metric.get(key)
                name += "_" + part if part else ""
            flat[f"metrics.{name}"] = metric["value"]

        return flat

    def _get_item_fields(self, meta: List[Dict[str, Any]]) -> List[str]:
        def keys_filter(key: str) -> bool:
            if key.startswith(("comments", "git_uncommitted_changes", "links")):
                return False
            if key in ("name", "slug", "tags", "saved_at", "created_at"):
                return False
            return True

        flat = self._prepare_item_dict(meta)
        keys = list(filter(keys_filter, flat.keys()))
        return keys

    def line_item_table(
        self, line_path: LinePathSpec, item_fields: List[str]
    ) -> List[Dict[str, Any]]:
        line = self._ws[line_path.repo][line_path.line]
        items = []
        for i in range(len(line)):
            try:
                meta = line.load_obj_meta(i)
            except ZeroMetaError:
                continue
            item = {}
            flat = self._prepare_item_dict(meta)
            for key in item_fields:
                value = flat.get(key)
                item[key] = value
            items.append(item)
        return items

    def line(self, path: LinePathSpec) -> LineResponse:
        line = self._ws[path.repo][path.line]
        line_meta = line.get_meta()

        items = []
        item_names = line.get_item_names()
        item_fields = set()
        for i, name in enumerate(item_names):
            try:
                meta = line.load_obj_meta(i)
                item_fields.update(self._get_item_fields(meta))
            except ZeroMetaError:
                continue
            item = Item(
                name=name,
                slug=meta[0].get("slug"),
                tags=meta[0].get("tags"),
                created_at=meta[0].get("created_at"),
                saved_at=meta[0]["saved_at"],
            )
            items.append(item)
        return LineResponse(
            name=path.line,
            len=len(line),
            type=CLS2TYPE[type(line)],
            comments=line_meta[0].get("comments"),
            tags=line_meta[0].get("tags"),
            items=items,
            item_fields=list(sorted(item_fields)),
        )

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
            cwd=meta[0].get("cwd"),
            python_version=meta[0]["python_version"],
            description=meta[0]["description"],
            comments=meta[0]["comments"],
            tags=meta[0]["tags"],
            params=meta[0]["params"],
            metrics=meta[0]["metrics"],
            artifacts=files["artifacts"],
            files=files["files"],
            git_commit=meta[0].get("git_commit"),
            git_uncommitted_changes=meta[0].get("git_uncommitted_changes"),
        )

    def run_log(self, path: ModelPathSpec) -> LogResponse:
        log_file = os.path.join(
            self._ws_name, path.repo, path.line, f"{path.num:0>5d}", "files", "cascade_run.log"
        )
        log_text = None
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                log_text = "\n".join(f.readlines())

        return LogResponse(log_text=log_text)

    def run_config(self, path: ModelPathSpec) -> ConfigResponse:
        config_file = os.path.join(
            self._ws_name, path.repo, path.line, f"{path.num:0>5d}", "files", "cascade_config.json"
        )
        overrides_file = os.path.join(
            self._ws_name,
            path.repo,
            path.line,
            f"{path.num:0>5d}",
            "files",
            "cascade_overrides.json",
        )
        config = None
        overrides = None

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = json.load(f)

        if os.path.exists(overrides_file):
            with open(overrides_file, "r") as f:
                overrides = json.load(f)

        return ConfigResponse(config=config, overrides=overrides)

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
