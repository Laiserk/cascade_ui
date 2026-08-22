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

from typing import Any, Dict, List, Optional, Tuple

from .models import PipelineEdge, PipelineNode

UNKNOWN_NAME = "Unknown"


def _is_meta(value: Any) -> bool:
    """
    Meta of a single pipeline is a list of dicts
    """
    return isinstance(value, list) and all(isinstance(block, dict) for block in value)


def _is_meta_list(value: Any) -> bool:
    """
    Concatenator, Composer and FunctionModifier store the metas of
    their inputs in the `data` field as a list of metas
    """
    return isinstance(value, list) and len(value) > 0 and all(_is_meta(item) for item in value)


def _label_of(block: Dict[str, Any]) -> str:
    """
    A short name for a step - the class name without the module path,
    ``Wrapper`` of ``cascade.data.dataset.Wrapper``

    Functional steps are all called FunctionDataset or FunctionModifier,
    so for them the name of the wrapped function is used instead
    """
    function = block.get("f")
    if isinstance(function, str) and function:
        return function

    name = block.get("name")
    if not isinstance(name, str) or not name:
        return UNKNOWN_NAME
    return name.split(".")[-1]


class _GraphBuilder:
    def __init__(self) -> None:
        self.nodes: List[PipelineNode] = []
        self.edges: List[PipelineEdge] = []

    def add_node(self, node_id: str, block: Dict[str, Any]) -> None:
        name = block.get("name")
        # The metas of the inputs become nodes of their own,
        # anything else under `data` is left as is
        meta = {
            key: value
            for key, value in block.items()
            if not (key == "data" and _is_meta_list(value))
        }
        self.nodes.append(
            PipelineNode(
                id=node_id,
                name=name if isinstance(name, str) else UNKNOWN_NAME,
                label=_label_of(block),
                meta=meta,
            )
        )

    def add_edge(self, source: str, target: str) -> None:
        self.edges.append(
            PipelineEdge(id=f"{source}->{target}", source=source, target=target)
        )

    def parse_meta(self, meta: List[Any], prefix: str) -> Optional[str]:
        """
        Parses one meta - a chain of pipeline steps where the block at index 0
        is the last step and every next block is the one it takes data from.

        Nested inputs are attached recursively, see ``parse_inputs``

        Returns
        -------
        Optional[str]
            The id of the last step of the chain - the node the parent
            should take data from. None if nothing was parsed
        """

        head = None
        previous = None
        for index, block in enumerate(meta):
            if not isinstance(block, dict):
                # Nothing renderable - the chain ends here
                break

            node_id = f"{prefix}:{index}"
            self.add_node(node_id, block)
            if previous is not None:
                self.add_edge(node_id, previous)
            self.parse_inputs(block.get("data"), node_id, node_id)
            previous = node_id
            if head is None:
                head = node_id
        return head

    def parse_inputs(self, inputs: Any, target: str, prefix: str) -> None:
        """
        Attaches the metas of the datasets a step takes data from -
        this is how Concatenator, Composer and FunctionModifier branch
        """

        if not _is_meta_list(inputs):
            return

        for index, meta in enumerate(inputs):
            source = self.parse_meta(meta, f"{prefix}/{index}")
            if source is not None:
                self.add_edge(source, target)


def build_pipeline_graph(meta: Any) -> Tuple[List[PipelineNode], List[PipelineEdge]]:
    """
    Builds a graph of a data pipeline out of the meta of a dataset

    Every node is a step of the pipeline and every edge points
    from a step to the one that takes its data

    Parameters
    ----------
    meta : Any
        Meta of a dataset as it was saved by a DataLine

    Returns
    -------
    Tuple[List[PipelineNode], List[PipelineEdge]]
        Nodes and edges of the graph
    """

    if not isinstance(meta, list):
        return [], []

    builder = _GraphBuilder()
    builder.parse_meta(meta, "node")
    return builder.nodes, builder.edges
