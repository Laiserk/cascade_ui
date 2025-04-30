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

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

sys.path.append(BASE_DIR)
from cascade_ui.server import LinePathSpec, ModelPathSpec, RepoPathSpec, Server


def test_repos(workspace):
    path = workspace.get_root()

    s = Server(path)
    repo = s.repo(RepoPathSpec(repo="repo"))
    assert repo.name == "repo"


def test_lines(workspace):
    path = workspace.get_root()

    s = Server(path)
    line = s.line(LinePathSpec(repo="repo", line="00000"))
    assert line.len == 1
    assert line.name == "00000"


def test_model(workspace):
    path = workspace.get_root()

    s = Server(path)
    model = s.model(ModelPathSpec(repo="repo", line="00000", num=0))
    assert len(model.artifacts) == 0
