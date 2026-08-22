export interface PipelineNode {
    id: string;
    name: string;
    label: string;
    meta: Record<string, any>;
}

export interface PipelineEdge {
    id: string;
    source: string;
    target: string;
}

export interface Pipeline {
    nodes: PipelineNode[];
    edges: PipelineEdge[];
}
