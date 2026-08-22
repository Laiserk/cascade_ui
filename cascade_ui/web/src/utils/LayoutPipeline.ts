import dagre from "@dagrejs/dagre";
import type { Edge, Node } from "@vue-flow/core";
import { MarkerType, Position } from "@vue-flow/core";
import type { Pipeline } from "@/models/Pipeline";

export const NODE_WIDTH = 220;
export const NODE_HEIGHT = 64;

export default function LayoutPipeline(pipeline: Pipeline): { nodes: Node[], edges: Edge[] } {
  const graph = new dagre.graphlib.Graph();
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({ rankdir: "TB", nodesep: 40, ranksep: 70, marginx: 20, marginy: 20 });

  for (const node of pipeline.nodes) {
    graph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }
  for (const edge of pipeline.edges) {
    graph.setEdge(edge.source, edge.target);
  }

  dagre.layout(graph);

  const nodes: Node[] = pipeline.nodes.map(node => {
    // Dagre gives the center of a node, Vue Flow expects the top left corner
    const placed = graph.node(node.id);
    return {
      id: node.id,
      type: "step",
      position: {
        x: (placed?.x ?? 0) - NODE_WIDTH / 2,
        y: (placed?.y ?? 0) - NODE_HEIGHT / 2
      },
      data: node,
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top
    };
  });

  const edges: Edge[] = pipeline.edges.map(edge => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: "smoothstep",
    style: { stroke: "#B0AEB3", strokeWidth: 2 },
    markerEnd: MarkerType.ArrowClosed
  }));

  return { nodes, edges };
}
