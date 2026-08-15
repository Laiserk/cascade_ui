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
import time
import warnings
from typing import Any, Dict, Iterator, List, Optional

from cascade import __version__ as cascade_version
from cascade.base import (
    MetaHandler,
    MetaIOError,
    TraceableOnDisk,
    ZeroMetaError,
    supported_meta_formats,
)
from cascade.base.utils import flatten_dict
from cascade.lines import DataLine, ModelLine
from cascade.workspaces import Workspace

from . import __version__
from .models import (
    AddCommentRequest,
    CompareColumn,
    CompareRequest,
    CompareResponse,
    ConfigResponse,
    DatasetPathSpec,
    DatasetResponse,
    File,
    Item,
    ItemSearchRequest,
    ItemSuggestion,
    ItemSuggestions,
    LinePathSpec,
    LineResponse,
    LineRow,
    LogResponse,
    ModelPathSpec,
    ModelResponse,
    RepoCard,
    RepoPathSpec,
    RepoResponse,
    VersionResponse,
    WorkspaceResponse,
)

SCRIPT_DIR = os.path.dirname(__file__)

CLS2TYPE = {DataLine: "data_line", ModelLine: "model_line"}

ITEM_INDEX_TTL_SEC = 60

ITEM_BASE_FIELDS = ("name", "slug", "tags", "created_at", "saved_at")


