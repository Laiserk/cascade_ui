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
from cascade.data import dataset, modifier

from cascade_ui.models import DatasetPathSpec
from cascade_ui.pipeline import build_pipeline_graph
from cascade_ui.server import Server


def block(name, **kwargs):
    return dict(name=name, type="dataset", **kwargs)


def names_of(nodes):
    return [node.label for node in nodes]


def edges_of(nodes, edges):
    labels = {node.id: node.label for node in nodes}
    return {(labels[edge.source], labels[edge.target]) for edge in edges}


def test_chain():
    meta = [
        block("cascade.data.apply_modifier.ApplyModifier"),
        block("cascade.data.dataset.Wrapper"),
    ]

    nodes, edges = build_pipeline_graph(meta)

    assert names_of(nodes) == ["ApplyModifier", "Wrapper"]
    assert edges_of(nodes, edges) == {("Wrapper", "ApplyModifier")}


def test_node_keeps_full_name_and_meta():
    meta = [block("cascade.data.dataset.Wrapper", len=3, tags=["raw"])]

    nodes, _ = build_pipeline_graph(meta)

    assert nodes[0].name == "cascade.data.dataset.Wrapper"
    assert nodes[0].label == "Wrapper"
    assert nodes[0].meta["len"] == 3
    assert nodes[0].meta["tags"] == ["raw"]


def test_concatenator_branches():
    meta = [
        block(
            "cascade.data.concatenator.Concatenator",
            num_concatenated=2,
            data=[
                [block("cascade.data.dataset.Wrapper")],
                [
                    block("cascade.data.range_sampler.RangeSampler"),
                    block("cascade.data.folder_dataset.FolderDataset"),
                ],
            ],
        )
    ]

    nodes, edges = build_pipeline_graph(meta)

    assert sorted(names_of(nodes)) == [
        "Concatenator",
        "FolderDataset",
        "RangeSampler",
        "Wrapper",
    ]
    assert edges_of(nodes, edges) == {
        ("Wrapper", "Concatenator"),
        ("RangeSampler", "Concatenator"),
        ("FolderDataset", "RangeSampler"),
    }


def test_branch_meta_does_not_leak_into_node_meta():
    meta = [
        block(
            "cascade.data.concatenator.Concatenator",
            data=[[block("cascade.data.dataset.Wrapper")]],
        )
    ]

    nodes, _ = build_pipeline_graph(meta)

    concat = [node for node in nodes if node.label == "Concatenator"][0]
    assert "data" not in concat.meta


def test_nested_concatenators():
    inner = block(
        "cascade.data.concatenator.Concatenator",
        data=[
            [block("cascade.data.dataset.Wrapper")],
            [block("cascade.data.dataset.IteratorWrapper")],
        ],
    )
    meta = [
        block("cascade.data.apply_modifier.ApplyModifier"),
        block(
            "cascade.data.composer.Composer",
            data=[[inner], [block("cascade.data.folder_dataset.FolderDataset")]],
        ),
    ]

    nodes, edges = build_pipeline_graph(meta)

    assert len(nodes) == 6
    assert edges_of(nodes, edges) == {
        ("Composer", "ApplyModifier"),
        ("Concatenator", "Composer"),
        ("FolderDataset", "Composer"),
        ("Wrapper", "Concatenator"),
        ("IteratorWrapper", "Concatenator"),
    }


def test_same_class_twice_gets_separate_nodes():
    meta = [
        block(
            "cascade.data.concatenator.Concatenator",
            data=[
                [block("cascade.data.dataset.Wrapper")],
                [block("cascade.data.dataset.Wrapper")],
            ],
        )
    ]

    nodes, edges = build_pipeline_graph(meta)

    assert len(nodes) == 3
    assert len({node.id for node in nodes}) == 3
    assert len(edges) == 2


def test_function_modifier_branches():
    meta = [
        block(
            "cascade.data.functions.FunctionModifier",
            f="join",
            data=[
                [block("cascade.data.functions.FunctionDataset", f="load_train")],
                [block("cascade.data.functions.FunctionDataset", f="load_test")],
            ],
        )
    ]

    nodes, edges = build_pipeline_graph(meta)

    assert len(nodes) == 3
    assert len(edges) == 2
    assert all(edge.target == nodes[0].id for edge in edges)


def test_functional_steps_are_labeled_with_the_function_name():
    # Every functional step is called FunctionDataset or FunctionModifier,
    # only `f` tells them apart
    meta = [
        block(
            "cascade.data.functions.FunctionModifier",
            f="add_labels",
            data=[[block("cascade.data.functions.FunctionDataset", f="load_train")]],
        )
    ]

    nodes, _ = build_pipeline_graph(meta)

    assert names_of(nodes) == ["add_labels", "load_train"]
    assert nodes[0].name == "cascade.data.functions.FunctionModifier"


def test_function_pipeline_from_cascade():
    @dataset
    def load(n):
        return list(range(n))

    @modifier
    def add(items, k):
        return [item + k for item in items]

    @modifier
    def join(left, right):
        return list(zip(left, right))

    pipeline = join(add(load(5), 1), load(5))

    nodes, edges = build_pipeline_graph(pipeline.get_meta())

    assert names_of(nodes) == ["join", "add", "load", "load"]
    assert edges_of(nodes, edges) == {
        ("load", "add"),
        ("add", "join"),
        ("load", "join"),
    }


def test_empty_and_broken_meta():
    assert build_pipeline_graph([]) == ([], [])
    assert build_pipeline_graph(None) == ([], [])
    assert build_pipeline_graph({"name": "not a list"}) == ([], [])

    nodes, edges = build_pipeline_graph([block("cascade.data.dataset.Wrapper"), None])
    assert names_of(nodes) == ["Wrapper"]
    assert edges == []

    nodes, _ = build_pipeline_graph([{"type": "dataset"}])
    assert names_of(nodes) == ["Unknown"]


def test_data_field_that_is_not_meta_is_ignored():
    meta = [block("custom.CustomDataset", data=[1, 2, 3])]

    nodes, edges = build_pipeline_graph(meta)

    assert names_of(nodes) == ["CustomDataset"]
    assert edges == []
    assert nodes[0].meta["data"] == [1, 2, 3]


def test_dataset_pipeline_endpoint(pipeline_workspace):
    s = Server(pipeline_workspace.get_root())

    response = s.dataset_pipeline(DatasetPathSpec(repo="repo", line="data", ver="0.1"))

    labels = names_of(response.nodes)
    assert labels[0] == "ApplyModifier"
    assert sorted(labels) == [
        "ApplyModifier",
        "Concatenator",
        "RangeSampler",
        "Wrapper",
        "Wrapper",
    ]
    assert edges_of(response.nodes, response.edges) == {
        ("Wrapper", "Concatenator"),
        ("Concatenator", "RangeSampler"),
        ("RangeSampler", "ApplyModifier"),
    }
    assert len(response.edges) == 4
