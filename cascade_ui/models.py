from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import pydantic


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
    tags: List[str]
    slug: Optional[str] = None
    created_at: Optional[str] = None
    saved_at: str


class LineResponse(Container):
    type: Literal["model_line", "data_line"]
    items: List[Item]
    item_fields: List[str]


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
    cwd: Optional[str]
    python_version: str
    description: Optional[str]
    comments: List[Comment]
    tags: List[str]
    params: Dict[str, Any]
    metrics: List[Metric]
    artifacts: List[str]
    files: List[str]
    git_commit: Optional[str]
    git_uncommitted_changes: Optional[List[str]]


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


class LogResponse(pydantic.BaseModel):
    log_text: Optional[str]


class ConfigResponse(pydantic.BaseModel):
    config: Optional[Dict[str, Any]]
    overrides: Optional[Dict[str, Any]]
