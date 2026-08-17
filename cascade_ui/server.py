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
from typing import Any, Dict, Iterator, List, Optional, Union

from cascade import __version__ as cascade_version
from cascade.base import (
    MetaHandler,
    MetaIOError,
    TraceableOnDisk,
    ZeroMetaError,
    supported_meta_formats,
)
from cascade.base.utils import flatten_dict
from cascade.cli.query import Executor, Field, Query
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
    LineSuggestion,
    LineSuggestions,
    LogResponse,
    ModelPathSpec,
    ModelResponse,
    NavSearchRequest,
    NavSuggestion,
    NavSuggestions,
    PlotPoint,
    PlotRequest,
    PlotResponse,
    PlotSeries,
    QueryRequest,
    QueryResponse,
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

NAV_TYPE_ORDER = {
    "repo": 0,
    "model_line": 1,
    "data_line": 1,
    "model": 2,
    "dataset": 2,
}


def json_safe(value: Any) -> Any:
    """
    Unwraps the ``Field`` objects the query executor returns for nested meta.

    A column that resolves to a dict or to a list of dicts comes back as
    ``Field``, which is not JSON serializable, so every value is unwrapped
    before it leaves the server.
    """

    if isinstance(value, Field):
        return json_safe(value.to_dict())
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


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

    def _read_slug(
        self, repo_name: str, line_name: str, item_name: str
    ) -> Optional[str]:
        slug_path = os.path.join(self._ws_name, repo_name, line_name, item_name, "SLUG")
        try:
            with open(slug_path, "r") as f:
                return f.read().strip() or None
        except OSError:
            return None

    def iterate_over_items(self) -> Iterator[ItemSuggestion]:
        """
        Walks over every model in workspace. Datalines are skipped for now.
        Models without slugs are reported.
        """

        for repo_name in self._ws.get_repo_names():
            repo = self._ws[repo_name]
            for line_name in repo.get_line_names():
                line = repo[line_name]
                if CLS2TYPE.get(type(line)) != "model_line":
                    continue
                for item_name in line.get_item_names():
                    try:
                        num = int(item_name)
                    except ValueError:
                        continue

                    slug = self._read_slug(repo_name, line_name, item_name)
                    if slug is None:
                        warnings.warn(
                            f"No slug found for {repo_name}/{line_name}/{item_name},"
                            " it will be addressed by its path"
                        )

                    yield ItemSuggestion(
                        path="/".join((repo_name, line_name, item_name)),
                        repo=repo_name,
                        line=line_name,
                        name=item_name,
                        num=num,
                        slug=slug,
                    )

    def _get_item_index(self) -> List[ItemSuggestion]:
        index = self._timed_cache.get("item_index")
        if index is None:
            index = list(self.iterate_over_items())
            self._timed_cache.add("item_index", index)
        return index

    def iterate_over_lines(self) -> Iterator[LineSuggestion]:
        """
        Walks over every line in workspace. Datalines are skipped since
        they have nothing to plot. Lines have no slugs, they are addressed
        by their ``repo/line`` path only.
        """

        for repo_name in self._ws.get_repo_names():
            repo = self._ws[repo_name]
            for line_name in repo.get_line_names():
                line = repo[line_name]
                line_type = CLS2TYPE.get(type(line))
                if line_type != "model_line":
                    continue

                yield LineSuggestion(
                    path="/".join((repo_name, line_name)),
                    repo=repo_name,
                    line=line_name,
                    type=line_type,
                    len=len(line),
                )

    def _get_line_index(self) -> List[LineSuggestion]:
        index = self._timed_cache.get("line_index")
        if index is None:
            index = list(self.iterate_over_lines())
            self._timed_cache.add("line_index", index)
        return index

    def _match_path(self, query: str, path: str) -> bool:
        """
        Matches a query against a path segment-wise.

        The query is either head-anchored or tail-anchored: every segment except
        the last one must match a whole path segment, the last one is a prefix.
        This way ``00003`` finds a model named ``00003`` in any line, but does not
        match a line with the same name, and mid-segment queries do not match.
        """

        query = query.strip().strip("/").lower()
        if not query:
            return True

        parts = query.split("/")
        segments = path.lower().split("/")
        if len(parts) > len(segments):
            return False

        def aligned(offset: int) -> bool:
            for i, part in enumerate(parts[:-1]):
                if part != segments[offset + i]:
                    return False
            return segments[offset + len(parts) - 1].startswith(parts[-1])

        return aligned(0) or aligned(len(segments) - len(parts))

    def _match_item(
        self, query: str, item: Union[ItemSuggestion, NavSuggestion]
    ) -> bool:
        """
        Matches a query against an item path, see ``_match_path``.
        Slugs are matched as substrings.
        """

        if item.slug and query.strip().strip("/").lower() in item.slug.lower():
            return True

        return self._match_path(query, item.path)

    def _is_exact_path(self, query: str, path: str) -> bool:
        return query.strip().strip("/").lower() == path.lower()

    def _is_exact_match(
        self, query: str, item: Union[ItemSuggestion, NavSuggestion]
    ) -> bool:
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

    def line_search_suggestions(self, req: ItemSearchRequest) -> LineSuggestions:
        matched = [
            line
            for line in self._get_line_index()
            if self._match_path(req.query, line.path)
        ]
        matched.sort(key=lambda line: not self._is_exact_path(req.query, line.path))

        return LineSuggestions(items=matched[: req.limit], total=len(matched))

    def iterate_over_nav_targets(self) -> Iterator[NavSuggestion]:
        """
        Walks over everything the global search can jump to: repos, lines, models and datasets
        """

        for repo_name in self._ws.get_repo_names():
            repo = self._ws[repo_name]
            yield NavSuggestion(
                type="repo", path=repo_name, repo=repo_name, len=len(repo)
            )

            for line_name in repo.get_line_names():
                line = repo[line_name]
                line_type = CLS2TYPE.get(type(line))
                if line_type is None:
                    continue

                line_path = "/".join((repo_name, line_name))
                yield NavSuggestion(
                    type=line_type,
                    path=line_path,
                    repo=repo_name,
                    line=line_name,
                    len=len(line),
                )

                for item_name in line.get_item_names():
                    item_path = "/".join((line_path, item_name))
                    if line_type == "model_line":
                        try:
                            num = int(item_name)
                        except ValueError:
                            continue

                        yield NavSuggestion(
                            type="model",
                            path=item_path,
                            repo=repo_name,
                            line=line_name,
                            name=item_name,
                            num=num,
                            slug=self._read_slug(repo_name, line_name, item_name),
                        )
                    else:
                        yield NavSuggestion(
                            type="dataset",
                            path=item_path,
                            repo=repo_name,
                            line=line_name,
                            name=item_name,
                        )

    def _get_nav_index(self) -> List[NavSuggestion]:
        index = self._timed_cache.get("nav_index")
        if index is None:
            index = list(self.iterate_over_nav_targets())
            self._timed_cache.add("nav_index", index)
        return index

    def nav_search_suggestions(self, req: NavSearchRequest) -> NavSuggestions:
        kinds = set(req.kinds) if req.kinds else None
        matched = [
            target
            for target in self._get_nav_index()
            if (kinds is None or target.type in kinds)
            and self._match_item(req.query, target)
        ]
        matched.sort(
            key=lambda target: (
                not self._is_exact_match(req.query, target),
                NAV_TYPE_ORDER[target.type],
                target.path,
            )
        )

        return NavSuggestions(items=matched[: req.limit], total=len(matched))

    def _resolve_line(self, identifier: str) -> Optional[LineSuggestion]:
        """
        Resolves a ``repo/line`` path into an indexed line
        """

        identifier = identifier.strip().strip("/")
        for line in self._get_line_index():
            if identifier == line.path:
                return line

        return None

    def _resolve_item(self, identifier: str) -> Optional[ItemSuggestion]:
        """
        Resolves a slug or a ``repo/line/<num or name>`` path into an indexed item
        """

        identifier = identifier.strip().strip("/")
        index = self._get_item_index()

        lowered = identifier.lower()
        for item in index:
            if identifier == item.path or (item.slug and lowered == item.slug.lower()):
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

            line = self._ws[item.repo][item.line]
            try:
                meta = line.load_obj_meta(item.num)
            except (ZeroMetaError, MetaIOError, FileNotFoundError):
                not_found.append(identifier)
                continue

            available_fields = sorted(self._get_item_fields(meta))
            item_fields.update(available_fields)

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
                    available_fields=available_fields,
                )
            )

        return CompareResponse(
            columns=columns,
            item_fields=list(sorted(item_fields)),
            not_found=not_found,
        )

    def plot_line_series(self, req: PlotRequest) -> PlotResponse:
        """
        Reads the requested fields for every item of every requested line.

        The union of plottable fields is collected during the same pass over the
        metas, so that the client can offer a field selector before any field is
        actually chosen.
        """

        series = []
        not_found = []
        all_plot_fields = set()

        for identifier in req.lines:
            suggestion = self._resolve_line(identifier)
            if suggestion is None:
                not_found.append(identifier)
                continue

            line = self._ws[suggestion.repo][suggestion.line]

            points = []
            plot_fields = set()
            for i in range(len(line)):
                try:
                    meta = line.load_obj_meta(i)
                except (ZeroMetaError, MetaIOError, FileNotFoundError):
                    continue

                plot_fields.update(
                    filter(self._filter_plot_fields, self._get_item_fields(meta))
                )

                flat = self._prepare_item_dict(meta)
                points.append(
                    PlotPoint(
                        num=i,
                        slug=meta[0].get("slug"),
                        values={key: flat.get(key) for key in req.fields},
                    )
                )

            all_plot_fields.update(plot_fields)
            series.append(
                PlotSeries(
                    id=identifier,
                    path=suggestion.path,
                    repo=suggestion.repo,
                    line=suggestion.line,
                    points=points,
                    plot_fields=list(sorted(plot_fields)),
                )
            )

        return PlotResponse(
            series=series,
            plot_fields=list(sorted(all_plot_fields)),
            not_found=not_found,
        )

    def query(self, req: QueryRequest) -> QueryResponse:
        """
        Runs a Cascade query against the whole workspace.
        """

        empty = QueryResponse(
            columns=req.columns,
            rows=[],
            has_next=False,
            time_s=0.0,
            workspace_root=self._ws_name,
        )

        if not req.columns:
            empty.error = (
                "Provide at least one column name."
                " Columns are meta fields, for example: created_at"
            )
            return empty

        q = Query(
            columns=req.columns,
            filter_expr=req.filter_expr or None,
            sort_expr=req.sort_expr or None,
            desc=req.desc,
            offset=req.offset,
            limit=req.limit + 1,
        )

        try:
            result = Executor(self._ws_name, "workspace").execute(q)
        except Exception as e:
            empty.error = str(e) or type(e).__name__
            return empty

        has_next = len(result.data) > req.limit
        rows = [
            {key: json_safe(value) for key, value in row.items()}
            for row in result.data[: req.limit]
        ]

        return QueryResponse(
            columns=result.columns,
            rows=rows,
            has_next=has_next,
            time_s=result.time_s,
            workspace_root=self._ws_name,
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