class TimedCache:
    def __init__(self, ttl_sec: float):
        self.ttl_sec = ttl_sec
        self.cache = {}

    def add(self, key: str, value: Any) -> None:
        self.cache[key] = {"value": value, "time": time.time()}

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self.cache:
            return default

        item = self.cache[key]

        if time.time() - item["time"] > self.ttl_sec:
            del self.cache[key]
            return default
        else:
            self.cache[key]["time"] = time.time()

        return item["value"]


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
            raise ValueError(f"Cannot start UI in {type}, workspaces only")

        self._ws_meta = meta
        self._ws = Workspace(path)
        self._ws_name = self._ws.get_root()
        self._timed_cache = TimedCache(ITEM_INDEX_TTL_SEC)

    def add_comment(self, req: AddCommentRequest):
        path = os.path.join(self._ws_name, *req.path_parts)
        tr = TraceableOnDisk(path, meta_fmt=".json")
        tr.comment(req.comment)

    def workspace(self) -> WorkspaceResponse:
        self._ws = Workspace(self._ws_name)
        ws_meta = self._ws.get_meta()

        repos = []
        for name in self._ws.get_repo_names():
            repo = self._ws[name]
            meta = repo.get_meta()
            card = RepoCard(name=name, len=len(repo), tags=meta[0].get("tags"))
            repos.append(card)

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
                tags=meta[0].get("tags"),
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
        flat = flatten_dict(
            meta, separator=".", root_keys_to_ignore=("tags", "metrics")
        )

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
            if key in ITEM_BASE_FIELDS:
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
                if key == "num":
                    value = i
                else:
                    value = flat.get(key)
                item[key] = value
            items.append(item)
        return items

    def _filter_plot_fields(self, field_name):
        if field_name.startswith(("metrics", "params")):
            return True
        return False

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
            plot_fields=list(sorted(filter(self._filter_plot_fields, item_fields))),
        )

    def _read_slug(self, repo_name: str, line_name: str, item_name: str) -> str:
        slug_path = os.path.join(self._ws_name, repo_name, line_name, item_name, "SLUG")
        with open(slug_path, "r") as f:
            return f.read().strip()

    def iterate_over_items(self) -> Iterator[ItemSuggestion]:
        """
        Walks over every model in workspace. Datalines are skipped for now
        """

        for repo_name in self._ws.get_repo_names():
            repo = self._ws[repo_name]
            for line_name in repo.get_line_names():
                line = repo[line_name]
                if CLS2TYPE.get(type(line)) != "model_line":
                    continue
                for item_name in line.get_item_names():
                    num = int(item_name)
                    yield ItemSuggestion(
                        path="/".join((repo_name, line_name, item_name)),
                        repo=repo_name,
                        line=line_name,
                        name=item_name,
                        num=num,
                        slug=self._read_slug(repo_name, line_name, item_name),
                    )

    def _get_item_index(self) -> List[ItemSuggestion]:
        index = self._timed_cache.get("item_index")
        if index is None:
            index = list(self.iterate_over_items())
            self._timed_cache.add("item_index", index)
        return index

    def _match_item(self, query: str, item: ItemSuggestion) -> bool:
        """
        Matches a query against an item path segment-wise.

        The query is either head-anchored or tail-anchored: every segment except
        the last one must match a whole path segment, the last one is a prefix.
        This way ``00003`` finds a model named ``00003`` in any line, but does not
        match a line with the same name, and mid-segment queries do not match.
        Slugs are matched as substrings.
        """

        query = query.strip().strip("/").lower()
        if not query:
            return True

        if item.slug and query in item.slug.lower():
            return True

        parts = query.split("/")
        segments = item.path.lower().split("/")
        if len(parts) > len(segments):
            return False

        def aligned(offset: int) -> bool:
            for i, part in enumerate(parts[:-1]):
                if part != segments[offset + i]:
                    return False
            return segments[offset + len(parts) - 1].startswith(parts[-1])

        return aligned(0) or aligned(len(segments) - len(parts))

    def _is_exact_match(self, query: str, item: ItemSuggestion) -> bool:
        query = query.strip().strip("/").lower()
        return query == item.path.lower() or (
            item.slug is not None and query == item.slug.lower()
        )

    def item_search_suggestions(self, req: ItemSearchRequest) -> ItemSuggestions:
        matched = [
            item for item in self._get_item_index() if self._match_item(req.query, item)
        ]
        matched.sort(key=lambda item: not self._is_exact_match(req.query, item))

        return ItemSuggestions(items=matched[: req.limit], total=len(matched))

    def _resolve_item(self, identifier: str) -> Optional[ItemSuggestion]:
        """
        Resolves a slug or a ``repo/line/<num or name>`` path into an indexed item
        """

        identifier = identifier.strip().strip("/")
        index = self._get_item_index()

        for item in index:
            if identifier == item.path or identifier == item.slug:
                return item

        parts = identifier.split("/")
        if len(parts) != 3:
            return None

        repo_name, line_name, item_part = parts
        try:
            num = int(item_part)
        except ValueError:
            return None

        for item in index:
            if item.repo == repo_name and item.line == line_name and item.num == num:
                return item

        return None

    def compare_item_table(self, req: CompareRequest) -> CompareResponse:
        columns = []
        not_found = []
        item_fields = set()

        for identifier in req.items:
            item = self._resolve_item(identifier)
            if item is None:
                not_found.append(identifier)
                continue

            path_spec = item.num if item.num is not None else item.slug
            if path_spec is None:
                not_found.append(identifier)
                continue

            line = self._ws[item.repo][item.line]
            try:
                meta = line.load_obj_meta(path_spec)
            except (ZeroMetaError, MetaIOError, FileNotFoundError):
                not_found.append(identifier)
                continue

            item_fields.update(self._get_item_fields(meta))

            flat = self._prepare_item_dict(meta)
            meta = {key: flat.get(key) for key in ITEM_BASE_FIELDS}
            meta["name"] = item.name
            for key in req.item_fields:
                if key not in meta:
                    meta[key] = flat.get(key)

            columns.append(
                CompareColumn(
                    id=identifier,
                    path=item.path,
                    repo=item.repo,
                    line=item.line,
                    name=item.name,
                    num=item.num,
                    slug=item.slug,
                    meta=meta,
                )
            )

        return CompareResponse(
            columns=columns,
            item_fields=list(sorted(item_fields)),
            not_found=not_found,
        )

    def _file_size_string(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / 1024**2:.1f} MB"
        else:
            return f"{size_bytes / 1024**3:.1f} GB"

    def model(self, path: ModelPathSpec) -> ModelResponse:
        line = self._ws[path.repo][path.line]
        meta = line.load_model_meta(path.num)
        paths = line.load_artifact_paths(path.num)

        files = []
        artifacts = []
        for key in paths:
            for p in paths[key]:
                if os.path.exists(p):
                    size_bytes = os.path.getsize(p)
                    size_str = self._file_size_string(size_bytes)
                    file = File(name=p, size=size_str)
                    if key == "artifacts":
                        artifacts.append(file)
                    else:
                        files.append(file)

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
            artifacts=artifacts,
            files=files,
            git_commit=meta[0].get("git_commit"),
            git_uncommitted_changes=meta[0].get("git_uncommitted_changes"),
        )

    def run_log(self, path: ModelPathSpec) -> LogResponse:
        log_file = os.path.join(
            self._ws_name,
            path.repo,
            path.line,
            f"{path.num:0>5d}",
            "files",
            "cascade_run.log",
        )
        log_text = None
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                log_text = "\n".join(f.readlines())

        return LogResponse(log_text=log_text)

    def run_config(self, path: ModelPathSpec) -> ConfigResponse:
        config_file = os.path.join(
            self._ws_name,
            path.repo,
            path.line,
            f"{path.num:0>5d}",
            "files",
            "cascade_config.json",
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
