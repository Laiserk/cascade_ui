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

from cascade.data import ApplyModifier, Concatenator, RangeSampler, Wrapper
from cascade.models import BasicModel
from cascade.workspaces import Workspace
from pytest import fixture


@fixture
def workspace(tmp_path) -> Workspace:
    tmp_path = str(tmp_path)
    ws = Workspace(tmp_path)
    repo = ws.add_repo("repo")
    line = repo.add_line(model_cls=BasicModel)
    model = BasicModel()

    line.save(model)

    return ws


@fixture
def compare_workspace(tmp_path) -> Workspace:
    """
    Two repos with several models each and one data line
    """

    tmp_path = str(tmp_path)
    ws = Workspace(tmp_path)

    first = ws.add_repo("first")
    line = first.add_line(model_cls=BasicModel)
    for lr in (0.1, 0.01):
        model = BasicModel(lr=lr, batch_size=32)
        line.save(model)

    second = ws.add_repo("second")
    line = second.add_line(model_cls=BasicModel)
    model = BasicModel(batch_size=32, momentum=0.9)
    line.save(model)

    data_line = second.add_line(line_type="data")
    data_line.save(Wrapper([0, 1, 2]))

    return ws


@fixture
def pipeline_workspace(tmp_path) -> Workspace:
    """
    One data line with a branching pipeline saved into it

        Wrapper   Wrapper
             \\     /
          Concatenator
               |
          RangeSampler
               |
          ApplyModifier
    """

    tmp_path = str(tmp_path)
    ws = Workspace(tmp_path)

    repo = ws.add_repo("repo")
    data_line = repo.add_line("data", line_type="data")

    concat = Concatenator([Wrapper([0, 1, 2]), Wrapper([3, 4])])
    ds = ApplyModifier(RangeSampler(concat, 0, 4), lambda x: x + 1)
    data_line.save(ds, only_meta=True)

    return ws
